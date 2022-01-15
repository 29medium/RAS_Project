import json

def loadApi(db):
    f = open('API.json','r')
    data = json.load(f)
    for desporto in data['Desportos']:
        print('searching for ... ' + desporto['nome'])
        desp = Desporto.query.filter_by(id=desporto['id']).first()
        if desp:
            novo = Desporto(id=desporto['id'])
            db.session.add(novo)
            db.session.commit()
            pass
        else:
            print("não existe table para " + desporto['nome'])
        #print(desporto['nome'])
