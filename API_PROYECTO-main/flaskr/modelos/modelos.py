from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy  import SQLAlchemyAutoSchema
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Carrito(db.Model):
    __tablename__ = 'carrito'
    id_carrito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    fecha = db.Column(db.Integer)
    total = db.Column(db.Integer)

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))


class DetalleCarrito(db.Model):
    __tablename__ = 'detalle_carrito'
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_carrito = db.Column(db.Integer, db.ForeignKey('carrito.id_carrito'))
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'))
    cantidad = db.Column(db.Integer)

class DetalleFactura(db.Model):
    __tablename__ = 'detalle_factura'
    id_detalle_factura = db.Column(db.Integer, primary_key=True)
    id_factura = db.Column(db.Integer, db.ForeignKey('factura.id_factura'))
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'))
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Integer)

class Envio(db.Model):
    __tablename__ = 'envio'
    id_envio = db.Column(db.Integer, primary_key=True)
    id_orden = db.Column(db.Integer, db.ForeignKey('orden.id_orden'))
    direccion =db.Column(db.String(50))
    fecha = db.Column(db.Date)     

class Factura(db.Model):
    __tablename__ = 'factura'
    id_factura = db.Column(db.Integer, primary_key=True)
    id_orden = db.Column(db.Integer, db.ForeignKey('orden.id_orden'))
    factura_fecha = db.Column(db.Date)
    monto_total = db.Column(db.Integer)

class Orden(db.Model):
    __tablename__ = 'orden'
    id_orden = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    fecha_orden = db.Column(db.Date)
    monto_total = db.Column(db.Integer)
    estado = db.Column(db.String(50))


class Pago(db.Model):
    __tablename__ = 'pago'
    id_pago = db.Column(db.Integer, primary_key=True)
    id_orden = db.Column(db.Integer, db.ForeignKey('orden.id_orden'))
    monto = db.Column(db.Integer)
    fecha_pago = db.Column(db.Date)
    metodo_pago = db.Column(db.String(50))
    estado = db.Column(db.String(50))



class Producto(db.Model):
    __tablename__ = 'producto'
    id_producto = db.Column(db.Integer, primary_key=True)
    producto_nombre = db.Column(db.String(100))
    producto_precio = db.Column(db.Integer)
    producto_stock = db.Column(db.Integer)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'))
    descripcion = db.Column(db.String(255))


class Rol(db.Model):
    __tablename__ = 'rol'
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50))


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    numerodoc = db.Column(db.Integer)
    correo = db.Column(db.String(100))
    contrasena_hash = db.Column('contrasena_hash', db.String(100))
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id_rol'))

    @property
    def contrasena(self):
        raise AttributeError("La contraseña n es un atributo legible")

    @contrasena.setter
    def contrasena(self, password):
        if not password:
            raise ValueError("La contraseña no puede estar vacía.")
        self.contrasena_hash = generate_password_hash(password)

    def verificar_contrasena(self, password):
        return check_password_hash(self.contrasena_hash, password)


# Esquemas

class DetalleCarritoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DetalleCarrito
        include_relationships = True
        load_instance = True

class DetalleFacturaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DetalleFactura
        include_relationships = True
        load_instance = True

class CarritoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Carrito
        include_relationships = True
        load_instance = True


class FacturaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Factura
        include_relationships = True
        load_instance = True

class OrdenSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Orden
        include_relationships = True
        load_instance = True

class PagoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Pago
        include_relationships = True
        load_instance = True

class ProductoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Producto
        include_relationships = True
        load_instance = True

class RolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Rol
        include_relationships = True
        load_instance = True

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True

class CategoriaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Categoria
        include_relationships = True
        load_instance = True

class EnvioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Envio
        include_relationships = True
        load_instance = True