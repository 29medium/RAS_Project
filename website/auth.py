from flask import Blueprint, render_template, request, flash
from . import execute_querie

import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    data = request.form
    email = data.get('email')
    password = data.get('password')
    # insert comparação de passwords
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return "<p>Logout</p>"

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        cc = request.form.get("cc")
        nif = request.form.get("nif")
        iban = request.form.get("iban")
        date = request.form.get("dataN")
        
        valid = True
        if not name:
            flash('Nome não preenchido',category='error')
            valid = False
        if not username:
            flash('Username não preenchido',category='error')
            valid = False
        if not email:
            flash('Email não preenchido',category='error')
            valid = False
        if not password1 or not password2:
            flash('Password não preenchida',category='error')
            valid = False
        if not date:
            flash('Data não preenchida',category='error')
            valid = False
        if not cc:
            flash('Cartão de Cidadão não preenchido', category='error')
            valid = False
        if not nif:
            flash('Número de Identificação Fiscal não preenchido', category='error')
            valid = False
        if not iban:
            flash('IBAN não introduzido', category='error')
            valid = False
        
        if valid:
            if password1 != password2:
                flash('Passwords must be equal',category='error')
            else:
                flash("User Created", category='success')
                add_user = '''INSERT INTO User
                    (username, name, email, password, iban, nif, cc, birth_date, type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, "1") ;'''
                
                data_user = (username, name, email, password1, iban, nif, cc, date)

                execute_querie(add_user, data_user)
                

    x = datetime.datetime.now() 
    y = str(datetime.date(year=x.year-18,month=x.month,day=x.day))
    return render_template("sign_up.html", maxDate=y)