from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, BooleanField, SubmitField
from wtforms.validators import Optional, NumberRange


class EmployerSearchFilterForm(FlaskForm):
    domain = SelectField('Primary Domain', choices=[
        ('', 'All Domains'),
        ('Technology', 'Technology'),
        ('Marketing', 'Marketing'),
        ('Finance', 'Finance'),
        ('Design', 'Design'),
        ('Operations', 'Operations'),
        ('Research', 'Research'),
        ('Legal', 'Legal'),
        ('Healthcare', 'Healthcare'),
        ('Education', 'Education'),
    ], validators=[Optional()])
    keyword = StringField('Keyword Search', validators=[Optional()])
    skills = StringField('Skills', validators=[Optional()])
    min_evidence_count = IntegerField('Minimum Evidence', validators=[Optional(), NumberRange(min=0)])
    min_verification_rate = IntegerField('Min Verification Rate (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    require_challenge = BooleanField('Challenge Completion Required', validators=[Optional()])
    region = StringField('Region', validators=[Optional()])
    country = StringField('Country', validators=[Optional()])
    experience_min = IntegerField('Min Years Experience', validators=[Optional(), NumberRange(min=0)])
    experience_max = IntegerField('Max Years Experience', validators=[Optional(), NumberRange(min=0)])
    experience_level = SelectField('Experience Level', choices=[
        ('', 'Any'),
        ('junior', 'Junior'),
        ('mid', 'Mid'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
    ], validators=[Optional()])
    sort_by = SelectField('Sort By', choices=[
        ('relevance', 'Relevance'),
        ('verification_rate', 'Verification Rate'),
        ('evidence_count', 'Evidence Count'),
        ('recent_activity', 'Recent Activity'),
    ], default='relevance')
    submit = SubmitField('Search')
