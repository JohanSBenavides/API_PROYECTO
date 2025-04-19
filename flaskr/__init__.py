import os
from flask import Flask, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask_mail import Mail  # <--- importamos Mail

from .modelos.modelo import db
from werkzeug.security import generate_password_hash
from .vistas.vistas import (
    VistaUsuario, VistaProductos, VistaProducto, VistaTarjeta, VistaPaypal, VistaTransferencia, VistaProductosRecomendados,
    VistaCategorias, VistaCategoria, VistaUsuarios, VistaLogin, VistaSignIn, 
    VistaCarrito, VistaCarritos, VistaCarritoActivo, VistaRolUsuario,
    VistaPago, VistaPerfilUsuario, VistaFactura, VistaDetalleFactura,VistaEnvio
)

# ✅ Creamos mail a nivel global
mail = Mail()

def create_app(config_name='default'):
    app = Flask(__name__)

    # Configuración de la base de datos MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/phphone'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuración para la subida de imágenes
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Inicialización de la base de datos y migración
    db.init_app(app)
    migrate = Migrate(app, db)

    # Configuración de JWT
    app.config['JWT_SECRET_KEY'] = 'clave_secreta'
    jwt = JWTManager(app)

    # ✅ Configuración de Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_DEBUG'] = True
    app.config['MAIL_USERNAME'] = 'dilanf1506@gmail.com'
    app.config['MAIL_PASSWORD'] = 'zycb icwa fxby yocj'
    app.config['MAIL_DEFAULT_SENDER'] = 'dilanf1506@gmail.com'

    mail.init_app(app)  # ✅ Inicializamos el objeto mail con la app

    CORS(app)

    # Rutas de la API
    api = Api(app)
    api.add_resource(VistaUsuario, '/usuario/<int:id_usuario>')
    api.add_resource(VistaUsuarios, '/usuarios')
    api.add_resource(VistaProducto, '/productos/<int:id_producto>')
    api.add_resource(VistaProductos, '/productos')
    api.add_resource(VistaCategoria, '/categoria/<int:id_categoria>')
    api.add_resource(VistaCategorias, '/categorias')
    api.add_resource(VistaLogin, '/login')
    api.add_resource(VistaSignIn, '/signin')
    api.add_resource(VistaCarritos, '/carritos')
    api.add_resource(VistaCarrito, '/carrito', endpoint='vista_carrito')
    api.add_resource(VistaCarrito, '/carrito/<int:id_carrito>/producto', endpoint='vista_carrito_producto')
    api.add_resource(VistaCarrito, '/carrito/<int:id_carrito>', endpoint='vista_carrito_detalle')
    api.add_resource(VistaCarritoActivo, '/carrito/activo', endpoint='vista_carrito_activo')
    api.add_resource(VistaPago, '/pago')
    api.add_resource(VistaTarjeta, '/pago/tarjeta')
    api.add_resource(VistaTransferencia, '/pago/transferencia')
    api.add_resource(VistaPaypal, '/pago/paypal')
    api.add_resource(VistaPerfilUsuario, '/perfil')
    api.add_resource(VistaRolUsuario, '/usuario/rol')
    api.add_resource(VistaProductosRecomendados, '/productos/recomendados')
    api.add_resource(VistaFactura, '/factura')
    api.add_resource(VistaDetalleFactura, '/detallefactura')
    api.add_resource(VistaEnvio, '/envio')

    return app
