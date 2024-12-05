from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .modelos.modelos import db

def create_app(config_name='default'):

    app = Flask(__name__)
    #configuracion de la bd
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/phphone'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    app.config["JWT_SECRET_KEY"] = 'clavesecreta'
    jwt = JWTManager(app)

    CORS(app)
    
    app.config['FLASK_RUN_PORT'] = 3306
    return app
