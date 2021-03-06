import imp
import threading

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '95b85e666378c85ba5812822d1ff0527'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rasbet.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'success'

from rasbet.models import *
db.create_all()
db.session.commit()

from rasbet.apiGraber import worker,loadAllApi

loadAllApi()

workerThread = threading.Thread(target=worker)
workerThread.daemon = True
workerThread.start()

from rasbet.stateThread import worker

stateThread = threading.Thread(target=worker)
stateThread.daemon = True
stateThread.start()

import rasbet.routes