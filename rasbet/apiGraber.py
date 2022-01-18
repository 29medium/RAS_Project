import json
from rasbet.models import *
from rasbet import db, bcrypt
from datetime import datetime, timedelta
import time

# script que atualiza desportos,competições, intervenientes e eventos na base de dados
# executada aquando da inicialização da app
def loadApi():
    f = open('rasbet/files/API.json','r')
    data = json.load(f)
    for desporto in data['Desportos']:        
        # desporto
        desp = Sport.query.filter_by(id=desporto['id']).first()
        if not desp:
            novo = Sport(id=desporto['id'],name=desporto['name'])
            db.session.add(novo)
            
        for competicao in desporto['competicoes']:
            comp = Competition.query.filter_by(id=competicao['id']).first()
            if not comp:
                novo = Competition(id=competicao['id'],name=competicao['name'],sport_id=desporto['id'])
                db.session.add(novo)    
                

        for interveniente in desporto['intervenientes']:
            part = Participant.query.filter_by(id=interveniente['id']).first()
            if not part:
                novo = Participant(id=interveniente['id'],name=interveniente['name'])
                db.session.add(novo)
                
        
        for evento in desporto['eventos']:
            event = Event.query.filter_by(id=evento['id']).first()
            if not event:
                start_date = datetime.strptime(evento['data'],'%Y-%m-%d %H:%M')
                if start_date > datetime.now():
                    state = 0
                elif start_date + timedelta(minutes=1) < datetime.now():
                    state = 2
                else:
                    state = 1
                novo = Event(id=evento['id'],name=evento['name'],competition_id=evento['competicao'],start_date=start_date,end_date = start_date + timedelta(minutes=1), state=str(state)) # falta result
                db.session.add(novo)
            

            for participant in evento['intervenientes']:
                if ((datetime.now() > datetime.strptime(evento['data'],'%Y-%m-%d %H:%M')) and (datetime.now() < datetime.strptime(evento['data'],'%Y-%m-%d %H:%M') + timedelta(minutes=1))):
                    odd_resultado = Odd.query.filter_by(event_id=evento['id'], participant_id=participant).first()
                    if odd_resultado and not odd_resultado.result:
                        if evento['resultado'] == -1:
                            odd_resultado.result = False
                            odd_empate = Odd.query.filter_by(event_id=event.id, participant_id=None).first()
                            if odd_empate and not odd_empate.result:
                                odd_empate.result = True
                        elif evento['resultado'] == participant.id:
                            odd_resultado.result = True
                            odd_empate = Odd.query.filter_by(event_id=event.id, participant_id=None).first()
                            if odd_empate and not odd_resultado.result:
                                odd_empate.result = False
                        else:
                            odd_resultado.result = False
                            odd_empate = Odd.query.filter_by(event_id=event.id, participant_id=None).first()
                            if odd_empate and not odd_resultado.result:
                                odd_empate.result = False
            

            if len(evento['odds']) == len(evento['intervenientes']):
                i = 0
                for odd in evento['odds']:
                    t = Odd.query.filter_by(participant_id=evento['intervenientes'][i],event_id=evento['id']).first()
                    if not t:
                        novo = Odd(value=odd,participant_id=evento['intervenientes'][i],event_id=evento['id'])
                        db.session.add(novo)
                    else:
                        t.value = odd
                    i+=1
            else:
                t = Odd.query.filter_by(participant_id=evento['intervenientes'][0],event_id=evento['id']).first()
                if not t:
                    novo = Odd(value=evento['odds'][0],participant_id=evento['intervenientes'][0],event_id=evento['id'])
                    db.session.add(novo)
                else:
                    t.value = evento['odds'][0]
                    
                t = Odd.query.filter_by(participant_id=None,event_id=evento['id']).first()
                if not t:
                    novo = Odd(value=evento['odds'][1],participant_id=None,event_id=evento['id'])
                    db.session.add(novo)
                else:
                    t.value=evento['odds'][1]
                
                t = Odd.query.filter_by(participant_id=evento['intervenientes'][1],event_id=evento['id']).first()
                if not t:
                    novo = Odd(value=evento['odds'][2],participant_id=evento['intervenientes'][1],event_id=evento['id'])
                    db.session.add(novo)
                else:
                    t.value = evento['odds'][2]
                    
    db.session.commit()
    
# script que atualiza as currency's através de um ficheiro json
def loadCurr():
    f = open('rasbet/files/Currency.json','r')
    data = json.load(f)
    for cur in data['Currency']:
        c = Currency.query.filter_by(id=cur['id']).first()
        if not c:
            novo = Currency(id=cur['id'],name=cur['name'],symbol=cur['symbol'],convertion_rate=cur['taxa']) 
            db.session.add(novo)
        else:
            c.conversion_rate=cur['taxa']
                    
    db.session.commit()

# script que atualiza tudo que tenha a haver com eventos
def loadApiWorker():
    f = open('rasbet/files/API.json','r')
    data = json.load(f)
    for desporto in data['Desportos']:
    
        for evento in desporto['eventos']:
            event = Event.query.filter_by(id=evento['id']).first()
            if not event:
                start_date = datetime.strptime(evento['data'],'%Y-%m-%d %H:%M')
                if start_date > datetime.now():
                    state = 0
                elif start_date + timedelta(minutes=1) < datetime.now():
                    state = 2
                else:
                    state = 1
                novo = Event(id=evento['id'],name=evento['name'],competition_id=evento['competicao'],start_date=start_date,end_date = start_date + timedelta(minutes=1) ,state=str(state)) # falta result
                db.session.add(novo)
            

            for participant in evento['intervenientes']:
                if ((datetime.now() > datetime.strptime(evento['data'],'%Y-%m-%d %H:%M')) and (datetime.now() < datetime.strptime(evento['data'],'%Y-%m-%d %H:%M') + timedelta(minutes=1))):
                    odd_resultado = Odd.query.filter_by(event_id=evento['id'], participant_id=participant).first()
                    if odd_resultado and not odd_resultado.result:
                        if evento['resultado'] == -1:
                            odd_resultado.result = False
                            odd_empate = Odd.query.filter_by(event_id=event.id, participant_id=None).first()
                            if odd_empate and not odd_resultado.result:
                                odd_empate.result = True
                        elif evento['resultado'] == participant.id:
                            odd_resultado.result = True
                            odd_empate = Odd.query.filter_by(event_id=event.id, participant_id=None).first()
                            if odd_empate and not odd_resultado.result:
                                odd_empate.result = False
                        else:
                            odd_resultado.result = False
                            odd_empate = Odd.query.filter_by(event_id=event.id, participant_id=None).first()
                            if odd_empate and not odd_resultado.result:
                                odd_empate.result = False
                
                
            if len(evento['odds']) == len(evento['intervenientes']):
                i = 0
                for odd in evento['odds']:
                    t = Odd.query.filter_by(participant_id=evento['intervenientes'][i],event_id=evento['id']).first()
                    if not t:
                        novo = Odd(value=odd,participant_id=evento['intervenientes'][i],event_id=evento['id'])
                        db.session.add(novo)
                    else:
                        t.value=odd

                    i+=1
            else:
                t = Odd.query.filter_by(participant_id=evento['intervenientes'][0],event_id=evento['id']).first()
                if not t:
                    novo = Odd(value=evento['odds'][0],participant_id=evento['intervenientes'][0],event_id=evento['id'])
                    db.session.add(novo)
                else:
                    t.value=evento['odds'][0]
                    
                t = Odd.query.filter_by(participant_id=None,event_id=evento['id']).first()
                if not t:
                    novo = Odd(value=evento['odds'][1],participant_id=None,event_id=evento['id'])
                    db.session.add(novo)
                else:
                    t.value=evento['odds'][1]

                t = Odd.query.filter_by(participant_id=evento['intervenientes'][1],event_id=evento['id']).first()
                if not t:
                    novo = Odd(value=evento['odds'][2],participant_id=evento['intervenientes'][1],event_id=evento['id'])
                    db.session.add(novo)
                else:
                    t.value=evento['odds'][2]
    db.session.commit()

# função executada por uma thread para atualizar constantemente os dados
def worker():
    while True:
        time.sleep(10)
        loadApiWorker()
        loadCurr()
    
# função que é executada aquando da inicialização da app
def loadAllApi():
    loadApi()
    loadCurr()

    user = User.query.filter_by(username="admin").first()
    if not user:
        hashed_password = bcrypt.generate_password_hash("admin").decode('utf-8')
        admin = User(username="admin",
                    name="admin",
                    email="admin@test.com", 
                    password=hashed_password,
                    birth_date= datetime.strptime("2000-01-02", "%Y-%m-%d"),
                    nif="123456789",
                    cc="12345678",
                    iban="1234567890123456789012345",
                    address="Rua do Administrador",
                    phone="123456789",
                    currency_fav=0,
                    role="admin")
        db.session.add(admin)

        currencies = Currency.query.all()
        for cur in currencies:
            wallet = Wallet(balance=0.0, user_id=admin.id, currency_id=cur.id)
            db.session.add(wallet)

        bet = Bet(state="Rascunho", odd=1, user_id=admin.id)
        db.session.add(bet)
        db.session.commit()