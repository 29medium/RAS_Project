import json
from rasbet.models import *
from rasbet import db
from datetime import datetime
import time

def loadApi():
    f = open('rasbet/files/API.json','r')
    data = json.load(f)
    for desporto in data['Desportos']:        
        # desporto
        desp = Sport.query.filter_by(id=desporto['id']).first()
        if not desp:
            novo = Sport(id=desporto['id'],name=desporto['name'])
            db.session.add(novo)
            db.session.commit()
         

        for competicao in desporto['competicoes']:
            comp = Competition.query.filter_by(id=competicao['id']).first()
            if not comp:
                novo = Competition(id=competicao['id'],name=competicao['name'],sport_id=desporto['id'])
                db.session.add(novo)    
                db.session.commit()

        for interveniente in desporto['intervenientes']:
            part = Participant.query.filter_by(id=interveniente['id']).first()
            if not part:
                novo = Participant(id=interveniente['id'],name=interveniente['name'])
                db.session.add(novo)
                db.session.commit()
        
        for evento in desporto['eventos']:
            event = Event.query.filter_by(id=evento['id']).first()
            if not event:
                novo = Event(id=evento['id'],name=evento['name'],competition_id=evento['competicao'],start_date=datetime.strptime(evento['data'],'%Y-%m-%d').date(),state=evento['status']) # falta result
                db.session.add(novo)
            else:
                event.state = evento['status']
            db.session.commit()

            for participant in evento['intervenientes']:
                if (datetime.now().date() < datetime.strptime(evento['data'],'%Y-%m-%d').date()):
                    result = -2
                elif evento['status'] == 2:
                    if evento['resultado'] == -1:
                        result = 0
                    elif evento['resultado'] == participant:
                        result = 1
                    else:
                        result = -1
                
                db.session.commit()

            if len(evento['odds']) == len(evento['intervenientes']):
                i = 0
                for odd in evento['odds']:
                    novo = Odd(value=odd,participant_id=evento['intervenientes'][i],event_id=evento['id'])
                    db.session.add(novo)
                    db.session.commit()
                    i+=1
            else:
                novo = Odd(value=evento['odds'][0],participant_id=evento['intervenientes'][0],event_id=evento['id'])
                db.session.add(novo)
                db.session.commit()
                novo = Odd(value=evento['odds'][1],participant_id=None,event_id=evento['id'])
                db.session.add(novo)
                db.session.commit()
                novo = Odd(value=evento['odds'][2],participant_id=evento['intervenientes'][1],event_id=evento['id'])
                db.session.add(novo)
                db.session.commit()

    

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


def loadApiWorker():
    f = open('rasbet/files/API.json','r')
    data = json.load(f)
    for desporto in data['Desportos']:
    
        for evento in desporto['eventos']:
            event = Event.query.filter_by(id=evento['id']).first()
            if not event:
                novo = Event(id=evento['id'],name=['name'],competition_id=evento['competicao'],start_date=evento['data'],state=evento['status']) # falta result
                db.session.add(novo)
            else:
                event.state = evento['status']
            db.session.commit()

            for participant in evento['intervenientes']:
                if (datetime.now().date() < datetime.strptime(evento['data'],'%Y-%m-%d').date()):
                    result = -2
                elif evento['status'] == 2:
                    if evento['resultado'] == -1:
                        result = 0
                    elif evento['resultado'] == participant:
                        result = 1
                    else:
                        result = -1
                
                db.session.commit()

            if len(evento['odds']) == len(evento['intervenientes']):
                i = 0
                for odd in evento['odds']:
                    novo = Odd(value=odd,participant_id=evento['intervenientes'][i],event_id=evento['id'])
                    db.session.add(novo)
                    db.session.commit()
                    i+=1
            else:
                novo = Odd(value=evento['odds'][0],participant_id=evento['intervenientes'][0],event_id=evento['id'])
                db.session.add(novo)
                db.session.commit()
                novo = Odd(value=evento['odds'][1],participant_id=None,event_id=evento['id'])
                db.session.add(novo)
                db.session.commit()
                novo = Odd(value=evento['odds'][2],participant_id=evento['intervenientes'][1],event_id=evento['id'])
                db.session.add(novo)
                db.session.commit()
    
def worker():
    while True:
        time.sleep(10)
        loadApiWorker()
        loadCurr()
    
def loadAllApi():
    loadApi()
    loadCurr()