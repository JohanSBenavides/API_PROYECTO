import os
from flask import Flask, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required
from flask_cors import CORS
from werkzeug.utils import secure_filename

from .modelos.modelo import db
from werkzeug.security import generate_password_hash
from .vistas.vistas import (
    VistaUsuario, VistaProductos, VistaProducto, VistaTarjeta, VistaPaypal, VistaTransferencia, VistaProductosRecomendados,VistaCategorias, VistaCategoria, VistaUsuarios, VistaLogin, VistaSignIn, 
    VistaCarrito, VistaCarritos, VistaDetalleFactura, VistaDetalleFacturas, VistaCarritoActivo, VistaRolUsuario,
    VistaEnvio, VistaEnvios, VistaFactura, VistaFacturas, VistaOrden, VistaOrdenes, VistaPago, VistaPerfilUsuario
)

def create_app(config_name='default'):
    app = Flask(__name__)

    # Configuración de la base de datos MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/phphone'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuración para la subida de imágenes
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')  # Ruta de las imágenes
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Extensiones permitidas

    # Asegurarse de que la carpeta de subidas existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Ruta para servir las imágenes desde el servidor
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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

    # Rutas para usuarios, productos, categorías, etc.
    api.add_resource(VistaUsuario, '/usuario/<int:id_usuario>')
    api.add_resource(VistaUsuarios, '/usuarios')
    api.add_resource(VistaProducto, '/productos/<int:id_producto>')
    api.add_resource(VistaProductos, '/productos')
    api.add_resource(VistaCategoria, '/categoria/<int:id_categoria>')
    api.add_resource(VistaCategorias, '/categorias')
    api.add_resource(VistaLogin, '/login')
    api.add_resource(VistaSignIn, '/signin')
    api.add_resource(VistaCarritos, '/carritos')
    # Ruta para obtener o crear un carrito
    api.add_resource(VistaCarrito, '/carrito', endpoint='vista_carrito')
    # Ruta para manejar productos dentro de un carrito específico
    api.add_resource(VistaCarrito, '/carrito/<int:id_carrito>/producto', endpoint='vista_carrito_producto')
    # Ruta para obtener o eliminar un carrito específico
    api.add_resource(VistaCarrito, '/carrito/<int:id_carrito>', endpoint='vista_carrito_detalle')
    #OBTENER CARRITO ACTIVO
    api.add_resource(VistaCarritoActivo, '/carrito/activo', endpoint='vista_carrito_activo')


    api.add_resource(VistaFacturas, '/factura')
    api.add_resource(VistaFactura, '/factura/<int:id_factura>')
    api.add_resource(VistaOrdenes, '/orden')
    api.add_resource(VistaOrden, '/orden/<int:id_orden>')
    api.add_resource(VistaDetalleFacturas, '/detalle_factura')
    api.add_resource(VistaDetalleFactura, '/detalle_factura/<int:id_detalle_factura>')
    api.add_resource(VistaEnvios, '/envio')
    api.add_resource(VistaEnvio, '/envio/<int:id_envio>')
    api.add_resource(VistaPago, '/pago')
    api.add_resource(VistaTarjeta, '/pago/tarjeta')
    api.add_resource(VistaTransferencia, '/pago/transferencia')
    api.add_resource(VistaPaypal, '/pago/paypal')
    api.add_resource(VistaPerfilUsuario, '/perfil')
    api.add_resource(VistaRolUsuario, '/usuario/rol')
    api.add_resource(VistaProductosRecomendados, '/productos/recomendados')




    return app