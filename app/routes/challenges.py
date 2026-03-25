from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.decorators import employer_required, premium_required
from app.models.challenge import WorkChallenge, ChallengeSubmission
from app.forms.challenge_forms import ChallengeSubmissionForm
from app.services.challenge_scorer import score_challenge_submission

challenges_bp = Blueprint('challenges', __name__)


@challenges_bp.route('/challenges/take/<int:id>', methods=['GET', 'POST'])
@login_required
def take_challenge(id):
    challenge = WorkChallenge.query.get_or_404(id)
    if not challenge.is_published:
        abort(404)

    existing = ChallengeSubmission.query.filter_by(
        challenge_id=id, user_id=current_user.id
    ).first()
    if existing:
        flash('You have already submitted a response to this challenge.', 'info')
        return redirect(url_for('challenges.submission_review', id=existing.id))

    form = ChallengeSubmissionForm()
    if form.validate_on_submit():
        time_taken = request.form.get('time_taken', 0, type=int)
        submission = ChallengeSubmission(
            challenge_id=challenge.id,
            user_id=current_user.id,
            response_text=form.response_text.data.strip(),
            time_taken_minutes=time_taken or challenge.time_limit_minutes,
            submitted_at=datetime.utcnow(),
        )
        db.session.add(submission)
        db.session.flush()

        result = score_challenge_submission(submission, challenge)
        submission.auto_quality_score = result['score']
        submission.ai_feedback = result['feedback']

        challenge.total_completions = (challenge.total_completions or 0) + 1
        all_scores = [s.auto_quality_score for s in challenge.submissions.all() if s.auto_quality_score]
        if all_scores:
            challenge.avg_quality_score = sum(all_scores) / len(all_scores)

        db.session.commit()

        flash('Challenge submitted and scored!', 'success')
        return redirect(url_for('challenges.submission_review', id=submission.id))

    return render_template('challenges/take.html', challenge=challenge, form=form)


@challenges_bp.route('/challenges/submission/<int:id>')
@login_required
def submission_review(id):
    submission = ChallengeSubmission.query.get_or_404(id)
    if submission.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    challenge = WorkChallenge.query.get(submission.challenge_id)
    return render_template('challenges/submission_review.html', submission=submission, challenge=challenge)


@challenges_bp.route('/employer/challenges/post', methods=['GET', 'POST'])
@employer_required
@premium_required
def post_sponsored_challenge():
    if request.method == 'POST':
        challenge = WorkChallenge(
            title=request.form.get('title', '').strip(),
            domain=request.form.get('domain', '').strip(),
            challenge_type=request.form.get('challenge_type', 'strategy'),
            difficulty=request.form.get('difficulty', 'intermediate'),
            brief_text=request.form.get('brief_text', '').strip(),
            instructions_text=request.form.get('instructions_text', '').strip(),
            evaluation_rubric={
                'clarity': 'Clear and well-structured response',
                'depth': 'Thorough analysis with supporting detail',
                'practicality': 'Actionable and realistic recommendations',
                'reasoning': 'Sound logical reasoning throughout',
            },
            time_limit_minutes=int(request.form.get('time_limit', 60)),
            is_published=True,
            is_sponsored=True,
            sponsor_employer_id=current_user.employer_account.id if current_user.employer_account else None,
        )
        db.session.add(challenge)
        db.session.commit()
        flash('Sponsored challenge published!', 'success')
        return redirect(url_for('employer_dashboard.employer_dashboard'))

    return render_template('challenges/post_sponsored.html')
