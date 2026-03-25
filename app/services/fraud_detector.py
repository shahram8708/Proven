import os
import re
import json
import logging
from datetime import datetime, timedelta
from collections import Counter

logger = logging.getLogger(__name__)


def run_fraud_detection(evidence, user):
    reasons = []
    flags = []

    plagiarism = _plagiarism_check(evidence, user)
    if plagiarism:
        flags.append(plagiarism['level'])
        reasons.append(plagiarism['reason'])

    velocity = _velocity_check(user)
    if velocity:
        flags.append(velocity['level'])
        reasons.append(velocity['reason'])

    consistency = _ai_consistency_check(evidence)
    if consistency:
        flags.append(consistency['level'])
        reasons.append(consistency['reason'])

    verifier_rel = _verifier_relationship_check(evidence, user)
    if verifier_rel:
        flags.append(verifier_rel['level'])
        reasons.append(verifier_rel['reason'])

    network = _network_analysis(evidence)
    if network:
        flags.append(network['level'])
        reasons.append(network['reason'])

    level_priority = {'high': 3, 'medium': 2, 'low': 1}
    if not flags:
        final_level = 'clean'
    else:
        final_level = max(flags, key=lambda x: level_priority.get(x, 0))

    action_map = {'clean': 'approve', 'low': 'approve', 'medium': 'review', 'high': 'hold'}
    action = action_map.get(final_level, 'review')

    return {
        'flag_level': final_level,
        'reasons': reasons,
        'action': action,
    }


def _plagiarism_check(evidence, user):
    from app.models.evidence import EvidenceSubmission

    combined = ' '.join([
        evidence.situation_text or '',
        evidence.approach_text or '',
        evidence.outcome_text or '',
    ]).lower()

    if len(combined) < 100:
        return None

    def _char_ngrams(text, n=4):
        return set(text[i:i+n] for i in range(len(text) - n + 1))

    evidence_ngrams = _char_ngrams(combined)
    if not evidence_ngrams:
        return None

    other_submissions = EvidenceSubmission.query.filter(
        EvidenceSubmission.user_id != user.id,
        EvidenceSubmission.is_published == True
    ).limit(200).all()

    for other in other_submissions:
        other_combined = ' '.join([
            other.situation_text or '',
            other.approach_text or '',
            other.outcome_text or '',
        ]).lower()
        other_ngrams = _char_ngrams(other_combined)
        if not other_ngrams:
            continue
        intersection = evidence_ngrams & other_ngrams
        union = evidence_ngrams | other_ngrams
        similarity = len(intersection) / len(union) if union else 0
        if similarity > 0.7:
            return {'level': 'high', 'reason': f'High text similarity ({similarity:.0%}) with existing submission #{other.id}.'}

    return None


def _velocity_check(user):
    from app.models.evidence import EvidenceSubmission
    day_ago = datetime.utcnow() - timedelta(hours=24)
    recent_count = EvidenceSubmission.query.filter(
        EvidenceSubmission.user_id == user.id,
        EvidenceSubmission.created_at >= day_ago
    ).count()

    if recent_count > 10:
        return {'level': 'high', 'reason': f'User submitted {recent_count} evidence items in last 24 hours.'}
    elif recent_count > 5:
        return {'level': 'medium', 'reason': f'User submitted {recent_count} evidence items in last 24 hours.'}
    return None


def _ai_consistency_check(evidence):
    try:
        from google import genai
        client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        combined = f"""Situation: {evidence.situation_text}
Approach: {evidence.approach_text}
Decisions: {evidence.decisions_text}
Outcome: {evidence.outcome_text}"""

        prompt = f"""Assess the internal consistency of this professional work evidence.
Does the evidence have consistent internal logic? Are the claimed actions consistent with the stated outcome?
Rate on a scale of 1-5 where:
5 = perfectly consistent and believable
1 = major inconsistencies or implausible claims

TEXT:
{combined}

Return ONLY a single integer 1-5."""
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        score = int(re.search(r'[1-5]', response.text.strip()).group())
        if score < 3:
            return {'level': 'low', 'reason': f'AI consistency check scored {score}/5 — potential inconsistencies detected.'}
    except Exception as exc:
        logger.warning("AI consistency check failed: %s", exc)
    return None


def _verifier_relationship_check(evidence, user):
    from app.models.verification import Verification
    verifications = Verification.query.filter_by(evidence_id=evidence.id).all()
    if not verifications:
        return None

    user_email_domain = user.email.split('@')[1] if '@' in user.email else ''
    for v in verifications:
        verifier_domain = v.verifier_email.split('@')[1] if '@' in v.verifier_email else ''
        if user_email_domain and verifier_domain:
            if user_email_domain == verifier_domain and user_email_domain in ('gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'):
                return {'level': 'low', 'reason': 'Verifier uses the same free email domain as the user.'}
    return None


def _network_analysis(evidence):
    from app.models.verification import Verification

    verifications = Verification.query.filter_by(evidence_id=evidence.id).all()
    for v in verifications:
        verifier_email = v.verifier_email
        other_verifications = Verification.query.filter(
            Verification.verifier_email == verifier_email,
            Verification.evidence_id != evidence.id
        ).all()
        unique_users = set(ov.requester_user_id for ov in other_verifications)
        if len(unique_users) > 3:
            ring_user_ids = unique_users | {v.requester_user_id}
            cross_verifications = Verification.query.filter(
                Verification.requester_user_id.in_(ring_user_ids)
            ).all()
            verifier_emails_by_user = {}
            for cv in cross_verifications:
                verifier_emails_by_user.setdefault(cv.requester_user_id, set()).add(cv.verifier_email)
            user_emails = {}
            from app.models.user import User
            for uid in ring_user_ids:
                u = db_session_get_user(uid)
                if u:
                    user_emails[uid] = u.email

            ring_detected = False
            for uid, ver_emails in verifier_emails_by_user.items():
                for other_uid, other_email in user_emails.items():
                    if uid != other_uid and other_email in ver_emails:
                        ring_detected = True
                        break
                if ring_detected:
                    break

            if ring_detected:
                return {'level': 'medium', 'reason': 'Potential verification ring detected among connected users.'}

    return None


def db_session_get_user(user_id):
    from app.models.user import User
    from app.extensions import db
    return db.session.get(User, user_id)
