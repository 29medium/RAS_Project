from email.headerregistry import Address
from tokenize import String
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from rasbet.models import User
import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Nome de Utilizador', validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('Nome Completo', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Password', validators=[DataRequired(), EqualTo('password')])
    birth_date = DateField('Data de Nascimento', validators=[DataRequired()])
    nif = StringField('Número de Identificação Fiscal', validators=[DataRequired(), Length(min=9, max=9)])
    cc = StringField('Cartão de Cidadão', validators=[DataRequired(), Length(min=8, max=8)])
    iban = StringField('Iban', validators=[DataRequired(), Length(min=25, max=25)])
    address = StringField('Morada', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Número de Telemóvel', validators=[DataRequired()])

    submit = SubmitField('Registar')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('O nome de utilizador já existe')
    
    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('O email já está registado')
    
    def validate_birth_date(self, birth_date):
        max_date = datetime.datetime.now() - datetime.timedelta(days=18*365)
        if birth_date < max_date:
            raise ValidationError('Tem de ser maior de idade')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('Nome Completo', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    birth_date = DateField('Data de Nascimento', validators=[DataRequired()])
    nif = StringField('Número de Identificação Fiscal', validators=[DataRequired(), Length(min=9, max=9)])
    cc = StringField('Cartão de Cidadão', validators=[DataRequired(), Length(min=8, max=8)])
    iban = StringField('Iban', validators=[DataRequired(), Length(min=25, max=25)])
    address = StringField('Morada', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Número de Telemóvel', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError('That username is taken. Please choose another one')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            if User.query.filter_by(email=email.data).first():
                raise ValidationError('That email is taken. Please choose another one')

    def validate_birth_date(self, birth_date):
        max_date = datetime.datetime.now() - datetime.timedelta(days=18*365)
        if birth_date.data > max_date.date():
            raise ValidationError('Tem de ser maior de idade')