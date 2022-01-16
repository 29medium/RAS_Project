import time
from rasbet.models import *
from rasbet import db
from datetime import datetime

def stateChanger():
    events = Event.query.all()
    for e in events:
        if e.start_date < datetime.now() and e.state==0:
            e.state = 1
        elif e.end_date < datetime.now() and e.state==1:
            e.state = 2
            db.session.commit()

            odds = Odd.query.filter_by(event_id=e.id).all()
            betodds = []

            for o in odds:
                betodds += BetOdd.query.filter_by(odd_id=o.id).all()

            for bo in betodds:
                bet = Bet.query.filter_by(id=bo.bet_id).first()
                change = True

                this_bet_odds = Bet.query.filter_by(bet_id=bet.id).all()
                this_odds = []
                for tbo in this_bet_odds:
                    this_odds += Odd.query.filter_by(id=tbo.odd_id).all()
                for to in this_odds:
                    if Event.query.filter_by(id=to.event_id).first().state != 2:
                        change = False 

                if change:
                    bet.state = "Concluida"

                    mov = Movement(value=bet.value*bet.odd,
                                   type="Aposta Concluida",
                                   date=datetime.now())
                    db.session.add(mov)

                    wallet = Wallet.query.filter_by(user_id=bet.user_id, currency_id=bet.currency_id).first()

                    wm = WalletMovement(movement_id=mov.id,
                            wallet_id=wallet.id)
                    db.session.add(wm)

                    wallet.balance += bet.value * bet.odd
                
    db.session.commit()

def worker():
    while True:
        time.sleep(10)
        stateChanger()