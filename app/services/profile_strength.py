from app.models.evidence import EvidenceSubmission
from app.models.challenge import ChallengeSubmission
from app.models.skill import UserSkillTag
from app.extensions import db


def compute_profile_strength(user):
    score = 0.0

    evidence_count = EvidenceSubmission.query.filter_by(
        user_id=user.id, is_published=True
    ).count()
    score += min(30, evidence_count * 6)

    verified_evidence = EvidenceSubmission.query.filter(
        EvidenceSubmission.user_id == user.id,
        EvidenceSubmission.is_published == True,
        EvidenceSubmission.verification_count >= 1
    ).count()
    total_evidence = max(1, evidence_count)
    verification_rate = verified_evidence / total_evidence
    score += verification_rate * 40

    challenge_count = ChallengeSubmission.query.filter_by(
        user_id=user.id, is_published=True
    ).count()
    score += min(15, challenge_count * 5)

    if user.profile_photo_url:
        score += 3
    if user.professional_summary and len(user.professional_summary) > 200:
        score += 5
    if user.primary_domain:
        score += 2
    skill_count = UserSkillTag.query.filter_by(user_id=user.id).count()
    if skill_count >= 5:
        score += 5

    return round(min(100.0, score), 1)
