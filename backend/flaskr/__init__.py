from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .modelos.modelo import db
from werkzeug.security import generate_password_hash
from .vistas.vistas import (
    VistaUsuario, VistaProductos, VistaProducto, VistaCategorias, VistaCategoria, VistaUsuarios, VistaLogin, VistaSignIn
)


def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Configuración de la base de datos MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/phphone'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicialización de la base de datos y migración
    db.init_app(app)
    migrate = Migrate(app, db)  # Inicializa Flask-Migrate

    # Configuración de JWT
    app.config['JWT_SECRET_KEY'] = 'clave_secreta'  # Cambia esto por una clave más segura
    jwt = JWTManager(app)  # Inicializa JWT para autenticar las peticiones

    # Habilita CORS para permitir solicitudes de otros dominios
    CORS(app)

    # Inicialización de las vistas
    api = Api(app)
    api.add_resource(VistaUsuario, '/usuario/<int:id_usuario>')
    api.add_resource(VistaProducto, '/producto/<int:id_producto>')
    api.add_resource(VistaCategoria, '/categoria/<int:id_categoria>')

    # Rutas para ver todos y añadir
    api.add_resource(VistaUsuarios, '/usuarios')
    api.add_resource(VistaProductos, '/productos')
    api.add_resource(VistaCategorias, '/categorias')

    # Rutas para login e iniciar sesión
    api.add_resource(VistaLogin, '/login')
    api.add_resource(VistaSignIn, '/signin')

    return app
