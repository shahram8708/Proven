from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.extensions import db, limiter
from app.decorators import talent_required
from app.models.evidence import EvidenceSubmission, EvidenceFile
from app.models.skill import SkillTaxonomy
from app.forms.evidence_forms import EvidenceForm
from app.services.ai_skill_extractor import extract_skills_from_evidence
from app.services.evidence_quality_scorer import compute_quality_score
from app.services.fraud_detector import run_fraud_detection
from app.services.skill_aggregator import rebuild_user_skill_tags
from app.services.file_handler import upload_to_s3

evidence_bp = Blueprint('evidence', __name__)


@evidence_bp.route('/evidence/new', methods=['GET', 'POST'])
@talent_required
@limiter.limit("10/day")
def new_evidence():
    form = EvidenceForm()
    if form.validate_on_submit():
        evidence = EvidenceSubmission(
            user_id=current_user.id,
            title=form.title.data.strip(),
            evidence_type=form.evidence_type.data,
            domain_tag=form.domain_tag.data.strip() if form.domain_tag.data else None,
            team_size_range=form.team_size_range.data or None,
            project_scale=form.project_scale.data or None,
            situation_text=form.situation_text.data.strip(),
            approach_text=form.approach_text.data.strip(),
            decisions_text=form.decisions_text.data.strip(),
            outcome_text=form.outcome_text.data.strip(),
            skills_text=form.skills_text.data.strip(),
            reflection_text=form.reflection_text.data.strip(),
            is_draft=True,
            is_published=False,
            submitted_at=datetime.utcnow(),
        )
        db.session.add(evidence)
        db.session.flush()

        files = request.files.getlist('evidence_files')
        for f in files[:5]:
            if f and f.filename:
                result, error = upload_to_s3(f, current_user.id, evidence.id)
                if result:
                    ef = EvidenceFile(
                        evidence_id=evidence.id,
                        original_filename=result['original_filename'],
                        storage_path=result['storage_path'],
                        file_type=result['file_type'],
                        file_size_bytes=result.get('file_size_bytes', 0),
                    )
                    db.session.add(ef)

        taxonomy = SkillTaxonomy.query.filter_by(is_active=True).all()
        extracted = extract_skills_from_evidence(evidence, taxonomy)
        evidence.ai_extracted_skills = extracted

        db.session.commit()
        return redirect(url_for('evidence.skills_review', id=evidence.id))

    return render_template('evidence/new.html', form=form)


@evidence_bp.route('/evidence/<int:id>/skills', methods=['GET', 'POST'])
@talent_required
def skills_review(id):
    evidence = EvidenceSubmission.query.get_or_404(id)
    if evidence.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        confirmed_ids = request.form.getlist('confirmed_skills')
        confirmed_tags = []
        for skill_data in (evidence.ai_extracted_skills or []):
            if str(skill_data.get('skill_id')) in confirmed_ids:
                confirmed_tags.append(skill_data)
        evidence.confirmed_skill_tags = confirmed_tags
        evidence.is_draft = False
        evidence.is_published = True

        fraud = run_fraud_detection(evidence, current_user)
        evidence.fraud_flag_level = fraud['flag_level']

        score = compute_quality_score(evidence)
        evidence.quality_score = score

        db.session.commit()
        rebuild_user_skill_tags(current_user.id)

        flash('Evidence published successfully!', 'success')
        return redirect(url_for('evidence.evidence_detail', id=evidence.id))

    return render_template('evidence/skills_review.html', evidence=evidence)


@evidence_bp.route('/evidence/<int:id>')
@login_required
def evidence_detail(id):
    evidence = EvidenceSubmission.query.get_or_404(id)
    if evidence.user_id != current_user.id and not current_user.is_admin and not evidence.is_published:
        abort(403)
    return render_template('evidence/detail.html', evidence=evidence)


@evidence_bp.route('/evidence/<int:id>/edit', methods=['GET', 'POST'])
@talent_required
def evidence_edit(id):
    evidence = EvidenceSubmission.query.get_or_404(id)
    if evidence.user_id != current_user.id:
        abort(403)

    form = EvidenceForm(obj=evidence)
    if form.validate_on_submit():
        evidence.title = form.title.data.strip()
        evidence.evidence_type = form.evidence_type.data
        evidence.domain_tag = form.domain_tag.data.strip() if form.domain_tag.data else None
        evidence.team_size_range = form.team_size_range.data or None
        evidence.project_scale = form.project_scale.data or None
        evidence.situation_text = form.situation_text.data.strip()
        evidence.approach_text = form.approach_text.data.strip()
        evidence.decisions_text = form.decisions_text.data.strip()
        evidence.outcome_text = form.outcome_text.data.strip()
        evidence.skills_text = form.skills_text.data.strip()
        evidence.reflection_text = form.reflection_text.data.strip()

        taxonomy = SkillTaxonomy.query.filter_by(is_active=True).all()
        extracted = extract_skills_from_evidence(evidence, taxonomy)
        evidence.ai_extracted_skills = extracted

        score = compute_quality_score(evidence)
        evidence.quality_score = score

        db.session.commit()
        rebuild_user_skill_tags(current_user.id)

        flash('Evidence updated successfully.', 'success')
        return redirect(url_for('evidence.evidence_detail', id=evidence.id))

    return render_template('evidence/edit.html', form=form, evidence=evidence)


@evidence_bp.route('/evidence/<int:id>/publish', methods=['POST'])
@talent_required
def publish_evidence(id):
    evidence = EvidenceSubmission.query.get_or_404(id)
    if evidence.user_id != current_user.id:
        abort(403)

    fraud = run_fraud_detection(evidence, current_user)
    evidence.fraud_flag_level = fraud['flag_level']

    if fraud['action'] == 'hold':
        flash('This evidence has been flagged for review. It cannot be published at this time.', 'danger')
        return redirect(url_for('evidence.evidence_detail', id=evidence.id))

    evidence.is_published = True
    evidence.is_draft = False
    evidence.submitted_at = datetime.utcnow()

    score = compute_quality_score(evidence)
    evidence.quality_score = score

    db.session.commit()
    rebuild_user_skill_tags(current_user.id)

    flash('Evidence published!', 'success')
    return redirect(url_for('evidence.evidence_detail', id=evidence.id))


@evidence_bp.route('/evidence/<int:id>/unpublish', methods=['POST'])
@talent_required
def unpublish_evidence(id):
    evidence = EvidenceSubmission.query.get_or_404(id)
    if evidence.user_id != current_user.id:
        abort(403)
    evidence.is_published = False
    db.session.commit()
    rebuild_user_skill_tags(current_user.id)
    flash('Evidence unpublished.', 'info')
    return redirect(url_for('evidence.evidence_detail', id=evidence.id))


@evidence_bp.route('/evidence/<int:id>/delete', methods=['POST'])
@talent_required
def delete_evidence(id):
    evidence = EvidenceSubmission.query.get_or_404(id)
    if evidence.user_id != current_user.id:
        abort(403)
    evidence.is_published = False
    evidence.is_draft = True
    db.session.commit()
    rebuild_user_skill_tags(current_user.id)
    flash('Evidence removed.', 'info')
    return redirect(url_for('talent_dashboard.talent_dashboard'))


@evidence_bp.route('/evidence/save-draft', methods=['POST'])
@talent_required
def save_draft():
    data = request.get_json(silent=True) or {}
    evidence_id = data.get('evidence_id')

    if evidence_id:
        evidence = EvidenceSubmission.query.get(evidence_id)
        if not evidence or evidence.user_id != current_user.id:
            return jsonify({'error': 'Not found'}), 404
    else:
        evidence = EvidenceSubmission(
            user_id=current_user.id,
            title=data.get('title', 'Untitled Draft'),
            evidence_type=data.get('evidence_type', 'project_delivery'),
            situation_text=data.get('situation_text', ''),
            approach_text=data.get('approach_text', ''),
            decisions_text=data.get('decisions_text', ''),
            outcome_text=data.get('outcome_text', ''),
            skills_text=data.get('skills_text', ''),
            reflection_text=data.get('reflection_text', ''),
            is_draft=True,
        )
        db.session.add(evidence)

    for field in ['title', 'evidence_type', 'situation_text', 'approach_text',
                  'decisions_text', 'outcome_text', 'skills_text', 'reflection_text',
                  'domain_tag', 'team_size_range', 'project_scale']:
        if field in data:
            setattr(evidence, field, data[field])

    db.session.commit()
    return jsonify({'evidence_id': evidence.id, 'status': 'saved'})
