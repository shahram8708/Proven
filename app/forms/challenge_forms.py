from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class ChallengeSubmissionForm(FlaskForm):
    response_text = TextAreaField('Your Response', validators=[DataRequired(), Length(min=100)])
    submit = SubmitField('Submit Response')
