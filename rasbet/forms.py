from email.headerregistry import Address
from tokenize import String
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from rasbet.models import *
import datetime

def currencyList():
    currencies = Currency.query.with_entities(Currency.id, Currency.name, Currency.symbol).all()
    choices = list()

    for c in currencies:
        choices.append((c.id, c.name + " (" + c.symbol + ")"))

    return choices
# Formulário de registo
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
    phone = StringField('Número de Telemóvel', validators=[DataRequired(), Length(min=9, max=9)])
    currency_fav = SelectField(u'Selecionar Moeda Preferida', choices=currencyList(), validators=[DataRequired()])

    submit = SubmitField('Registar')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('O nome de utilizador já existe')
    
    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('O email já está registado')

    def validate_cc(self, cc):
        if User.query.filter_by(cc=cc.data).first():
            raise ValidationError('O cc já está registado')
    
    def validate_nif(self, nif):
        if User.query.filter_by(nif=nif.data).first():
            raise ValidationError('O nif já está registado')
    
    def validate_phone(self, phone):
        if User.query.filter_by(phone=phone.data).first():
            raise ValidationError('O número de telemóvel já está registado')
    
    def validate_birth_date(self, birth_date):
        max_date = datetime.datetime.now() - datetime.timedelta(days=18*365)
        if birth_date.data > max_date.date():
            raise ValidationError('Tem de ser maior de idade')

# formulário de login
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Lembrar')
    submit = SubmitField('Login')

# formulário de update de conta
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
    currency_fav = SelectField(u'Selecionar Moeda Preferida', choices=currencyList(), validators=[DataRequired()])
    submit = SubmitField('Atualizar')

    def validate_username(self, username):
        if username.data != current_user.username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError('O username já existe')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            if User.query.filter_by(email=email.data).first():
                raise ValidationError('O email já existe')
    
    def validate_cc(self, cc):
        if cc.data != current_user.cc:
            if User.query.filter_by(cc=cc.data).first():
                raise ValidationError('O cc já existe')

    def validate_nif(self, nif):
        if nif.data != current_user.nif:
            if User.query.filter_by(nif=nif.data).first():
                raise ValidationError('O nif já existe')

    def validate_phone(self, phone):
        if phone.data != current_user.phone:
            if User.query.filter_by(phone=phone.data).first():
                raise ValidationError('O número de telemovel já existe')

    def validate_birth_date(self, birth_date):
        max_date = datetime.datetime.now() - datetime.timedelta(days=18*365)
        if birth_date.data > max_date.date():
            raise ValidationError('Tem de ser maior de idade')

# formulario de depositar dinheiro
class DepositForm(FlaskForm):
    value = FloatField('Valor', validators=[DataRequired()])
    currency_id = SelectField(u'Moeda', choices=currencyList(), validators=[DataRequired()])

    submit = SubmitField('Depositar')

    def validate_value(self, value):
        if value.data < 0:
            raise ValidationError(f'O levantamento tem de ser de um valor positivo')
        else:
            min = 10 / Currency.query.filter_by(id=self.currency_id.data).first().convertion_rate
            if value.data < min:
                raise ValidationError(f'O depósito minimo é {min} {Currency.query.filter_by(id=self.currency_id.data).first().name}')

# formulário de levantar dinheiro
class CashOutForm(FlaskForm):
    value = FloatField('Valor', validators=[DataRequired()])
    currency_id = SelectField(u'Moeda', choices=currencyList(), validators=[DataRequired()])

    submit = SubmitField('Levantar')

    def validate_value(self, value):
        if value.data < 0:
            raise ValidationError(f'O levantamento tem de ser de um valor positivo')
        elif value.data > Wallet.query.filter_by(user_id=current_user.id, currency_id=self.currency_id.data).first().balance:
            raise ValidationError(f'Quantia indisponível na carteira')

# formulário de conversão de moeda
class ConvertForm(FlaskForm):
    value = FloatField('Valor', validators=[DataRequired()])
    currency_id_out = SelectField(u'Moeda', choices=currencyList(), validators=[DataRequired()])
    currency_id_in = SelectField(u'Moeda', choices=currencyList(), validators=[DataRequired()])
    
    submit = SubmitField('Converter')

    def validate_value(self, value):
        if value.data < 0:
            raise ValidationError(f'A conversão tem de ser de um valor positivo')
        elif value.data > Wallet.query.filter_by(user_id=current_user.id, currency_id=self.currency_id_out.data).first().balance:
            raise ValidationError(f'Quantia indisponível na carteira')
        elif self.currency_id_in.data == self.currency_id_out.data:
            raise ValidationError(f'A conversão tem de ser feita com duas moedas diferentes')

# formulário de aposta
class BetForm(FlaskForm):
    value = FloatField('Valor', validators=[DataRequired()])
    currency_id = SelectField(u'Moeda', choices=currencyList(), validators=[DataRequired()])

    submit = SubmitField('Apostar')

    def validate_value(self, value):
        min = 1 / Currency.query.filter_by(id=self.currency_id.data).first().convertion_rate
        if value.data<min:
            raise ValidationError(f'O valor mínimo da aposta é {min} {Currency.query.filter_by(id=self.currency_id.data).first().name}')
        elif value.data > Wallet.query.filter_by(user_id=current_user.id, currency_id=self.currency_id.data).first().balance:
            raise ValidationError(f'Quantia indisponível na carteira')