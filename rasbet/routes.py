from crypt import methods
from locale import currency
from flask import render_template, url_for, flash, redirect, request
from rasbet import app, db, bcrypt
from rasbet.forms import *
from rasbet.models import *
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    balance = None
    symbol = None
    if current_user.is_authenticated:
        balance = round(Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance, 2)
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol

    return render_template('home.html', title='Bets', balance=balance, symbol=symbol)

@app.route("/bets/<sport_id>/<competition_id>", methods=['GET', 'POST'])
def bets(sport_id, competition_id):
    balance = None
    symbol = None
    if current_user.is_authenticated:
        balance = round(Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance, 2)
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol

    competition_name = None
    sports = Sport.query.all()
    events = []
    e = []

    sport_name = Sport.query.filter_by(id=sport_id).first().name
    competitions = Competition.query.filter_by(sport_id=sport_id).all()
    if competition_id == "-1":
        for c in competitions:
            e += Event.query.filter_by(competition_id=c.id).all()
    else:
        competition_name = Competition.query.filter_by(id=competition_id).first().name
        e = Event.query.filter_by(competition_id=competition_id).all()

    for ee in e:
        odd = Odd.query.filter_by(event_id=ee.id).all()
        p = []
        for o in odd:
            p.append(Participant.query.filter_by(id=o.participant_id).first())
        events.append([ee, odd, p])

    if current_user.is_authenticated:
        form = BetForm()

        bet = Bet.query.filter_by(user_id=current_user.get_id(), state="Rascunho").first()
        bet_odds = []
        for bo in BetOdd.query.filter_by(bet_id=bet.id).all():
            bet_odds.append(Odd.query.filter_by(id=bo.odd_id).first())

        if form.validate_on_submit():
            bet.value = form.value.data
            bet.state = "Ativa"
            bet.date = datetime.now()
            db.session.commit()

            nova = Bet(state="Rascunho", odd=1, user_id=current_user.id)
            db.session.add(nova)
            db.session.commit()
            
            mov = Movement(value=form.value.data,
                       type="Apostas",
                       date=datetime.now())
            db.session.add(mov)
            db.session.commit()

            wallet = Wallet.query.filter_by(user_id=current_user.id, currency_id=form.currency_id.data).first()

            wm = WalletMovement(movement_id=mov.id,
                            wallet_id=wallet.id)
            db.session.add(wm)
            wallet.balance -= form.value.data
            db.session.commit()

            flash('Aposta efetuada com sucesso')
            return redirect(url_for('mybets'))

        return render_template('bets_logged_in.html', title='Bets', 
                               sport_id=sport_id, sport_name=sport_name, sports = sports, 
                               competition_id=competition_id, competition_name=competition_name, competitions=competitions,
                               events = events, balance=balance, symbol=symbol, form=form, bet=bet, bet_odds=bet_odds)
    else:
        return render_template('bets_logged_out.html', title='Bets', 
                               sport_id=sport_id, sport_name=sport_name, sports = sports, 
                               competition_id=competition_id, competition_name=competition_name, competitions=competitions,
                               events = events, balance=balance, symbol=symbol)

@app.route("/bets/odd/<sport_id>/<competition_id>/<odd_id>", methods=['GET', 'POST'])
@login_required
def odd(sport_id, competition_id, odd_id):
    bet = Bet.query.filter_by(user_id=current_user.get_id(), state="Rascunho").first()

    o_id = Odd.query.filter_by(id=odd_id).first()
    e_id = Event.query.filter_by(id=o_id.event_id).first()

    for bo in BetOdd.query.filter_by(bet_id=bet.id).all():
        o = Odd.query.filter_by(id=bo.odd_id).first()
        for e in Event.query.filter_by(id=o.event_id):
            if e.id == e_id.id:
                flash("Odd cannot be added", "danger")
                return redirect(url_for('bets', sport_id=sport_id, competition_id=competition_id))

    bet.odd *= o_id.value

    betOdd = BetOdd(bet_id=bet.id, odd_id=odd_id)
    db.session.add(betOdd)
    db.session.commit()

    flash("Odd added to the bet", "success")

    return redirect(url_for('bets', sport_id=sport_id, competition_id=competition_id))

@app.route("/mybets")
@login_required
def mybets():
    balance = None
    symbol = None
    if current_user.is_authenticated:
        balance = round(Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance, 2)
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol

    bets = []
    
    for bet in Bet.query.filter_by(user_id=current_user.id).all():
        if bet.state != "Rascunho":
            bets.append(bet)

    return render_template('mybets.html', title='Mybets', bets=bets, balance=balance, symbol=symbol)



@app.route("/about")
def about():
    balance = None
    symbol = None
    if current_user.is_authenticated:
        balance = round(Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance, 2)
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol
        
    return render_template('about.html', title='About', balance=balance, symbol=symbol)

@app.route("/faq")
def faq():
    balance = None
    symbol = None
    if current_user.is_authenticated:
        balance = round(Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance, 2)
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol
        
    return render_template('faq.html', title='FAQ', balance=balance, symbol=symbol)

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

        bet = Bet(state="Rascunho", odd=1, user_id=user.id)
        db.session.add(bet)
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
@login_required
def logout():
    logout_user()
    return(redirect(url_for('home')))

@app.route("/account")
@login_required
def account():
    balance = None
    symbol = None
    if current_user.is_authenticated:
        balance = round(Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance, 2)
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol

    balances = {}
    wallets = Wallet.query.filter_by(user_id=current_user.id).all()

    for w in wallets:
        cur = Currency.query.filter_by(id=w.currency_id).first()
        balances[cur.name]= str(round(w.balance, 2)) + " " + cur.symbol
    
    return render_template('account.html', title='Account', balances=balances, balance=balance, symbol=symbol)

@app.route("/account/update", methods=['GET', 'POST'])
@login_required
def update():
    balance = None
    symbol = None
    if current_user.is_authenticated:
        balance = round(Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance, 2)
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol

    form = UpdateAccountForm()

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
    
    return render_template('update.html', title='Update', form=form, balance=balance, symbol=symbol)

@app.route("/account/deposit", methods=['GET', 'POST'])
@login_required
def deposit():
    balance = None
    symbol = None
    if current_user.is_authenticated:
        balance = round(Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance, 2)
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol

    form = DepositForm()

    if form.validate_on_submit():
        mov = Movement(value=form.value.data,
                       type="Depósito",
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
    balance = None
    symbol = None
    if current_user.is_authenticated:
        balance = round(Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance, 2)
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol
        
    form = CashOutForm()

    if form.validate_on_submit():
        mov = Movement(value=form.value.data,
                       type="Levantamento",
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
    balance = None
    symbol = None
    if current_user.is_authenticated:
        balance = round(Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance, 2)
        symbol = Currency.query.filter_by(id=current_user.currency_fav).first().symbol
        
    form = ConvertForm()

    if form.validate_on_submit():
        mov_out = Movement(value=form.value.data,
                       type="Valor a converter",
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
                       type="Valor convertido",
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
    balance = None
    symbol = None
    if current_user.is_authenticated:
        balance = round(Wallet.query.filter_by(user_id=current_user.id,currency_id=current_user.currency_fav).first().balance, 2)
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

@app.route("/users")
@login_required
def users():
    if current_user.role == "user":
        return redirect(url_for('home'))
    else:
        users = User.query.all()
    return render_template('users.html', title='Users', users=users)