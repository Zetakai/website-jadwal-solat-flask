"""Form WTForms untuk autentikasi (validasi server + CSRF)."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegisterForm(FlaskForm):
    name = StringField("Nama", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Kata Sandi", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField(
        "Ulangi Kata Sandi",
        validators=[DataRequired(), EqualTo("password", message="Kata sandi tidak cocok.")],
    )


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Kata Sandi", validators=[DataRequired()])
    remember = BooleanField("Ingat saya")
