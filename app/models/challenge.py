from datetime import datetime
from app.extensions import db


class WorkChallenge(db.Model):
    __tablename__ = 'work_challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    domain = db.Column(db.String(100), nullable=False)
    challenge_type = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    brief_text = db.Column(db.Text, nullable=False)
    instructions_text = db.Column(db.Text, nullable=False)
    evaluation_rubric = db.Column(db.JSON, nullable=False)
    time_limit_minutes = db.Column(db.Integer, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    is_sponsored = db.Column(db.Boolean, default=False)
    sponsor_employer_id = db.Column(db.Integer, db.ForeignKey('employer_accounts.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_completions = db.Column(db.Integer, default=0)
    avg_quality_score = db.Column(db.Float, default=0.0)

    submissions = db.relationship('ChallengeSubmission', backref='challenge', lazy='dynamic')

    def __repr__(self):
        return f'<WorkChallenge {self.title[:40]}>'


class ChallengeSubmission(db.Model):
    __tablename__ = 'challenge_submissions'

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('work_challenges.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    response_text = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_taken_minutes = db.Column(db.Integer)
    auto_quality_score = db.Column(db.Float)
    ai_feedback = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<ChallengeSubmission {self.id}>'
