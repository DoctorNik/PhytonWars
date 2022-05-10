from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class FormLogin(FlaskForm):
    nickname = StringField("Input nickname", validators=[DataRequired()])
    password = PasswordField("Input password", validators=[DataRequired()])
    submit = SubmitField("Log in")

