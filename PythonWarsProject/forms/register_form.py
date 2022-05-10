from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class FormRegister(FlaskForm):
    nickname = StringField("Choose your display name", validators=[DataRequired()])
    email = StringField("Set your email", validators=[DataRequired()])
    password = PasswordField("Choose your password", validators=[DataRequired()])
    repeated_password = PasswordField("Repeat your password", validators=[DataRequired()])
    submit = SubmitField("Create account")

