from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class SolveKata(FlaskForm):
    solution = TextAreaField("", validators=[DataRequired()])
