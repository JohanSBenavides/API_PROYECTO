from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/phphone'  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    app.config['FLASK_RUN_PORT'] = 5001
    
    db.init_app(app)  
    
    return app
