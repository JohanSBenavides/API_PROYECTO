from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import enum
# Inicialización de la base de datos
db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100))
    numerodoc = db.Column(db.Integer)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena_hash = db.Column('contrasena_hash', db.String(255))
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.rol_id'))

    @property
    def contrasena(self):
        raise AttributeError("La contraseña no es un atributo legible.")

    @contrasena.setter
    def contrasena(self, password):
        if not password.strip():
            raise ValueError("La contraseña no puede estar vacía.")
        self.contrasena_hash = generate_password_hash(password)

    def verificar_contrasena(self, password):
        return check_password_hash(self.contrasena_hash, password)


class Rol(db.Model):
    __tablename__ = 'rol'
    rol_id = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50))


class Categoria(db.Model):
    __tablename__ = 'categoria'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))


class Producto(db.Model):
    __tablename__ = 'producto'
    id_producto = db.Column(db.Integer, primary_key=True)
    producto_nombre = db.Column(db.String(100))
    producto_precio = db.Column(db.Integer)
    producto_stock = db.Column(db.Integer, default=0)  # Stock inicial en 0
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'))
    descripcion = db.Column(db.String(255))
    producto_foto = db.Column(db.String(255))


class Carrito(db.Model):
    __tablename__ = 'carrito'
    id_carrito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    fecha = db.Column(db.DateTime, default=db.func.now())  # Fecha automática
    total = db.Column(db.Integer, nullable=False, default=0)
    procesado = db.Column(db.Boolean, default=False)  # Indica si el carrito fue confirmado


class DetalleCarrito(db.Model):
    __tablename__ = 'detalle_carrito'
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_carrito = db.Column(db.Integer, db.ForeignKey('carrito.id_carrito'))
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'))
    cantidad = db.Column(db.Integer, nullable=False)


class Orden(db.Model):
    __tablename__ = 'orden'
    id_orden = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    fecha_orden = db.Column(db.DateTime, default=db.func.now())
    monto_total = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Enum('pendiente', 'procesando', 'pagada', 'enviada', 'cancelada', name='estado_orden'), default='pendiente')


class Factura(db.Model):
    __tablename__ = 'factura'
    id_factura = db.Column(db.Integer, primary_key=True)
    id_orden = db.Column(db.Integer, db.ForeignKey('orden.id_orden'))
    factura_fecha = db.Column(db.DateTime, default=db.func.now())
    monto_total = db.Column(db.Integer, nullable=False)


class DetalleFactura(db.Model):
    __tablename__ = 'detalle_factura'
    id_detalle_factura = db.Column(db.Integer, primary_key=True)
    id_factura = db.Column(db.Integer, db.ForeignKey('factura.id_factura'))
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'))
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Integer, nullable=False)


class Pago(db.Model):
    __tablename__ = 'pago'
    id_pago = db.Column(db.Integer, primary_key=True)
    id_orden = db.Column(db.Integer, db.ForeignKey('orden.id_orden'))
    monto = db.Column(db.Integer, nullable=False)
    fecha_pago = db.Column(db.DateTime, default=db.func.now())
    metodo_pago = db.Column(db.Enum('tarjeta', 'paypal', 'transferencia', name='metodo_pago'))
    estado = db.Column(db.Enum('pendiente', 'completado', 'rechazado', name='estado_pago'), default='pendiente')


class Envio(db.Model):
    __tablename__ = 'envio'
    id_envio = db.Column(db.Integer, primary_key=True)
    id_orden = db.Column(db.Integer, db.ForeignKey('orden.id_orden'))
    direccion = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.now())




        