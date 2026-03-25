import re
import os
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def compute_quality_score(evidence):
    score = 0.0
    score += _completeness_score(evidence)
    score += _specificity_score(evidence)
    score += _measurability_score(evidence)
    score += _verification_score(evidence)
    score += _recency_score(evidence)
    score += _anti_fraud_score(evidence)
    return round(min(100.0, score), 1)


def _completeness_score(evidence):
    fields = [
        evidence.situation_text or '',
        evidence.approach_text or '',
        evidence.decisions_text or '',
        evidence.outcome_text or '',
        evidence.skills_text or '',
        evidence.reflection_text or '',
    ]
    total = 0
    for field in fields:
        word_count = len(field.split())
        if word_count >= 200:
            total += 3
        elif word_count >= 100:
            total += 2
        elif word_count >= 50:
            total += 1
    return (total / 18.0) * 20.0


def _specificity_score(evidence):
    try:
        from google import genai
        client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        combined = f"Approach: {evidence.approach_text}\nOutcome: {evidence.outcome_text}"
        prompt = f"""Rate how specific vs generic this professional work evidence is on a scale of 0-5.
5 = highly specific with concrete details, names, numbers, technologies, and measurable results.
0 = completely generic with no specific details.

TEXT:
{combined}

Return ONLY a single integer 0-5."""
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        rating = int(re.search(r'[0-5]', response.text.strip()).group())
        return (rating / 5.0) * 20.0
    except Exception as exc:
        logger.warning("Specificity AI scoring failed: %s", exc)
        return 10.0


def _measurability_score(evidence):
    outcome = evidence.outcome_text or ''
    patterns = [
        r'\d+%',
        r'[₹$€£]\s*[\d,]+',
        r'\d+\s*(months?|weeks?|days?|hours?|years?)',
        r'\d+x',
        r'\d+\s*(users?|customers?|clients?|employees?|teams?)',
        r'\d+',
    ]
    found = 0
    for pat in patterns:
        if re.search(pat, outcome, re.IGNORECASE):
            found += 1
    if found == 0:
        return 0
    elif found == 1:
        return 10
    elif found == 2:
        return 15
    return 20


def _verification_score(evidence):
    from app.models.verification import Verification
    verifications = Verification.query.filter_by(evidence_id=evidence.id).all()
    confirmed_count = 0.0
    for v in verifications:
        if v.response == 'confirmed':
            confirmed_count += 1.0
        elif v.response == 'confirmed_with_qualification':
            confirmed_count += 0.7

    if confirmed_count >= 3:
        return 25
    elif confirmed_count >= 2:
        return 22
    elif confirmed_count >= 1:
        return 15
    return 0


def _recency_score(evidence):
    submitted = evidence.submitted_at or evidence.created_at
    if not submitted:
        return 1
    months_ago = (datetime.utcnow() - submitted).days / 30.0
    if months_ago <= 12:
        return 10
    elif months_ago <= 24:
        return 7
    elif months_ago <= 36:
        return 4
    return 1


def _anti_fraud_score(evidence):
    if evidence.fraud_flag_level in (None, 'clean'):
        return 5
    return 0
