from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from .modelo import DetalleFactura, Carrito, Factura, Orden, Pago, Producto, Rol, Usuario, Categoria, Envio, CarritoProducto

# Esquemas


class DetalleFacturaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DetalleFactura
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
# 1. ProductoSchema (completo)
class ProductoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Producto
        include_relationships = True
        load_instance = True

    id_producto = fields.Int(dump_only=True)
    producto_nombre = fields.Str(required=True)
    producto_precio = fields.Float(required=True)
    producto_stock = fields.Int(required=True)
    descripcion = fields.Str(required=True)
    producto_foto = fields.Str(required=True)
    categoria_id = fields.Int(required=True)

# 2. ProductoLigeroSchema (ligero, usado solo en CarritoProducto)
class ProductoLigeroSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Producto
        fields = ("id_producto", "producto_nombre", "producto_precio", "producto_foto")
        load_instance = True

# 3. CarritoProductoSchema
class CarritoProductoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CarritoProducto
        include_relationships = True
        load_instance = True

    id_carrito_producto = fields.Int(dump_only=True)
    id_carrito = fields.Int(required=True)
    id_producto = fields.Int(required=True)
    cantidad = fields.Int(required=True)

    producto = fields.Nested(ProductoLigeroSchema, dump_only=True)

# 4. CarritoSchema
class CarritoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Carrito
        include_relationships = True
        load_instance = True

    id_carrito = fields.Int(dump_only=True)
    id_usuario = fields.Int(required=True)
    fecha = fields.DateTime(dump_only=True)
    total = fields.Int(required=True)
    procesado = fields.Bool()

    productos = fields.Nested(CarritoProductoSchema, many=True, dump_only=True)



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

    # Si no quieres que la contraseña se devuelva, puedes omitirla del esquema
    contrasena = fields.Str(load_only=True)  # La contraseña se carga pero no se incluye en la salida

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

