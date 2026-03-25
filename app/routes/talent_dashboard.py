from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.decorators import talent_required
from app.models.evidence import EvidenceSubmission
from app.models.verification import Verification
from app.models.challenge import ChallengeSubmission
from app.models.skill import UserSkillTag
from app.services.profile_strength import compute_profile_strength
from app.extensions import db

talent_dashboard_bp = Blueprint('talent_dashboard', __name__)


@talent_dashboard_bp.route('/dashboard')
@talent_required
def talent_dashboard():
    strength = compute_profile_strength(current_user)
    current_user.profile_strength = strength
    db.session.commit()

    published = EvidenceSubmission.query.filter_by(
        user_id=current_user.id, is_published=True
    ).order_by(EvidenceSubmission.submitted_at.desc()).all()

    drafts = EvidenceSubmission.query.filter_by(
        user_id=current_user.id, is_draft=True
    ).order_by(EvidenceSubmission.created_at.desc()).all()

    pending_verifications = Verification.query.join(EvidenceSubmission).filter(
        EvidenceSubmission.user_id == current_user.id,
        Verification.response == 'pending'
    ).count()

    confirmed_verifications = Verification.query.join(EvidenceSubmission).filter(
        EvidenceSubmission.user_id == current_user.id,
        Verification.response.in_(['confirmed', 'confirmed_with_qualification'])
    ).count()

    challenge_count = ChallengeSubmission.query.filter_by(user_id=current_user.id).count()
    skill_count = UserSkillTag.query.filter_by(user_id=current_user.id).count()

    return render_template(
        'talent/dashboard.html',
        profile_strength=strength,
        published_evidence=published,
        drafts=drafts,
        pending_verifications=pending_verifications,
        confirmed_verifications=confirmed_verifications,
        challenge_count=challenge_count,
        skill_count=skill_count,
    )
