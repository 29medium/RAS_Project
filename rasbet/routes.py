from crypt import methods
from locale import currency
from flask import render_template, url_for, flash, redirect, request
from rasbet import app, db, bcrypt
from rasbet.forms import *
from rasbet.models import *
from flask_login import login_user, current_user, logout_user, login_required
import json

## ficheiro de routes
## especificado os caminhos a que um utilizador logado(ou não) pode aceder

# Função que devolve os pre requisitos de uma página para conter informação na navbar
def pre_requisits():
    balance = None
    balances = {}
    symbol = None
    notifications = []
    if current_user.is_authenticated:
        balance = round(Wallet.query.filter_by(user_id=current_user.id,
                        currency_id=current_user.currency_fav).first().balance, 2)
        symbol = Currency.query.filter_by(
            id=current_user.currency_fav).first().symbol

        wallets = Wallet.query.filter_by(user_id=current_user.id).all()

        notifications = Notification.query.filter_by(user_id=current_user.id).all()

        for w in wallets:
            cur = Currency.query.filter_by(id=w.currency_id).first()
            balances[cur.name] = str(round(w.balance, 2)) + " " + cur.symbol
    
    return balance, balances, symbol, notifications

# Route para a página inicial
@app.route("/")
@app.route("/home")
def home():
    balance, balances, symbol, notifications = pre_requisits()

    return render_template('home.html', title='Bets', balance=balance, symbol=symbol, balances=balances, notifications=notifications)

# Método que determina a ordenação do array de apostas
def ord_bets(e):
    return e[0].start_date

# Route para a página apostar
@app.route("/bets/<sport_id>/<competition_id>", methods=['GET', 'POST'])
def bets(sport_id, competition_id):
    wallet_DB = Wallet.query.all()
    currency_DB = Currency.query.all()
    sport_DB = Sport.query.all()
    competition_DB = Competition.query.all()
    event_DB = Event.query.filter_by(state=0).all()
    participant_DB = Participant.query.all()
    betOdd_DB = BetOdd.query.all()
    odd_DB = Odd.query.all()

    balance = None
    balances = {}
    symbol = None

    if current_user.is_authenticated:
        for line in wallet_DB:
            if line.user_id == current_user.id and line.currency_id == current_user.currency_fav:
                balance = round(line.balance, 2)
                break

        for line in currency_DB:
            if line.id == current_user.currency_fav:
                symbol = line.symbol
                break

        wallets = []
        for line in wallet_DB:
            if line.user_id == current_user.id:
                wallets.append(line)

        for w in wallets:
            cur = None
            for line in currency_DB:
                if line.id == w.currency_id:
                    cur = line
                    break
            balances[cur.name] = str(round(w.balance, 2)) + " " + cur.symbol

    competition_name = None

    events = []
    e = []

    sport_name = None
    for line in sport_DB:
        if line.id == int(sport_id):
            sport_name = line.name
            break

    competitions = []
    for line in competition_DB:
        if line.sport_id == int(sport_id):
            competitions.append(line)

    if competition_id == "-1":
        for c in competitions:
            temp = []
            for line in event_DB:
                if line.competition_id == c.id:
                    temp.append(line)
            e += temp
    else:
        competition_name = None
        for line in competition_DB:
            if line.id == int(competition_id):
                competition_name = line.name
                break

        for line in event_DB:
            if line.competition_id == int(competition_id):
                e.append(line)

    for ee in e:
        odd = []
        for line in odd_DB:
            if line.event_id == ee.id:
                odd.append(line)

        p = []
        for o in odd:
            for line in participant_DB:
                if line.id == o.participant_id:
                    p.append(line)
                    break

        events.append([ee, odd, p])
        events.sort(key=ord_bets)

    notifications = []
    if current_user.is_authenticated:
        notifications = Notification.query.filter_by(user_id=current_user.id).all()
        form = BetForm()

        bet = Bet.query.filter_by(
            user_id=current_user.get_id(), state="Rascunho").first()
        bet_odds = []
        odd_ids = []

        allbetods = []
        for line in betOdd_DB:
            if line.bet_id == bet.id:
                allbetods.append(line)
        for bo in allbetods:
            zOdd = None
            for line in odd_DB:
                if line.id == bo.odd_id:
                    zOdd = line
                    break

            if zOdd.participant_id == None:
                for line in event_DB:
                    if line.id == zOdd.event_id:
                        bet_odds.append((zOdd, line.name, "Empate"))

            else:
                for line in event_DB:
                    if line.id == zOdd.event_id:
                        for line2 in participant_DB:
                            if line2.id == zOdd.participant_id:
                                bet_odds.append((zOdd, line.name, line2.name))
                                break
                        break

            odd_ids.append(zOdd.id)
        if form.validate_on_submit():
            new_bo = BetOdd.query.filter_by(bet_id=bet.id).all()
            if new_bo:
                bet.value = int(form.value.data)
                bet.state = "Ativa"
                bet.date = datetime.now()
                bet.currency_id = int(form.currency_id.data)

                nova = Bet(state="Rascunho", odd=1, user_id=current_user.id)
                db.session.add(nova)

                mov = Movement(value=form.value.data,
                            type="Apostas",
                            date=datetime.now())
                db.session.add(mov)
                db.session.commit()

                wallet = None

                for line in wallet_DB:

                    if line.user_id == current_user.id and line.currency_id == int(form.currency_id.data):
                        wallet = line
                        break

                wm = WalletMovement(movement_id=mov.id,
                                    wallet_id=wallet.id)
                db.session.add(wm)
                wallet.balance -= int(form.value.data)
                db.session.commit()

                flash('Aposta efetuada com sucesso', 'success')
                return redirect(url_for('mybets'))
            else:
                flash('Não tem nenhuma odd selecionada', 'danger')

        return render_template('bets_logged_in.html', title='Bets',
                               sport_id=sport_id, sport_name=sport_name, sports=sport_DB,
                               competition_id=competition_id, competition_name=competition_name, competitions=competitions,
                               events=events, balance=balance, symbol=symbol, balances=balances, notifications=notifications, form=form, bet=bet, bet_odds={"bet_odds": bet_odds, "odd_ids": odd_ids})
    else:
        return render_template('bets_logged_out.html', title='Bets',
                               sport_id=sport_id, sport_name=sport_name, sports=sport_DB,
                               competition_id=competition_id, competition_name=competition_name, competitions=competitions,
                               events=events, balance=balance, symbol=symbol, balances=balances, notifications=notifications)


# Route para a página de uma aposta
@app.route("/bet/<bet_id>")
def bet(bet_id):
    balance, balances, symbol, notifications = pre_requisits()

    bet = Bet.query.filter_by(id=bet_id).first()

    bet_odds = []
    allbetods = []
    for line in BetOdd.query.all():
        if line.bet_id == bet.id:
            allbetods.append(line)

    for bo in allbetods:
        zOdd = None
        for line in Odd.query.all():
            if line.id == bo.odd_id:
                zOdd = line
                break

        if zOdd.participant_id == None:
            for line in Event.query.all():
                if line.id == zOdd.event_id:
                    bet_odds.append((zOdd, line.name, "Empate", line.state))

        else:
            for line in Event.query.all():
                if line.id == zOdd.event_id:
                    for line2 in Participant.query.all():
                        if line2.id == zOdd.participant_id:
                            bet_odds.append((zOdd, line.name, line2.name, line.state))
                            break
                    break

    return render_template('bet.html', bet=bet, bet_odds=bet_odds, balance=balance, symbol=symbol, balances=balances, notifications=notifications)


# Route para adicionar uma odd a uma aposta
@app.route("/bets/odd/<sport_id>/<competition_id>/<odd_id>", methods=['GET', 'POST'])
@login_required
def odd(sport_id, competition_id, odd_id):
    bet = Bet.query.filter_by(
        user_id=current_user.get_id(), state="Rascunho").first()

    o_id = Odd.query.filter_by(id=odd_id).first()
    e_id = Event.query.filter_by(id=o_id.event_id).first()

    for bo in BetOdd.query.filter_by(bet_id=bet.id).all():
        o = Odd.query.filter_by(id=bo.odd_id).first()
        for e in Event.query.filter_by(id=o.event_id):
            if e.id == e_id.id:
                flash("Não pode haver duas odds do mesmo evento", "danger")
                return redirect(url_for('bets', sport_id=sport_id, competition_id=competition_id))

    bet.odd *= o_id.value

    betOdd = BetOdd(bet_id=bet.id, odd_id=odd_id)
    db.session.add(betOdd)
    db.session.commit()

    return redirect(url_for('bets', sport_id=sport_id, competition_id=competition_id))

# Route para remover uma odd de uma aposta
@app.route("/bets/remove_odd/<sport_id>/<competition_id>/<odd_id>", methods=['GET', 'DELETE'])
@login_required
def remove_odd(sport_id, competition_id, odd_id):
    bet = Bet.query.filter_by(
        user_id=current_user.get_id(), state="Rascunho").first()

    bo = BetOdd.query.filter_by(bet_id=bet.id, odd_id=odd_id).first()

    db.session.delete(bo)

    bet.odd /= Odd.query.filter_by(id=odd_id).first().value

    db.session.commit()

    return redirect(url_for('bets', sport_id=sport_id, competition_id=competition_id))

# Route para a página das minhas apostas
@app.route("/mybets")
@login_required
def mybets():
    balance, balances, symbol, notifications = pre_requisits()

    bets = {}

    for bet in Bet.query.filter_by(user_id=current_user.id).all():
        if bet.state != "Rascunho":
            cur = Currency.query.filter_by(id=bet.currency_id).first()
            bets[bet] = cur.name + " (" + cur.symbol + ")"

    return render_template('mybets.html', title='Mybets', bets=bets, balance=balance, symbol=symbol, balances=balances, notifications=notifications)

# Route para a página sobre
@app.route("/about")
def about():
    balance, balances, symbol, notifications = pre_requisits()

    return render_template('about.html', title='About', balance=balance, symbol=symbol, balances=balances, notifications=notifications)

# Route para a página faq
@app.route("/faq")
def faq():
    balance, balances, symbol, notifications = pre_requisits()

    data = json.load(open('rasbet/files/faq.json'))
    return render_template('faq.html', title='FAQ', balance=balance, symbol=symbol, balances=balances, data=data, notifications=notifications)

# Route para a página de registo
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return(redirect(url_for('home')))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
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
            db.session.add(wallet)
        db.session.commit()

        bet = Bet(state="Rascunho", odd=1, user_id=user.id)
        db.session.add(bet)
        db.session.commit()

        flash('A sua conta foi criada com sucesso! Pode agora fazer login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# Route para a página de login
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
            flash('Login efetuado com sucesso!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login efetuado sem sucesso! Verifique o email e a password', 'danger')

    return render_template('login.html', title='Login', form=form)

# Route para efetuar logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logout efetuado com sucesso', 'info')
    return(redirect(url_for('home')))

# Route para a página da conta
@app.route("/account")
@login_required
def account():
    balance, balances, symbol, notifications = pre_requisits()

    return render_template('account.html', title='Account', balances=balances, balance=balance, symbol=symbol, notifications=notifications)

# Route para atualizar as informações da conta
@app.route("/account/update", methods=['GET', 'POST'])
@login_required
def update():
    balance, balances, symbol, notifications = pre_requisits()

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
        flash('A sua conta foi atualizada com sucesso', 'success')
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

    return render_template('update.html', title='Update', form=form, balance=balance, balances=balances, symbol=symbol, notifications=notifications)

# Route para a página de depósito
@app.route("/account/deposit", methods=['GET', 'POST'])
@login_required
def deposit():
    balance, balances, symbol, notifications = pre_requisits()

    form = DepositForm()

    if form.validate_on_submit():
        mov = Movement(value=form.value.data,
                       type="Depósito",
                       date=datetime.now())
        db.session.add(mov)

        wallet = Wallet.query.filter_by(
            user_id=current_user.id, currency_id=form.currency_id.data).first()

        wm = WalletMovement(movement_id=mov.id,
                            wallet_id=wallet.id)
        db.session.add(wm)
        wallet.balance += form.value.data
        db.session.commit()

        flash('Depósito efetuado com sucesso', 'success')
        return redirect(url_for('account'))

    return render_template('deposit.html', title='Deposit', form=form, balance=balance, balances=balances, symbol=symbol, notifications=notifications)

# Route para a página de levantamento
@app.route("/account/cashout", methods=['GET', 'POST'])
@login_required
def cashout():
    balance, balances, symbol, notifications = pre_requisits()

    form = CashOutForm()

    if form.validate_on_submit():
        mov = Movement(value=form.value.data,
                       type="Levantamento",
                       date=datetime.now())
        db.session.add(mov)

        wallet = Wallet.query.filter_by(
            user_id=current_user.id, currency_id=form.currency_id.data).first()

        wm = WalletMovement(movement_id=mov.id,
                            wallet_id=wallet.id)
        db.session.add(wm)
        wallet.balance -= form.value.data
        db.session.commit()

        flash('Levantamento efetuado com sucesso', 'success')
        return redirect(url_for('account'))

    return render_template('cashout.html', title='Cashout', form=form, balance=balance, balances=balances, symbol=symbol, notifications=notifications)

# Route para a página de converter moedas
@app.route("/account/convert", methods=['GET', 'POST'])
@login_required
def convert():
    balance, balances, symbol, notifications = pre_requisits()

    form = ConvertForm()

    if form.validate_on_submit():
        mov_out = Movement(value=form.value.data,
                           type="Valor a converter",
                           date=datetime.now())
        db.session.add(mov_out)
        db.session.commit()

        print(mov_out)

        wallet_out = Wallet.query.filter_by(
            user_id=current_user.id, currency_id=form.currency_id_out.data).first()

        wm_out = WalletMovement(movement_id=mov_out.id,
                                wallet_id=wallet_out.id)

        db.session.add(wm_out)

        wallet_out.balance -= form.value.data

        wallet_in = Wallet.query.filter_by(
            user_id=current_user.id, currency_id=form.currency_id_in.data).first()

        new_value = form.value.data * 1/Currency.query.filter_by(id=wallet_in.currency_id).first(
        ).convertion_rate * Currency.query.filter_by(id=wallet_out.currency_id).first().convertion_rate * 0.98

        mov_in = Movement(value=new_value,
                          type="Valor convertido",
                          date=datetime.now())

        db.session.add(mov_in)
        db.session.commit()

        print(mov_in)

        wm_in = WalletMovement(movement_id=mov_in.id,
                               wallet_id=wallet_in.id)

        wallet_in.balance += new_value

        db.session.add(wm_in)
        db.session.commit()

        flash('Conversão efetuado com sucesso', 'success')
        return redirect(url_for('account'))

    return render_template('convert.html', title='Convert', form=form, balance=balance, balances=balances, symbol=symbol, notifications=notifications)

# Método responsável pela ordem do array movimentos
def ord_movements(m):
    return m.id

# Route para a página dos movimentos
@app.route("/account/movements")
def movements():
    balance, balances, symbol, notifications = pre_requisits()

    movements = []
    currencies = {}

    for w in Wallet.query.filter_by(user_id=current_user.id).all():
        for wm in w.wm:
            for m in Movement.query.filter_by(id=wm.movement_id).all():
                movements.append(m)
                currencies[m.id] = Currency.query.filter_by(
                    id=w.currency_id).first().name

    movements.sort(reverse=True, key=ord_movements)

    return render_template('movements.html', title='Movemets', movements=movements, currencies=currencies, balance=balance, symbol=symbol, balances=balances, notifications=notifications)

# Route para a página dos utilizadores
@app.route("/users")
@login_required
def users():
    if current_user.role == "user":
        return redirect(url_for('home'))
    else:
        users = {}
        for u in User.query.all():
            users[u] = Currency.query.filter_by(id=u.currency_fav).first()

    balance, balances, symbol, notifications = pre_requisits()

    return render_template('users.html', title='Users', users=users, balance=balance, symbol=symbol, balances=balances, notifications=notifications)

# Método resposável pela ordem dos elementos do array eventos
def ord_events(e):
    return e.start_date

# Route para a página de gestão de eventos
@app.route("/allEvents", methods=['GET', 'POST'])
@login_required
def events():
    if current_user.role == "user":
        return redirect(url_for('home'))
    else:
        events = Event.query.all()
        events.sort(key=ord_events)

    balance, balances, symbol, notifications = pre_requisits()

    return render_template('allEvents.html', title='AllEvents', events=events, balance=balance, symbol=symbol, balances=balances, notifications=notifications)

# Route responsável por mudar o estado de um evento
@app.route("/allEvents/event/<event_id>/<status>")
@login_required
def event(event_id, status):
    if current_user.role == "user":
        return redirect(url_for('home'))
    else:
        event = Event.query.filter_by(id=event_id).first()
        event.state = str(status)
        
        db.session.commit()

        odds = Odd.query.filter_by(event_id=event_id).all()
        betodds = []
        for o in odds:
            betodds += BetOdd.query.filter_by(odd_id=o.id).all()

        for bo in betodds:
            bet = Bet.query.filter_by(id=bo.bet_id).first()

            if event.state == "0":
                change = True

                this_bet_odds = BetOdd.query.filter_by(bet_id=bet.id).all()
                this_odds = []
                for tbo in this_bet_odds:
                    this_odds += Odd.query.filter_by(id=tbo.odd_id).all()
                for to in this_odds:
                    if Event.query.filter_by(id=to.event_id).first().state != "0":
                        change = False

                if change:
                    bet.state = "Ativa"
                    notif = Notification(bet_id=bet.id, text=f'A sua aposta foi ativada', user_id=bet.user_id)
                    db.session.add(notif)
                    flash('Nova notificação', 'warning')
            if event.state == "1":
                    change = True
                    win = True

                    print(bet)

                    this_bet_odds = BetOdd.query.filter_by(bet_id=bet.id).all()
                    
                    this_odds = []
                    for tbo in this_bet_odds:
                        this_odds += Odd.query.filter_by(id=tbo.odd_id).all()
                    for to in this_odds:
                        if to.event_id != event.id:
                            if Event.query.filter_by(id=to.event_id).first().state != "2":
                                change = False
                        if to.result != None:
                            if to.result == False:
                                win = False

                    if change and win:
                        bet.state = "Ganha"

                        mov = Movement(value=bet.value*bet.odd,
                                       type="Aposta Ganha",
                                       date=datetime.now())
                        db.session.add(mov)

                        wallet = Wallet.query.filter_by(
                            user_id=bet.user_id, currency_id=bet.currency_id).first()

                        wm = WalletMovement(movement_id=mov.id,
                                            wallet_id=wallet.id)
                        db.session.add(wm)

                        wallet.balance += bet.value * bet.odd

                        notif = Notification(bet_id=bet.id, text=f'A sua aposta foi ganha e foram transferidos {bet.value * bet.odd} {Currency.query.filter_by(id=bet.currency_id).first().symbol}', user_id=bet.user_id)
                        db.session.add(notif)
                        flash('Nova notificação', 'warning')
                    elif change and not win:
                        bet.state = "Perdida"
                        notif = Notification(bet_id=bet.id, text=f'A sua aposta foi perdida', user_id=bet.user_id)
                        db.session.add(notif)
                        flash('Nova notificação', 'warning')
            elif event.state == "3":
                bet.state = "Suspensa"

                notif = Notification(bet_id=bet.id, text='A sua aposta foi suspensa', user_id=bet.user_id)
                db.session.add(notif)

                flash('Nova notificação', 'warning')
            elif event.state == "4":
                bet.state = "Cancelada"

                mov = Movement(value=bet.value,
                               type="Aposta Cancelada",
                               date=datetime.now())
                db.session.add(mov)

                wallet = Wallet.query.filter_by(
                    user_id=bet.user_id, currency_id=bet.currency_id).first()

                wm = WalletMovement(movement_id=mov.id,
                                    wallet_id=wallet.id)
                db.session.add(wm)

                wallet.balance += bet.value

                notif = Notification(bet_id=bet.id, text=f'A sua aposta foi cancelada e foram devolvidos {bet.value} {Currency.query.filter_by(id=bet.currency_id).first().symbol}', user_id=bet.user_id)
                db.session.add(notif)

                flash('Nova notificação', 'warning')

        db.session.commit()

        if status == "0":
            flash('Evento ativado com sucesso', 'success')
        elif status == "2":
            flash('Evento concluido com sucesso', 'success')
        elif status == "3":
            flash('Evento supenso com sucesso', 'success')
        elif status == "4":
            flash('Evento cancelado com sucesso', 'success')

        return redirect(url_for('events'))

# Route para a página de notificações
@app.route("/account/notifications")
@login_required
def notifications():
    balance, balances, symbol, notifications = pre_requisits()

    notif = Notification.query.filter_by(user_id=current_user.id).all()

    return render_template('notifications.html', notif=notif, balance=balance, symbol=symbol, balances=balances, notifications=notifications)

# Route para remover uma notificação
@app.route("/account/notifications/delete/<not_id>")
@login_required
def notification_delete(not_id):
    notif = Notification.query.filter_by(id=not_id).first()
    db.session.delete(notif)
    db.session.commit()
    return redirect(url_for('notifications'))