import os
import json
import re
import logging

logger = logging.getLogger(__name__)


def score_challenge_submission(submission, challenge):
    try:
        from google import genai
        client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        rubric_json = json.dumps(challenge.evaluation_rubric)
        prompt = f"""You are evaluating a professional work challenge submission.

CHALLENGE: {challenge.title}
BRIEF: {challenge.brief_text}
EVALUATION RUBRIC: {rubric_json}

SUBMISSION TO EVALUATE:
{submission.response_text}

Score this submission against the rubric. Return JSON only:
{{"overall_score": 0-100, "feedback": "2-3 sentences of constructive feedback", "dimension_scores": {{"clarity": 0-100, "depth": 0-100, "practicality": 0-100, "reasoning": 0-100}}}}"""

        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        raw = response.text.strip()
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]
            if raw.endswith('```'):
                raw = raw[:-3]
            raw = raw.strip()

        result = json.loads(raw)
        return {
            'score': float(result.get('overall_score', 50)),
            'feedback': result.get('feedback', 'No feedback available.'),
            'dimension_scores': result.get('dimension_scores', {
                'clarity': 50, 'depth': 50, 'practicality': 50, 'reasoning': 50
            }),
        }
    except Exception as exc:
        logger.error("Challenge scoring failed: %s", exc)
        return {
            'score': 50.0,
            'feedback': 'Automated scoring is temporarily unavailable. Your submission has been recorded.',
            'dimension_scores': {'clarity': 50, 'depth': 50, 'practicality': 50, 'reasoning': 50},
        }
