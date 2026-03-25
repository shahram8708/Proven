from datetime import datetime
from app.extensions import db


class ContactRequest(db.Model):
    __tablename__ = 'contact_requests'

    id = db.Column(db.Integer, primary_key=True)
    employer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    talent_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)

    employer = db.relationship('User', foreign_keys=[employer_user_id], backref='sent_contact_requests')
    talent = db.relationship('User', foreign_keys=[talent_user_id], backref='received_contact_requests')

    def __repr__(self):
        return f'<ContactRequest {self.id} from employer={self.employer_user_id} to talent={self.talent_user_id}>'
