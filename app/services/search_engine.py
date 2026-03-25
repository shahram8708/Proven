from sqlalchemy import func, and_
from app.extensions import db
from app.models.user import User
from app.models.evidence import EvidenceSubmission
from app.models.skill import UserSkillTag, SkillTaxonomy
from app.models.challenge import ChallengeSubmission


def build_talent_search_query(filters):
    query = User.query.filter(
        User.account_type == 'talent',
        User.is_email_verified == True,
        User.onboarding_complete == True,
    )

    domain = filters.get('domain')
    if domain:
        query = query.filter(User.primary_domain == domain)

    country = filters.get('country')
    if country:
        query = query.filter(User.location_country.ilike(f'%{country}%'))

    exp_min = filters.get('experience_min')
    if exp_min is not None:
        query = query.filter(User.years_experience >= exp_min)

    exp_max = filters.get('experience_max')
    if exp_max is not None:
        query = query.filter(User.years_experience <= exp_max)

    min_evidence = filters.get('min_evidence_count')
    if min_evidence:
        subq = db.session.query(
            EvidenceSubmission.user_id,
            func.count(EvidenceSubmission.id).label('ev_count')
        ).filter(
            EvidenceSubmission.is_published == True
        ).group_by(EvidenceSubmission.user_id).subquery()
        query = query.join(subq, User.id == subq.c.user_id).filter(subq.c.ev_count >= min_evidence)

    skill_ids = filters.get('skill_ids')
    if skill_ids:
        for sid in skill_ids:
            skill_alias = db.aliased(UserSkillTag)
            query = query.join(skill_alias, User.id == skill_alias.user_id).filter(
                skill_alias.skill_id == sid
            )

    min_ver_rate = filters.get('min_verification_rate')
    if min_ver_rate is not None and min_ver_rate > 0:
        query = query.filter(User.profile_strength >= min_ver_rate * 0.4)

    require_challenge = filters.get('require_challenge')
    if require_challenge:
        challenge_users = db.session.query(ChallengeSubmission.user_id).filter(
            ChallengeSubmission.is_published == True
        ).distinct().subquery()
        query = query.filter(User.id.in_(db.session.query(challenge_users.c.user_id)))

    keyword = filters.get('keyword')
    if keyword:
        kw_pattern = f'%{keyword}%'
        query = query.filter(
            db.or_(
                User.professional_summary.ilike(kw_pattern),
                User.primary_domain.ilike(kw_pattern),
                User.first_name.ilike(kw_pattern),
                User.last_name.ilike(kw_pattern),
            )
        )

    sort_by = filters.get('sort_by', 'relevance')
    if sort_by == 'verification_rate':
        query = query.order_by(User.profile_strength.desc())
    elif sort_by == 'evidence_count':
        query = query.order_by(User.profile_strength.desc())
    elif sort_by == 'recent_activity':
        query = query.order_by(User.last_login.desc().nullslast())
    else:
        query = query.order_by(User.profile_strength.desc())

    page = filters.get('page', 1)
    per_page = filters.get('per_page', 12)
    return query.paginate(page=page, per_page=per_page, error_out=False)
