import json
import os
import logging

logger = logging.getLogger(__name__)


def extract_skills_from_evidence(evidence, taxonomy):
    full_evidence_text = f"""
Title: {evidence.title}
Situation: {evidence.situation_text}
Approach: {evidence.approach_text}
Decisions: {evidence.decisions_text}
Outcome: {evidence.outcome_text}
Skills: {evidence.skills_text}
Reflection: {evidence.reflection_text}
"""
    taxonomy_json = json.dumps([
        {"id": s.id, "name": s.name, "dimension": s.dimension}
        for s in taxonomy
    ])

    prompt = f"""You are a professional skills analyst. Extract professional skills DEMONSTRATED (not just mentioned) in this work evidence.

RULES:
1. Map ALL skills to the provided taxonomy. Only use taxonomy terms.
2. Classify each skill by dimension: technical / process / communication / leadership / problem_solving
3. Only include skills that are CLEARLY DEMONSTRATED with evidence of action or outcome.
4. Limit to 3-8 skills. Prioritize the most distinctive skills.
5. Return ONLY a JSON array. No explanation text.

TAXONOMY: {taxonomy_json}

WORK EVIDENCE: {full_evidence_text}

OUTPUT FORMAT: [{{"skill_id": X, "skill_name": "...", "dimension": "...", "confidence": 0.0-1.0}}]
Return JSON only."""

    try:
        from google import genai
        client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        raw = response.text.strip()
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]
            if raw.endswith('```'):
                raw = raw[:-3]
            raw = raw.strip()
        parsed = json.loads(raw)
        valid_ids = {s.id for s in taxonomy}
        results = []
        for item in parsed:
            if isinstance(item, dict) and item.get('skill_id') in valid_ids:
                results.append({
                    'skill_id': item['skill_id'],
                    'skill_name': item.get('skill_name', ''),
                    'dimension': item.get('dimension', ''),
                    'confidence': min(1.0, max(0.0, float(item.get('confidence', 0.5)))),
                })
        return results[:8]
    except Exception as exc:
        logger.error("AI skill extraction failed: %s", exc)
        return []
