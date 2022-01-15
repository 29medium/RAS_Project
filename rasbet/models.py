from datetime import datetime
from rasbet import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    birth_date = db.Column(db.DateTime, nullable = False)
    nif = db.Column(db.String(9), unique = True, nullable = False)
    cc = db.Column(db.String(8), unique = True, nullable = False)
    iban = db.Column(db.String(25), nullable = False)
    address = db.Column(db.String(100), nullable = False)
    phone = db.Column(db.String(15), unique=True, nullable = False)
    role = db.Column(db.String(20), unique = False)
    currency_fav = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    wallet = db.relationship("Wallet")
    bets = db.relationship("Bet")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    balance = db.Column(db.Float, unique = False, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    wm = db.relationship("WalletMovement")

    def __repr__(self):
        return f"Wallet('{self.balance}', '{self.user_id}')"

class Currency(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(20), unique = False, nullable = False)
    symbol = db.Column(db.String(10), unique = True, nullable = False)
    convertion_rate = db.Column(db.Float, nullable = False)
    wallets = db.relationship("Wallet")
    users = db.relationship("User")

    def __repr__(self):
        return f"Currency('{self.name}', '{self.conversion_rate}')"

class Movement(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    value = db.Column(db.Float, unique = False, nullable = False)
    type = db.Column(db.String(20), unique = False, nullable = False)
    date = db.Column(db.DateTime, nullable = False)
    wm = db.relationship("WalletMovement")

    def __repr__(self):
        return f"Movement('{self.value}', '{self.type}', '{self.date})"

class WalletMovement(db.Model):
    movement_id = db.Column(db.Integer, db.ForeignKey('movement.id'), primary_key=True, nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id' ), primary_key=True, nullable=False)

    def __repr__(self):
        return f"WalletMovement('{self.movement_id}', '{self.wallet_id}')"

class Bet(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    value = db.Column(db.Float, unique = False, nullable = False)
    state = db.Column(db.String(20), unique = False, nullable = False)
    date = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id' ), nullable=False)
    bo = db.relationship("BetOdd")

    def __repr__(self):
        return f"Bet('{self.value}', '{self.state}', '{self.user_id}')"

class BetOdd(db.Model):
    bet_id = db.Column(db.Integer, db.ForeignKey('bet.id' ), primary_key=True, nullable=False)
    odd_id = db.Column(db.Integer, db.ForeignKey('odd.id' ), primary_key=True, nullable=False)

    def __repr__(self):
        return f"BetOdd('{self.bet_id}', '{self.odd_id}')"

class Odd(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    value = db.Column(db.Float, unique = False, nullable = False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id' ), nullable = True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id' ), nullable=False)
    bo = db.relationship("BetOdd")

    def __repr__(self):
        return f"Odd('{self.value}', '{self.participant_id}', '{self.event_id}')"

class Event(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.DateTime, nullable = False)
    state = db.Column(db.String(20), unique = False, nullable = False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id' ), nullable=False)
    odds = db.relationship("Odd")

    def __repr__(self):
        return f"Event('{self.name}', '{self.start_date}')"

class Competition(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(120), unique = False, nullable = False)
    sport_id = db.Column(db.Integer, db.ForeignKey('sport.id' ), nullable=False)
    events = db.relationship("Event")

    def __repr__(self):
        return f"Competition('{self.name}', '{self.sport_id}')"

class Sport(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(120), unique = True, nullable = False)
    competitions = db.relationship("Competition")
    
    def __repr__(self):
        return f"Sport('{self.id}', '{self.name}')"

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(120), unique = True, nullable = False)
    odds = db.relationship("Odd")

    def __repr__(self):
        return f"Participant('{self.id}', '{self.name}')"