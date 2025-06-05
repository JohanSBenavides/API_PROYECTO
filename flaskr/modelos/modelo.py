from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    numerodoc = db.Column(db.Integer, nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(255))
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.rol_id'))

    # Relación con Rol
    rol = db.relationship('Rol', back_populates='usuarios')  
    
    carritos = db.relationship('Carrito', back_populates='usuario')
    envios = db.relationship('Envio', back_populates='usuario', cascade='all, delete-orphan')

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
    nombre_rol = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relación con Usuario
    usuarios = db.relationship('Usuario', back_populates='rol')

    def __init__(self, nombre_rol=None):
        if nombre_rol is None:
            raise ValueError("El nombre del rol es obligatorio")
        if len(nombre_rol) > 50:
            raise ValueError("El nombre del rol no puede exceder los 50 caracteres")
        self.nombre_rol = nombre_rol


class Categoria(db.Model):
    __tablename__ = 'categoria'

    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)


class Producto(db.Model):
    __tablename__ = 'producto'

    id_producto = db.Column(db.Integer, primary_key=True)
    producto_nombre = db.Column(db.String(100), nullable=False)
    producto_precio = db.Column(db.Integer, nullable=False)
    producto_stock = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    producto_foto = db.Column(db.String(100), nullable=False)
    categoria_id = db.Column(db.Integer, nullable=False)

    carritos = db.relationship('CarritoProducto', back_populates='producto')
    
    def ajustar_stock(self, cantidad_entrada, motivo=None):
        """Registra una entrada de stock y actualiza el historial"""
        if cantidad_entrada <= 0:
            raise ValueError("La cantidad de entrada debe ser un número positivo")
        
        # Registrar el stock actual antes del ajuste
        stock_actual = self.producto_stock
        
        # Actualizar el stock del producto
        self.producto_stock += cantidad_entrada
        
        # Crear registro en el historial
        nuevo_registro = HistorialStock(
            id_producto=self.id_producto,
            stock_anterior=stock_actual,
            cantidad_ajuste=cantidad_entrada,
            nuevo_stock=self.producto_stock,
            motivo=motivo
        )
        
        db.session.add(nuevo_registro)
        return nuevo_registro


class HistorialStock(db.Model):
    __tablename__ = 'historial_stock'

    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)
    stock_anterior = db.Column(db.Integer, nullable=False)
    cantidad_ajuste = db.Column(db.Integer, nullable=False)
    nuevo_stock = db.Column(db.Integer, nullable=False)
    fecha_ajuste = db.Column(db.DateTime, default=db.func.now())
    motivo = db.Column(db.String(255))
    
    producto = db.relationship('Producto', backref='historial_stocks')


class Carrito(db.Model):
    __tablename__ = 'carrito'

    id_carrito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.now())
    total = db.Column(db.Integer, nullable=False, default=0)
    procesado = db.Column(db.Boolean, default=False)

    usuario = db.relationship('Usuario', back_populates='carritos')
    productos = db.relationship('CarritoProducto', back_populates='carrito', cascade="all, delete-orphan")


class CarritoProducto(db.Model):
    __tablename__ = 'carrito_producto'

    id_carrito_producto = db.Column(db.Integer, primary_key=True)
    id_carrito = db.Column(db.Integer, db.ForeignKey('carrito.id_carrito'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

    carrito = db.relationship('Carrito', back_populates='productos')
    producto = db.relationship('Producto', back_populates='carritos')


class Pago(db.Model):
    __tablename__ = 'pago'

    id_pago = db.Column(db.Integer, primary_key=True)
    id_carrito = db.Column(db.Integer, db.ForeignKey('carrito.id_carrito'), nullable=False)
    monto = db.Column(db.Integer, nullable=False)
    fecha_pago = db.Column(db.DateTime, default=db.func.now())
    metodo_pago = db.Column(db.Enum('tarjeta', 'paypal', 'transferencia', name='metodo_pago'))
    estado = db.Column(db.Enum('pendiente', 'completado', 'rechazado', name='estado_pago'), default='completado')


class PaypalDetalle(db.Model):
    __tablename__ = 'paypal_detalle'

    id_paypal = db.Column(db.Integer, primary_key=True)
    id_pago = db.Column(db.Integer, db.ForeignKey('pago.id_pago'), unique=True)
    email_paypal = db.Column(db.String(150), nullable=False)
    confirmacion_id = db.Column(db.String(255), nullable=False)

    pago = db.relationship('Pago', backref=db.backref('paypal', uselist=False))


class TransferenciaDetalle(db.Model):
    __tablename__ = 'transferencia_detalle'

    id_transferencia = db.Column(db.Integer, primary_key=True)
    id_pago = db.Column(db.Integer, db.ForeignKey('pago.id_pago'))
    nombre_titular = db.Column(db.String(100), nullable=False)
    banco_origen = db.Column(db.String(100), nullable=False)
    numero_cuenta = db.Column(db.String(100), nullable=False)
    comprobante_url = db.Column(db.String(255), nullable=False)
    fecha_transferencia = db.Column(db.DateTime, default=db.func.now())

    pago = db.relationship('Pago', backref=db.backref('transferencia', uselist=False))


class TarjetaDetalle(db.Model):
    __tablename__ = 'tarjeta_detalle'

    id_tarjeta = db.Column(db.Integer, primary_key=True)
    id_pago = db.Column(db.Integer, db.ForeignKey('pago.id_pago'), unique=True)
    numero_tarjeta_hash = db.Column(db.String(255), nullable=False)
    nombre_en_tarjeta = db.Column(db.String(100), nullable=False)
    cvv_hash = db.Column(db.String(255), nullable=False)
    fecha_expiracion = db.Column(db.String(7), nullable=False)

    pago = db.relationship('Pago', backref=db.backref('tarjeta', uselist=False))

    @property
    def numero_tarjeta(self):
        raise AttributeError("El número de tarjeta no se puede leer directamente.")

    @numero_tarjeta.setter
    def numero_tarjeta(self, numero):
        self.numero_tarjeta_hash = generate_password_hash(numero)

    def verificar_numero_tarjeta(self, numero):
        return check_password_hash(self.numero_tarjeta_hash, numero)

    @property
    def cvv(self):
        raise AttributeError("El CVV no se puede leer directamente.")

    @cvv.setter
    def cvv(self, valor):
        self.cvv_hash = generate_password_hash(str(valor))  # Convertir a string

    def verificar_cvv(self, valor):
        return check_password_hash(self.cvv_hash, valor)


class Factura(db.Model):
    __tablename__ = 'factura'

    id_factura = db.Column(db.Integer, primary_key=True)
    id_pago = db.Column(db.Integer, db.ForeignKey('pago.id_pago'))
    factura_fecha = db.Column(db.DateTime, default=db.func.now())
    total = db.Column(db.Integer, nullable=False)

    detalles = db.relationship('DetalleFactura', backref='factura', lazy=True)


class DetalleFactura(db.Model):
    __tablename__ = 'detalle_factura'

    id_detalle_factura = db.Column(db.Integer, primary_key=True)
    id_factura = db.Column(db.Integer, db.ForeignKey('factura.id_factura'))
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'))
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Integer, nullable=False)
    monto_total = db.Column(db.Integer, nullable=False)


class Orden(db.Model):
    __tablename__ = 'orden'

    id_orden = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    id_factura = db.Column(db.Integer, db.ForeignKey('factura.id_factura'), nullable=False)
    fecha_orden = db.Column(db.DateTime, default=db.func.now())
    monto_total = db.Column(db.Integer, nullable=False)
    estado = db.Column(
        db.Enum('pendiente', 'procesando', 'pagada', 'enviada', 'cancelada', name='estado_orden'),
        default='enviada'
    )


class Envio(db.Model):
    __tablename__ = 'envio'
    
    ESTADOS_VALIDOS = {
        'Empacando',
        'Validando',
        'En Camino a Tu Hogar',
        'Tu Pedido Ya Ha Sido Entregado'
    }
    
    id = db.Column(db.Integer, primary_key=True)
    direccion = db.Column(db.String(255), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    departamento = db.Column(db.String(100), nullable=False)
    codigo_postal = db.Column(db.String(20), nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    estado_envio = db.Column(db.String(100), default="Empacando")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime)  # Añadir este campo
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    usuario = db.relationship('Usuario', back_populates='envios')
    id_factura = db.Column(db.Integer, db.ForeignKey('factura.id_factura'), nullable=False)  # Cambiar a nullable=False
    factura = db.relationship('Factura', backref=db.backref('envios', lazy=True))