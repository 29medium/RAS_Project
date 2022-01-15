from datetime import datetime
from rasbet import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
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

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
