from datetime import datetime
from app.extensions import db
from app.models.skill import SkillTaxonomy, UserSkillTag
from app.models.evidence import EvidenceSubmission
from app.models.verification import Verification


def rebuild_user_skill_tags(user_id):
    UserSkillTag.query.filter_by(user_id=user_id).delete()

    published_evidence = EvidenceSubmission.query.filter_by(
        user_id=user_id, is_published=True
    ).all()

    skill_data = {}

    for ev in published_evidence:
        tags = ev.confirmed_skill_tags or ev.ai_extracted_skills or []
        verified = Verification.query.filter_by(
            evidence_id=ev.id, response='confirmed'
        ).count()
        has_verification = verified > 0

        for tag in tags:
            sid = tag.get('skill_id')
            if sid is None:
                continue
            if sid not in skill_data:
                skill_data[sid] = {'evidence_count': 0, 'verified_count': 0, 'confidences': []}
            skill_data[sid]['evidence_count'] += 1
            if has_verification:
                skill_data[sid]['verified_count'] += 1
            skill_data[sid]['confidences'].append(tag.get('confidence', 0.5))

    for skill_id, data in skill_data.items():
        skill = db.session.get(SkillTaxonomy, skill_id)
        if not skill:
            continue
        avg_confidence = sum(data['confidences']) / len(data['confidences']) if data['confidences'] else 0
        strength = min(1.0, avg_confidence * (1 + 0.1 * data['evidence_count']) * (1 + 0.2 * data['verified_count']))

        tag = UserSkillTag(
            user_id=user_id,
            skill_id=skill_id,
            evidence_count=data['evidence_count'],
            verified_evidence_count=data['verified_count'],
            skill_strength=round(strength, 3),
            last_updated=datetime.utcnow(),
        )
        db.session.add(tag)

        skill.usage_count = SkillTaxonomy.usage_count + 1

    db.session.commit()
