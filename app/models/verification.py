from datetime import datetime
from app.extensions import db


class Verification(db.Model):
    __tablename__ = 'verifications'

    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_submissions.id', ondelete='CASCADE'))
    requester_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    verifier_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    verifier_email = db.Column(db.String(255), nullable=False)
    verifier_name = db.Column(db.String(300))
    verifier_role = db.Column(db.String(300))
    verifier_company = db.Column(db.String(300))
    specific_claim = db.Column(db.Text, nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    token_expires = db.Column(db.DateTime, nullable=False)
    response = db.Column(db.String(50), default='pending')
    qualification_text = db.Column(db.Text)
    responded_at = db.Column(db.DateTime)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Verification {self.id} - {self.response}>'
