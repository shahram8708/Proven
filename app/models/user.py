from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    account_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_email_verified = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    subscription_tier = db.Column(db.String(50), default='free')
    subscription_expires = db.Column(db.DateTime)
    razorpay_customer_id = db.Column(db.String(100))
    razorpay_subscription_id = db.Column(db.String(100))
    onboarding_complete = db.Column(db.Boolean, default=False)
    primary_domain = db.Column(db.String(100))
    years_experience = db.Column(db.Integer)
    location_city = db.Column(db.String(100))
    location_country = db.Column(db.String(100))
    open_to_opportunities = db.Column(db.Boolean, default=True)
    opportunity_type = db.Column(db.String(50))
    profile_photo_url = db.Column(db.String(500))
    professional_summary = db.Column(db.Text)
    profile_strength = db.Column(db.Float, default=0.0)
    is_admin = db.Column(db.Boolean, default=False)
    linkedin_id = db.Column(db.String(100))

    evidence_submissions = db.relationship(
        'EvidenceSubmission', backref='user', lazy='dynamic', cascade='all, delete-orphan'
    )
    skill_tags = db.relationship(
        'UserSkillTag', backref='user', lazy='dynamic', cascade='all, delete-orphan'
    )
    challenge_submissions = db.relationship(
        'ChallengeSubmission', backref='user', lazy='dynamic'
    )
    employer_account = db.relationship(
        'EmployerAccount', backref='owner', uselist=False, cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'<User {self.username}>'
