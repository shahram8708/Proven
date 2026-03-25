from datetime import datetime
from app.extensions import db


class SkillTaxonomy(db.Model):
    __tablename__ = 'skill_taxonomy'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    dimension = db.Column(db.String(50), nullable=False)
    domain = db.Column(db.String(100))
    parent_skill_id = db.Column(db.Integer, db.ForeignKey('skill_taxonomy.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)

    children = db.relationship('SkillTaxonomy', backref=db.backref('parent', remote_side='SkillTaxonomy.id'), lazy='dynamic')

    def __repr__(self):
        return f'<SkillTaxonomy {self.name}>'


class UserSkillTag(db.Model):
    __tablename__ = 'user_skill_tags'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill_taxonomy.id'), nullable=False)
    evidence_count = db.Column(db.Integer, default=0)
    verified_evidence_count = db.Column(db.Integer, default=0)
    skill_strength = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    skill = db.relationship('SkillTaxonomy', backref='user_tags')

    __table_args__ = (db.UniqueConstraint('user_id', 'skill_id'),)

    def __repr__(self):
        return f'<UserSkillTag user={self.user_id} skill={self.skill_id}>'
