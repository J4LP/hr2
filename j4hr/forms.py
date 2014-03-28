from flask_wtf import Form
from wtforms import TextField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class ApplicationForm(Form):
    character_id = TextField('Character ID', validators=[DataRequired()])
    character_name = TextField('Character Name', validators=[DataRequired()])
    email = TextField('Email', validators=[DataRequired(), Email()])
    corporation_id = TextField('Corporation ID', validators=[DataRequired()])
    corporation_name = TextField('Corporation Name',
                                 validators=[DataRequired()])
    key_id = TextField('Key ID', validators=[DataRequired()])
    vcode = TextField('vCode', validators=[DataRequired()])
    motivation = TextAreaField('Motivation', validators=[DataRequired(),
                                                         Length(min=5)])
