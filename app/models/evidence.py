from datetime import datetime
from app.extensions import db


class EvidenceSubmission(db.Model):
    __tablename__ = 'evidence_submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    evidence_type = db.Column(db.String(50), nullable=False)
    situation_text = db.Column(db.Text, nullable=False)
    approach_text = db.Column(db.Text, nullable=False)
    decisions_text = db.Column(db.Text, nullable=False)
    outcome_text = db.Column(db.Text, nullable=False)
    skills_text = db.Column(db.Text, nullable=False)
    reflection_text = db.Column(db.Text, nullable=False)
    domain_tag = db.Column(db.String(100))
    team_size_range = db.Column(db.String(50))
    project_scale = db.Column(db.String(50))
    is_published = db.Column(db.Boolean, default=False)
    is_draft = db.Column(db.Boolean, default=True)
    submitted_at = db.Column(db.DateTime)
    quality_score = db.Column(db.Float, default=0.0)
    verification_count = db.Column(db.Integer, default=0)
    ai_extracted_skills = db.Column(db.JSON)
    confirmed_skill_tags = db.Column(db.JSON)
    fraud_flag_level = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    files = db.relationship(
        'EvidenceFile', backref='evidence', lazy='dynamic', cascade='all, delete-orphan'
    )
    verifications = db.relationship('Verification', backref='evidence', lazy='dynamic')

    def __repr__(self):
        return f'<EvidenceSubmission {self.id}: {self.title[:40]}>'


class EvidenceFile(db.Model):
    __tablename__ = 'evidence_files'

    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_submissions.id', ondelete='CASCADE'))
    original_filename = db.Column(db.String(500))
    storage_path = db.Column(db.String(1000))
    file_type = db.Column(db.String(50))
    file_size_bytes = db.Column(db.Integer)
    visibility = db.Column(db.String(50), default='employer_premium')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<EvidenceFile {self.original_filename}>'
