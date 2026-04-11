from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, abort, flash, redirect, url_for
from flask_login import current_user
from app.extensions import db
from app.decorators import employer_required, premium_required
from app.models.user import User
from app.models.employer import EmployerAccount, TalentList, TalentListMember
from app.models.evidence import EvidenceSubmission
from app.models.skill import UserSkillTag, SkillTaxonomy
from app.models.connection import ContactRequest
from app.models.challenge import ChallengeSubmission
from app.forms.discover_forms import EmployerSearchFilterForm
from app.services.search_engine import build_talent_search_query
from app.services.email_service import send_contact_request_to_talent

discover_bp = Blueprint('discover', __name__)


@discover_bp.route('/discover')
@employer_required
def discover_index():
    form = EmployerSearchFilterForm(request.args)
    domains = ['Technology', 'Marketing', 'Finance', 'Design', 'Operations', 'Research', 'Legal', 'Healthcare', 'Education']
    skills = SkillTaxonomy.query.filter_by(is_active=True).order_by(SkillTaxonomy.usage_count.desc()).limit(50).all()
    employer = EmployerAccount.query.filter_by(owner_user_id=current_user.id).first()
    lists = TalentList.query.filter_by(employer_account_id=employer.id).all() if employer else []

    filters = {
        'domain': request.args.get('domain', ''),
        'keyword': request.args.get('keyword', ''),
        'skills': request.args.get('skills', ''),
        'min_evidence_count': request.args.get('min_evidence_count', 0, type=int),
        'min_verification_rate': request.args.get('min_verification_rate', 0, type=int),
        'require_challenge': request.args.get('require_challenge') == 'on',
        'country': request.args.get('country', ''),
        'region': request.args.get('region', ''),
        'experience_min': request.args.get('experience_min', type=int),
        'experience_max': request.args.get('experience_max', type=int),
        'experience_level': request.args.get('experience_level', ''),
        'sort_by': request.args.get('sort_by', 'relevance'),
        'page': request.args.get('page', 1, type=int),
        'per_page': 12,
    }
    results = build_talent_search_query(filters)

    talents = getattr(results, 'items', results)
    pagination = results if hasattr(results, 'pages') else None
    pagination_params = {k: v for k, v in filters.items() if k not in ['page', 'per_page'] and v not in [None, '']}

    return render_template(
        'discover/index.html',
        form=form,
        results=results,
        talents=talents,
        pagination=pagination,
        pagination_params=pagination_params,
        filters=filters,
        domains=domains,
        skills=skills,
        talent_lists=lists,
    )


@discover_bp.route('/discover/search', methods=['POST'])
@employer_required
def discover_search():
    data = request.get_json(silent=True) or {}
    filters = {
        'domain': data.get('domain', ''),
        'keyword': data.get('keyword', ''),
        'skills': data.get('skills', ''),
        'min_evidence_count': data.get('min_evidence_count', 0),
        'skill_ids': data.get('skill_ids', []),
        'min_verification_rate': data.get('min_verification_rate', 0),
        'require_challenge': data.get('require_challenge', False),
        'country': data.get('country', ''),
        'region': data.get('region', ''),
        'experience_min': data.get('experience_min'),
        'experience_max': data.get('experience_max'),
        'experience_level': data.get('experience_level', ''),
        'sort_by': data.get('sort_by', 'relevance'),
        'page': data.get('page', 1),
        'per_page': 12,
    }
    results = build_talent_search_query(filters)
    talents = []
    for u in results.items:
        ev_count = EvidenceSubmission.query.filter_by(user_id=u.id, is_published=True).count()
        ch_count = ChallengeSubmission.query.filter_by(user_id=u.id, is_published=True).count()
        top_skills = UserSkillTag.query.filter_by(user_id=u.id).order_by(UserSkillTag.skill_strength.desc()).limit(3).all()
        talents.append({
            'id': u.id,
            'full_name': u.full_name,
            'username': u.username,
            'primary_domain': u.primary_domain,
            'location_country': u.location_country,
            'profile_strength': u.profile_strength,
            'evidence_count': ev_count,
            'challenge_count': ch_count,
            'professional_summary': (u.professional_summary or '')[:150],
            'top_skills': [{'name': ts.skill.name, 'strength': ts.skill_strength} for ts in top_skills if ts.skill],
            'profile_photo_url': u.profile_photo_url,
        })
    return jsonify({
        'talents': talents,
        'total': results.total,
        'pages': results.pages,
        'current_page': results.page,
    })


@discover_bp.route('/discover/profile/<int:user_id>')
@employer_required
def profile_preview(user_id):
    user = User.query.get_or_404(user_id)
    if user.account_type != 'talent':
        abort(404)

    evidence = EvidenceSubmission.query.filter_by(
        user_id=user_id, is_published=True
    ).order_by(EvidenceSubmission.quality_score.desc()).limit(3).all()

    skills = UserSkillTag.query.filter_by(user_id=user_id).order_by(
        UserSkillTag.skill_strength.desc()
    ).limit(5).all()

    employer = EmployerAccount.query.filter_by(owner_user_id=current_user.id).first()
    if employer:
        employer.total_profiles_viewed = (employer.total_profiles_viewed or 0) + 1
        db.session.commit()

    return jsonify({
        'id': user.id,
        'full_name': user.full_name,
        'username': user.username,
        'primary_domain': user.primary_domain,
        'location': f"{user.location_city or ''}, {user.location_country or ''}".strip(', '),
        'professional_summary': user.professional_summary,
        'profile_strength': user.profile_strength,
        'profile_photo_url': user.profile_photo_url,
        'open_to_opportunities': user.open_to_opportunities,
        'evidence': [{
            'id': e.id,
            'title': e.title,
            'evidence_type': e.evidence_type,
            'quality_score': e.quality_score,
            'verification_count': e.verification_count,
        } for e in evidence],
        'skills': [{
            'name': s.skill.name if s.skill else '',
            'dimension': s.skill.dimension if s.skill else '',
            'strength': s.skill_strength,
            'evidence_count': s.evidence_count,
        } for s in skills],
    })


@discover_bp.route('/discover/contact/<int:user_id>', methods=['POST'])
@employer_required
@premium_required
def request_contact(user_id):
    user = User.query.get_or_404(user_id)
    if user.account_type != 'talent':
        abort(404)

    employer = EmployerAccount.query.filter_by(owner_user_id=current_user.id).first()
    if employer and employer.monthly_contact_credits <= 0:
        return jsonify({'error': 'No contact credits remaining.'}), 403

    existing = ContactRequest.query.filter_by(
        employer_user_id=current_user.id,
        talent_user_id=user_id,
    ).first()
    if existing:
        return jsonify({'error': 'Contact request already sent.'}), 400

    data = request.get_json(silent=True) or {}
    cr = ContactRequest(
        employer_user_id=current_user.id,
        talent_user_id=user_id,
        message=data.get('message', ''),
    )
    db.session.add(cr)

    if employer:
        employer.monthly_contact_credits = max(0, employer.monthly_contact_credits - 1)

        # Keep discover lists useful by attaching contacted talent to a list.
        target_list = TalentList.query.filter_by(
            employer_account_id=employer.id
        ).order_by(TalentList.created_at.asc()).first()
        if not target_list:
            target_list = TalentList(employer_account_id=employer.id, name='Contacted')
            db.session.add(target_list)
            db.session.flush()

        membership = TalentListMember.query.filter_by(
            list_id=target_list.id,
            talent_user_id=user_id,
        ).first()
        if not membership:
            membership = TalentListMember(
                list_id=target_list.id,
                talent_user_id=user_id,
                pipeline_stage='contacted',
            )
            db.session.add(membership)
        else:
            membership.pipeline_stage = 'contacted'

    db.session.commit()

    company_name = employer.company_name if employer else current_user.full_name
    send_contact_request_to_talent(cr, company_name)

    return jsonify({'success': True, 'message': 'Contact request sent.'})


@discover_bp.route('/discover/lists', methods=['GET', 'POST'])
@employer_required
def talent_lists():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('List name is required.', 'warning')
            return redirect(url_for('discover.talent_lists'))

        employer = EmployerAccount.query.filter_by(owner_user_id=current_user.id).first()
        if not employer:
            abort(403)

        tl = TalentList(employer_account_id=employer.id, name=name)
        db.session.add(tl)
        db.session.commit()
        flash('List created.', 'success')
        return redirect(url_for('discover.talent_lists'))

    employer = EmployerAccount.query.filter_by(owner_user_id=current_user.id).first()
    lists = TalentList.query.filter_by(employer_account_id=employer.id).all() if employer else []
    return render_template('discover/lists.html', talent_lists=lists)


@discover_bp.route('/discover/lists/new', methods=['POST'])
@employer_required
def create_list():
    data = request.get_json(silent=True) or request.form
    name = data.get('name', '').strip()
    if not name:
        flash('List name is required.', 'warning')
        return redirect(url_for('discover.talent_lists'))

    employer = EmployerAccount.query.filter_by(owner_user_id=current_user.id).first()
    if not employer:
        abort(403)

    tl = TalentList(employer_account_id=employer.id, name=name)
    db.session.add(tl)
    db.session.commit()

    if request.is_json:
        return jsonify({'id': tl.id, 'name': tl.name})
    flash('List created.', 'success')
    return redirect(url_for('discover.talent_lists'))


@discover_bp.route('/discover/lists/<int:id>')
@employer_required
def list_detail(id):
    tl = TalentList.query.get_or_404(id)
    employer = EmployerAccount.query.filter_by(owner_user_id=current_user.id).first()
    if not employer or tl.employer_account_id != employer.id:
        abort(403)
    members = TalentListMember.query.filter_by(list_id=id).all()
    return render_template('discover/lists.html', talent_lists=[tl], members=members, current_list=tl)


@discover_bp.route('/discover/lists/<int:id>/add', methods=['POST'])
@employer_required
def add_to_list(id):
    tl = TalentList.query.get_or_404(id)
    employer = EmployerAccount.query.filter_by(owner_user_id=current_user.id).first()
    if not employer or tl.employer_account_id != employer.id:
        abort(403)

    data = request.get_json(silent=True) or {}
    talent_user_id = data.get('talent_user_id')
    if not talent_user_id:
        return jsonify({'error': 'talent_user_id required'}), 400

    existing = TalentListMember.query.filter_by(list_id=id, talent_user_id=talent_user_id).first()
    if existing:
        return jsonify({'error': 'Already in list'}), 400

    member = TalentListMember(list_id=id, talent_user_id=talent_user_id)
    db.session.add(member)
    db.session.commit()
    return jsonify({'success': True})


@discover_bp.route('/discover/lists/member/<int:id>/stage', methods=['POST'])
@employer_required
def update_pipeline_stage(id):
    member = TalentListMember.query.get_or_404(id)
    tl = TalentList.query.get(member.list_id)
    employer = EmployerAccount.query.filter_by(owner_user_id=current_user.id).first()
    if not employer or tl.employer_account_id != employer.id:
        abort(403)

    data = request.get_json(silent=True) or {}
    stage = data.get('stage', 'shortlisted')
    valid_stages = [
        'discovered', 'reviewing', 'shortlisted', 'contacted',
        'interviewing', 'offer', 'offered', 'hired', 'declined'
    ]
    if stage not in valid_stages:
        return jsonify({'error': 'Invalid stage'}), 400

    if stage == 'offered':
        stage = 'offer'

    member.pipeline_stage = stage
    db.session.commit()
    return jsonify({'success': True, 'stage': stage})


@discover_bp.route('/discover/notes/<int:user_id>', methods=['POST'])
@employer_required
def save_employer_note(user_id):
    data = request.get_json(silent=True) or {}
    note_text = data.get('notes', '')

    employer = EmployerAccount.query.filter_by(owner_user_id=current_user.id).first()
    if not employer:
        abort(403)

    members = TalentListMember.query.join(TalentList).filter(
        TalentList.employer_account_id == employer.id,
        TalentListMember.talent_user_id == user_id,
    ).all()

    if members:
        for m in members:
            m.employer_notes = note_text
    else:
        default_list = TalentList.query.filter_by(employer_account_id=employer.id).first()
        if not default_list:
            default_list = TalentList(employer_account_id=employer.id, name='Default')
            db.session.add(default_list)
            db.session.flush()
        member = TalentListMember(
            list_id=default_list.id,
            talent_user_id=user_id,
            employer_notes=note_text,
        )
        db.session.add(member)

    db.session.commit()
    return jsonify({'success': True})
