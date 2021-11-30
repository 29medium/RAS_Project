from flask import Flask
import mysql.connector
from mysql.connector import errorcode

def execute_querie(add, data):
    try:
        config = {
            "user" : "root",
            "passwd" : "root",
            "database" : "rasbet",
            "host" : "127.0.0.1",
            "port" : "3306",
            "raise_on_warnings" : True
        }

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute(add, data)
        cnx.commit()
        cnx.close()
        cursor.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
   

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ABC'

    from .views import views
    from .auth import auth
    
    app.register_blueprint(views,url_prefix="/")
    app.register_blueprint(auth,url_prefix="/")

    return app