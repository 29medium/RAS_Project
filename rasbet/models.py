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
    wallet = db.relationship("Wallet")
    bets = db.relationship("Bet")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    balance = db.Column(db.Float, unique = False, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id', ondelete='CASCADE'), nullable=False)
    wm = db.relationship("WalletMovement")

    def __repr__(self):
        return f"Wallet('{self.balance}', '{self.user_id}')"

class Currency(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(20), unique = False, nullable = False)
    conversion_rate = db.Column(db.Float, nullable = False)
    wallets = db.relationship("Wallet")

    def __repr__(self):
        return f"Currency('{self.name}', '{self.conversion_rate}')"

class Movement(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    value = db.Column(db.Float, unique = False, nullable = False)
    type = db.Column(db.String(20), unique = False, nullable = False)
    date = db.Column(db.DateTime, nullable = False)
    wm = db.relationship("WalletMovement")

class WalletMovement(db.Model):
    movement_id = db.Column(db.Integer, db.ForeignKey('movement.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id', ondelete='CASCADE'), primary_key=True, nullable=False)

class Bet(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    value = db.Column(db.Float, unique = False, nullable = False)
    state = db.Column(db.String(20), unique = False, nullable = False)
    date = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    bo = db.relationship("BetOdd")

class BetOdd(db.Model):
    bet_id = db.Column(db.Integer, db.ForeignKey('bet.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    odd_id = db.Column(db.Integer, db.ForeignKey('odd.id', ondelete='CASCADE'), primary_key=True, nullable=False)

class Odd(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    value = db.Column(db.Float, unique = False, nullable = False)
    description = db.Column(db.String(20), unique = False, nullable = False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id', ondelete='CASCADE'), nullable=False)
    bo = db.relationship("BetOdd")

class Event(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    start_date = db.Column(db.DateTime, nullable = False)
    end_date = db.Column(db.DateTime, nullable = False)
    state = db.Column(db.String(20), unique = False, nullable = False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id', ondelete='CASCADE'), nullable=False)
    odds = db.relationship("Odd")
    ep = db.relationship("ParticipantEvent")

class Competition(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(120), unique = False, nullable = False)
    sport_id = db.Column(db.Integer, db.ForeignKey('sport.id', ondelete='CASCADE'), nullable=False)
    events = db.relationship("Event")
    pc = db.relationship("ParticipantCompetition")

class Sport(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(120), unique = True, nullable = False)
    competitions = db.relationship("Competition")
    
    def __repr__(self):
        return f"Sport('{self.id}', '{self.name}')"

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(120), unique = True, nullable = False)
    pc = db.relationship("ParticipantCompetition")
    pe = db.relationship("ParticipantEvent")

class ParticipantCompetition(db.Model):
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id', ondelete='CASCADE'), primary_key=True, nullable=False)

class ParticipantEvent(db.Model):
    event_id = db.Column(db.Integer, db.ForeignKey('event.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    result = db.Column(db.Integer, nullable=False)