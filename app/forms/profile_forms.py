from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class ProfileEditForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    professional_summary = TextAreaField('Professional Summary', validators=[Optional(), Length(max=2000)])
    primary_domain = SelectField('Primary Domain', choices=[
        ('', 'Select Domain'),
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
    location_city = StringField('City', validators=[Optional(), Length(max=100)])
    location_country = StringField('Country', validators=[Optional(), Length(max=100)])
    open_to_opportunities = BooleanField('Open to Opportunities')
    opportunity_type = SelectField('Opportunity Type', choices=[
        ('', 'Select Type'),
        ('freelance', 'Freelance'),
        ('full_time', 'Full Time'),
        ('both', 'Both'),
    ], validators=[Optional()])
    submit = SubmitField('Save Profile')


class ProfessionalSummaryForm(FlaskForm):
    professional_summary = TextAreaField('Professional Summary', validators=[DataRequired(), Length(min=50, max=2000)])
    submit = SubmitField('Save Summary')


class AccountSettingsForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(max=255)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save Settings')
