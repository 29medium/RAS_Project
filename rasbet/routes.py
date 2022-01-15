from locale import currency
from flask import render_template, url_for, flash, redirect, request
from rasbet import app, db, bcrypt
from rasbet.forms import *
from rasbet.models import *
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        balance = Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol

    competitions = [[],[],[]]
    for c in Competition.query.all():
        if c.sport_id == 0:
            competitions[0].append(c.name)
        elif c.sport_id == 1:
            competitions[1].append(c.name)
        elif c.sport_id == 2:
            competitions[2].append(c.name)

    return render_template('home.html', title='Home', competitions=competitions, balance=balance, symbol=symbol)

@app.route("/about")
def about():
    if current_user.is_authenticated:
        balance = Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol
        
    return render_template('about.html', title='About', balance=balance, symbol=symbol)

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
                    currency_fav=form.currency_fav.data,
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
    if current_user.is_authenticated:
        balance = Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol

    form = UpdateAccountForm()
    balances = {}
    wallets = Wallet.query.filter_by(user_id=current_user.id).all()

    for w in wallets:
        cur = Currency.query.filter_by(id=w.currency_id).first()
        balances[cur.name]=w.balance

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
        current_user.currency_fav = form.currency_fav.data
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
        form.currency_fav.data = current_user.currency_fav
        form.phone.data = current_user.phone  
    return render_template('account.html', title='Account', form=form, balances=balances, balance=balance, symbol=symbol)

@app.route("/account/deposit", methods=['GET', 'POST'])
@login_required
def deposit():
    if current_user.is_authenticated:
        balance = Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol

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

    return render_template('deposit.html', title='Deposit', form=form, balance=balance, symbol=symbol)

@app.route("/account/cashout", methods=['GET', 'POST'])
@login_required
def cashout():
    if current_user.is_authenticated:
        balance = Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol
        
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

    return render_template('cashout.html', title='Cashout', form=form, balance=balance, symbol=symbol)

@app.route("/account/convert", methods=['GET', 'POST'])
@login_required
def convert():
    if current_user.is_authenticated:
        balance = Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol
        
    form = ConvertForm()

    if form.validate_on_submit():
        mov_out = Movement(value=form.value.data,
                       type="convert",
                       date=datetime.now())
        db.session.add(mov_out)
        db.session.commit()

        wallet_out = Wallet.query.filter_by(user_id=current_user.id, currency_id=form.currency_id_out.data).first()
        
        wm_out = WalletMovement(movement_id=mov_out.id,
                            wallet_id=wallet_out.id)
        
        db.session.add(wm_out)

        wallet_out.balance -= form.value.data

        db.session.commit()

        wallet_in = Wallet.query.filter_by(user_id=current_user.id, currency_id=form.currency_id_in.data).first()

        new_value = form.value.data * 1/Currency.query.filter_by(id=wallet_in.currency_id).first().convertion_rate * Currency.query.filter_by(id=wallet_out.currency_id).first().convertion_rate * 0.98

        mov_in = Movement(value=new_value,
                       type="convert",
                       date=datetime.now())

        db.session.add(mov_in)
        db.session.commit()
    
        wm_in = WalletMovement(movement_id=mov_in.id,
                            wallet_id=wallet_in.id)

        wallet_in.balance += new_value
        
        db.session.add(wm_in)
        db.session.commit()

        return redirect(url_for('account'))

    return render_template('convert.html', title='Convert', form=form, balance=balance, symbol=symbol)

def ord_movements(m):
    return m.id

@app.route("/account/movements")
def movements():
    if current_user.is_authenticated:
        balance = Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol
        
    movements = []
    currencies = {}

    for w in Wallet.query.filter_by(user_id=current_user.id).all():
        for wm in w.wm:
            for m in Movement.query.filter_by(id=wm.movement_id).all():
                movements.append(m)
                currencies[m.id] = Currency.query.filter_by(id=w.currency_id).first().name

    movements.sort(reverse=True,key=ord_movements)

    return render_template('movements.html', title='Movemets', movements=movements, currencies=currencies, balance=balance, symbol=symbol)
