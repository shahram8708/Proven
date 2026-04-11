from sqlalchemy import func, and_, or_
from sqlalchemy.orm import aliased
from app.extensions import db
from app.models.user import User
from app.models.evidence import EvidenceSubmission
from app.models.skill import UserSkillTag, SkillTaxonomy
from app.models.challenge import ChallengeSubmission


def build_talent_search_query(filters):
    query = User.query.filter(
        User.account_type == 'talent',
        User.is_admin == False,
    )

    domain = filters.get('domain')
    if domain:
        query = query.filter(User.primary_domain == domain)

    country = filters.get('country')
    if country:
        query = query.filter(User.location_country.ilike(f'%{country}%'))

    region = filters.get('region')
    if region:
        region_pattern = f'%{region}%'
        query = query.filter(
            or_(
                User.location_city.ilike(region_pattern),
                User.location_country.ilike(region_pattern),
            )
        )

    exp_min = filters.get('experience_min')
    if exp_min is not None:
        query = query.filter(User.years_experience >= exp_min)

    exp_max = filters.get('experience_max')
    if exp_max is not None:
        query = query.filter(User.years_experience <= exp_max)

    experience_level = filters.get('experience_level')
    if experience_level == 'junior':
        query = query.filter(func.coalesce(User.years_experience, 0) <= 2)
    elif experience_level == 'mid':
        query = query.filter(User.years_experience.between(3, 5))
    elif experience_level == 'senior':
        query = query.filter(User.years_experience.between(6, 9))
    elif experience_level == 'lead':
        query = query.filter(func.coalesce(User.years_experience, 0) >= 10)

    min_evidence = filters.get('min_evidence_count')
    evidence_subq = db.session.query(
        EvidenceSubmission.user_id.label('user_id'),
        func.count(EvidenceSubmission.id).label('ev_count')
    ).filter(
        EvidenceSubmission.is_published == True
    ).group_by(EvidenceSubmission.user_id).subquery()

    if min_evidence:
        query = query.join(evidence_subq, User.id == evidence_subq.c.user_id).filter(evidence_subq.c.ev_count >= min_evidence)

    skill_ids = filters.get('skill_ids')
    if skill_ids:
        for sid in skill_ids:
            skill_alias = aliased(UserSkillTag)
            query = query.join(skill_alias, User.id == skill_alias.user_id).filter(
                skill_alias.skill_id == sid
            )

    skills = filters.get('skills', '')
    if skills:
        skill_terms = [s.strip() for s in skills.split(',') if s.strip()]
        for term in skill_terms:
            term_users_subq = db.session.query(UserSkillTag.user_id).join(
                SkillTaxonomy, UserSkillTag.skill_id == SkillTaxonomy.id
            ).filter(
                SkillTaxonomy.name.ilike(f'%{term}%')
            ).subquery()
            query = query.filter(User.id.in_(db.session.query(term_users_subq.c.user_id)))

    min_ver_rate = filters.get('min_verification_rate')
    if min_ver_rate is not None and min_ver_rate > 0:
        query = query.filter(func.coalesce(User.profile_strength, 0) >= min_ver_rate)

    require_challenge = filters.get('require_challenge')
    if require_challenge:
        challenge_users = db.session.query(ChallengeSubmission.user_id).filter(
            ChallengeSubmission.is_published == True
        ).distinct().subquery()
        query = query.filter(User.id.in_(db.session.query(challenge_users.c.user_id)))

    keyword = filters.get('keyword')
    if keyword:
        kw_pattern = f'%{keyword}%'
        query = query.outerjoin(UserSkillTag, User.id == UserSkillTag.user_id).outerjoin(
            SkillTaxonomy, UserSkillTag.skill_id == SkillTaxonomy.id
        )
        query = query.filter(
            or_(
                User.professional_summary.ilike(kw_pattern),
                User.primary_domain.ilike(kw_pattern),
                User.first_name.ilike(kw_pattern),
                User.last_name.ilike(kw_pattern),
                User.username.ilike(kw_pattern),
                User.location_city.ilike(kw_pattern),
                User.location_country.ilike(kw_pattern),
                SkillTaxonomy.name.ilike(kw_pattern),
            )
        ).distinct()

    sort_by = filters.get('sort_by', 'relevance')
    if sort_by == 'verification_rate':
        query = query.order_by(func.coalesce(User.profile_strength, 0).desc())
    elif sort_by == 'evidence_count':
        query = query.outerjoin(evidence_subq, User.id == evidence_subq.c.user_id).order_by(
            func.coalesce(evidence_subq.c.ev_count, 0).desc(),
            func.coalesce(User.profile_strength, 0).desc(),
        )
    elif sort_by == 'recent_activity':
        query = query.order_by(User.last_login.desc().nullslast())
    else:
        query = query.order_by(func.coalesce(User.profile_strength, 0).desc(), User.last_login.desc().nullslast())

    page = filters.get('page', 1)
    per_page = filters.get('per_page', 12)
    return query.paginate(page=page, per_page=per_page, error_out=False)
