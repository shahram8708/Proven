from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class VerificationRequestForm(FlaskForm):
    verifier_name = StringField('Verifier Full Name', validators=[DataRequired(), Length(max=300)])
    verifier_email = StringField('Verifier Email', validators=[DataRequired(), Email(), Length(max=255)])
    verifier_role = StringField('Verifier Role/Title', validators=[Length(max=300)])
    verifier_company = StringField('Verifier Company', validators=[Length(max=300)])
    specific_claim = TextAreaField('What specific claim should they verify?', validators=[DataRequired(), Length(min=20)])
    submit = SubmitField('Send Verification Request')


class VerifierResponseForm(FlaskForm):
    response = SelectField('Your Response', choices=[
        ('confirmed', 'I confirm this is accurate'),
        ('confirmed_with_qualification', 'I confirm with qualifications'),
        ('cannot_confirm', 'I cannot confirm this'),
    ], validators=[DataRequired()])
    qualification_text = TextAreaField('Additional Comments (optional)', validators=[Length(max=2000)])
    submit = SubmitField('Submit Response')
