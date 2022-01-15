from locale import currency
from flask import render_template, url_for, flash, redirect, request
from rasbet import app, db, bcrypt
from rasbet.forms import *
from rasbet.models import *
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return(redirect(url_for('home')))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    name=form.name.data,
                    email=form.email.data, 
                    password=hashed_password,
                    birth_date=form.birth_date.data,
                    nif=form.nif.data,
                    cc=form.cc.data,
                    iban=form.iban.data,
                    address=form.address.data,
                    phone=form.phone.data,
                    role="user")
        db.session.add(user)
        db.session.commit()

        currencies = Currency.query.all()
        for cur in currencies:
            wallet = Wallet(balance=0.0, user_id=user.id, currency_id=cur.id)
            print(wallet)
            db.session.add(wallet)
        db.session.commit()
        
        flash('Your account has been created! You are now able to login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return(redirect(url_for('home')))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessfull. Please check username and password', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return(redirect(url_for('home')))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    balance = {}
    wallets = Wallet.query.filter_by(user_id=current_user.id).all()

    for w in wallets:
        cur = Currency.query.filter_by(id=w.currency_id).first()
        balance[cur.name]=w.balance

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.birth_date = form.birth_date.data
        current_user.nif = form.nif.data
        current_user.cc = form.cc.data
        current_user.iban = form.iban.data
        current_user.address = form.address.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.birth_date.data = current_user.birth_date
        form.nif.data = current_user.nif
        form.cc.data = current_user.cc
        form.iban.data = current_user.iban
        form.address.data = current_user.address
        form.phone.data = current_user.phone  
    return render_template('account.html', title='Account', form=form, balance=balance)

@app.route("/account/deposit", methods=['GET', 'POST'])
@login_required
def deposit():
    form = DepositForm()

    if form.validate_on_submit():
        mov = Movement(value=form.value.data,
                       type="deposit",
                       date=datetime.now())
        db.session.add(mov)
        db.session.commit()

        wallet = Wallet.query.filter_by(user_id=current_user.id, currency_id=form.currency_id.data).first()

        wm = WalletMovement(movement_id=mov.id,
                            wallet_id=wallet.id)
        db.session.add(wm)
        wallet.balance += form.value.data
        db.session.commit()

        flash('Depósito efetuado com sucesso')
        return redirect(url_for('account'))

    return render_template('deposit.html', title='Deposit', form=form)

@app.route("/account/cashout", methods=['GET', 'POST'])
@login_required
def cashout():
    form = CashOutForm()

    if form.validate_on_submit():
        mov = Movement(value=form.value.data,
                       type="cashout",
                       date=datetime.now())
        db.session.add(mov)
        db.session.commit()

        wallet = Wallet.query.filter_by(user_id=current_user.id, currency_id=form.currency_id.data).first()

        wm = WalletMovement(movement_id=mov.id,
                            wallet_id=wallet.id)
        db.session.add(wm)
        wallet.balance -= form.value.data
        db.session.commit()

        flash('Levantamento efetuado com sucesso')
        return redirect(url_for('account'))

    return render_template('deposit.html', title='Cashout', form=form)