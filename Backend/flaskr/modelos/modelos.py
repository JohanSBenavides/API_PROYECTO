from marshmallow import fields
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

class Estado(enum.Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"

class Usuario(db.Model):
    id_usuario= db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(50))
    apellidos = db.Column(db.String(50))
    tipo_doc = db.Column(db.String(50))
    telefono = db.Column(db.Numeric(40))
    num_documento = db.Column(db.Numeric(40))
    direccion = db.Column(db.String(100))
    contrasena_hash = db.Column(db.String(100))
    estado = db.Column(db.Enum(Estado), default=Estado.ACTIVO)
    email = db.Column(db.String(100), unique=True)

    id_rol = db.relationship('Rol', backref='id_rol', lazy=True)
    clientes = db.relationship('Cliente', backref='usuario', lazy=True)

    def set_contrasena(self, contrasena):
        self.contrasena_hash = generate_password_hash(contrasena)

    def check_contrasena(self, contrasena):
        return check_password_hash(self.contrasena_hash, contrasena)

class Rol(db.Model):
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    descripcion = db.Column(db.String(100))

    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    contacto = db.Column(db.String(50))
    estado = db.Column(db.Enum(Estado), default=Estado.ACTIVO)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    descripcion = db.Column(db.String(200))
    productos = db.relationship('Producto', backref='categoria', lazy=True)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.String(200))
    imagen = db.Column(db.String(255))
    stock = db.Column(db.Integer)
    precio = db.Column(db.Float)
    estado = db.Column(db.Enum(Estado), default=Estado.ACTIVO)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)

class Factura(db.Model):
    id_factura = db.Column(db.Integer, primary_key=True)
    fecha_factura = db.Column(db.Date)
    fecha_vencimiento = db.Column(db.Date)
    metodo_pago = db.Column(db.String(50))
    IVA = db.Column(db.numeric)
    subtotal = db.Column(db.numeric)
    total = db.Column(db.Float)
    estado = db.Column(db.Enum(Estado), default=Estado.ACTIVO)

    cliente = db.relationship('Cliente', backref='factura', lazy=True)
    compra = db.relationship('Compra', backref='factura', lazy=True)                                                                                                                                                

class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {"llave": value.name, "valor": value.value}

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True
    contrasena = fields.Method("set_contrasena", deserialize="load_contrasena")

    def set_contrasena(self, contrasena):
        usuario = self.context.get("usuario")
        if usuario:
            usuario.contrasena.set_contrasena(contrasena)


class ProveedorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Proveedor
        include_relationships = True
        load_instance = True

class CategoriaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Categoria
        include_relationships = True
        load_instance = True

class ProductoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Producto
        include_relationships = True
        load_instance = True


class FacturaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Factura
        include_relationships = True
        load_instance = True
