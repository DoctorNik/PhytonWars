from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class FormCreateTask(FlaskForm):
    title = StringField('', validators=[DataRequired()])
    description = TextAreaField('', validators=[DataRequired()])
    completed_solution = TextAreaField('', validators=[DataRequired()])
    tests = TextAreaField("", validators=[DataRequired()])
