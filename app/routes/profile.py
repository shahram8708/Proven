from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.evidence import EvidenceSubmission
from app.models.skill import UserSkillTag, SkillTaxonomy
from app.models.challenge import ChallengeSubmission
from app.models.verification import Verification
from app.forms.profile_forms import ProfileEditForm

profile_bp = Blueprint('profile', __name__)


def compute_capability_radar_data(user_id):
    dimensions = ['technical', 'process', 'communication', 'leadership', 'problem_solving']
    verified = []
    unverified = []
    for dim in dimensions:
        tags = UserSkillTag.query.join(SkillTaxonomy).filter(
            UserSkillTag.user_id == user_id,
            SkillTaxonomy.dimension == dim
        ).all()
        if tags:
            max_strength = max(t.skill_strength for t in tags)
            verified_strength = max(
                (t.verified_evidence_count / max(t.evidence_count, 1)) * t.skill_strength
                for t in tags
            )
            verified.append(round(verified_strength * 100, 1))
            unverified.append(round(max_strength * 100, 1))
        else:
            verified.append(0)
            unverified.append(0)
    return {'verified': verified, 'unverified': unverified}


@profile_bp.route('/profile/<username>')
def public_profile(username):
    user = User.query.filter_by(username=username.lower()).first_or_404()
    if user.account_type != 'talent':
        abort(404)

    evidence = EvidenceSubmission.query.filter_by(
        user_id=user.id, is_published=True
    ).order_by(EvidenceSubmission.submitted_at.desc()).all()

    skills = UserSkillTag.query.filter_by(user_id=user.id).order_by(
        UserSkillTag.skill_strength.desc()
    ).all()

    challenges = ChallengeSubmission.query.filter_by(
        user_id=user.id, is_published=True
    ).all()

    total_verifications = sum(e.verification_count or 0 for e in evidence)
    total_evidence = len(evidence)
    verification_rate = (total_verifications / max(total_evidence, 1)) * 100

    capability_data = compute_capability_radar_data(user.id)
    radar_data = {
        'labels': ['Technical', 'Process', 'Communication', 'Leadership', 'Problem Solving'],
        'data': capability_data['verified'],
    }

    skills_by_dimension = {}
    for s in skills:
        dim = s.skill.dimension if s.skill else 'other'
        skills_by_dimension.setdefault(dim, []).append(s)

    return render_template(
        'profile/public.html',
        user=user,
        evidence_items=evidence,
        skills=skills,
        skills_by_dimension=skills_by_dimension,
        challenge_submissions=challenges,
        verification_rate=round(verification_rate, 1),
        radar_data=radar_data,
    )


@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileEditForm(obj=current_user)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data.strip()
        current_user.last_name = form.last_name.data.strip()
        current_user.professional_summary = form.professional_summary.data.strip() if form.professional_summary.data else None
        current_user.primary_domain = form.primary_domain.data or None
        current_user.location_city = form.location_city.data.strip() if form.location_city.data else None
        current_user.location_country = form.location_country.data.strip() if form.location_country.data else None
        current_user.open_to_opportunities = form.open_to_opportunities.data
        current_user.opportunity_type = form.opportunity_type.data or None
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile.public_profile', username=current_user.username))
    return render_template('profile/edit.html', form=form)
