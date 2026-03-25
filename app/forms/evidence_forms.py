from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import Length


EVIDENCE_TYPE_CHOICES = [
    ('project_delivery', 'Project Delivery'),
    ('problem_solved', 'Problem Solved'),
    ('decision_made', 'Decision Made'),
    ('process_improved', 'Process Improved'),
    ('collaboration_led', 'Collaboration Led'),
]

TEAM_SIZE_CHOICES = [
    ('', 'Select team size'),
    ('solo', 'Solo'),
    ('2-5', '2-5 people'),
    ('6-15', '6-15 people'),
    ('16-50', '16-50 people'),
    ('50+', '50+ people'),
]

PROJECT_SCALE_CHOICES = [
    ('', 'Select project scale'),
    ('personal', 'Personal'),
    ('team', 'Team'),
    ('department', 'Department'),
    ('company', 'Company'),
    ('multi-company', 'Multi-Company'),
]


class EvidenceForm(FlaskForm):
    title = StringField('Evidence Title', validators=[Length(max=500)])
    evidence_type = SelectField('Evidence Type', choices=EVIDENCE_TYPE_CHOICES)
    domain_tag = StringField('Domain', validators=[Length(max=100)])
    team_size_range = SelectField('Team Size', choices=TEAM_SIZE_CHOICES)
    project_scale = SelectField('Project Scale', choices=PROJECT_SCALE_CHOICES)
    situation_text = TextAreaField('Situation & Context')
    approach_text = TextAreaField('Your Approach')
    decisions_text = TextAreaField('Key Decisions & Reasoning')
    outcome_text = TextAreaField('Results & Outcomes')
    skills_text = TextAreaField('Skills Demonstrated')
    reflection_text = TextAreaField('Reflection & Learnings')
    submit = SubmitField('Submit Evidence')
