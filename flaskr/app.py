from flaskr import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

USER_DB = 'root'
PASS_DB = ''
URL_DB = 'localhost'
NAME_DB = 'phphone'
FULL_URL_DB = f'mysql+pymysql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'

app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate= Migrate()
migrate.init_app(app, db)