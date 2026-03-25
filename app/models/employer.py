from datetime import datetime
from app.extensions import db


class EmployerAccount(db.Model):
    __tablename__ = 'employer_accounts'

    id = db.Column(db.Integer, primary_key=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    company_name = db.Column(db.String(300), nullable=False)
    company_domain = db.Column(db.String(200))
    company_size = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    monthly_contact_credits = db.Column(db.Integer, default=0)
    total_profiles_viewed = db.Column(db.Integer, default=0)
    subscription_tier = db.Column(db.String(50), default='free')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    talent_lists = db.relationship('TalentList', backref='employer', lazy='dynamic')

    def __repr__(self):
        return f'<EmployerAccount {self.company_name}>'


class TalentList(db.Model):
    __tablename__ = 'talent_lists'

    id = db.Column(db.Integer, primary_key=True)
    employer_account_id = db.Column(db.Integer, db.ForeignKey('employer_accounts.id'))
    name = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_shared = db.Column(db.Boolean, default=False)

    members = db.relationship(
        'TalentListMember', backref='list', lazy='dynamic', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<TalentList {self.name}>'


class TalentListMember(db.Model):
    __tablename__ = 'talent_list_members'

    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('talent_lists.id', ondelete='CASCADE'))
    talent_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    employer_notes = db.Column(db.Text)
    pipeline_stage = db.Column(db.String(50), default='shortlisted')

    talent = db.relationship('User', backref='list_memberships')

    def __repr__(self):
        return f'<TalentListMember list={self.list_id} talent={self.talent_user_id}>'
