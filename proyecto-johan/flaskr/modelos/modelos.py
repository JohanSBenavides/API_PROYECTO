from marshmallow import fields
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
import enum

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class rol(db.Model):
    id_rol = db.Column(db.Integer, primary_key = True)
    nombre_rol = db.Column(db.String(45))

class Usuario(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(45))
    apellido = db.Column(db.String(45))
    usuariousuario = db.Column(db.String(45))
    usuarioclave = db.Column(db.Integer)
    usuarioemail = db.Column(db.String(45))
    id_rol =  db.Column(db.Integer)

class compras(db.Model): 
    id_compra = db.Column(db.Integer, primary_key = True)
    id_usuario = db.Column(db.Integer)
    id_proveedor = db.Column(db.Integer)
    fecha_compra = db.Column(db.String(45))
    total = db.Column(db.Integer)
  
class producto(db.Model):
    id_producto = db.Column(db.Integer, primary_key = True)
    producto_codigo = db.Column(db.String(45))
    nombre = db.Column(db.String(45))
    precio = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    categoria_id = db.Column(db.Integer)

class detalle_compra(db.Model):
    id_compra = db.Column(db.Integer, primary_key = True)
    id_producto = db.Column(db.Integer)
    cantidad = db.Column(db.Integer)
    precio_unitario = db.Column(db.Integer)

class categoria(db.Model):
    id_categoria = db.Column(db.Integer, primary_key = True)
    categoria_nombre = db.Column(db.String(45))

class carrito_compras(db.Model):
    id_carrito_compras = db.Column(db.Integer, primary_key = True)
    id_usuario = db.Column(db.Integer)
    fecha = db.Column(db.String(45))

class detalle_carrito(db.Model):
    id_detalle = db.Column(db.Integer, primary_key = True)
    id_carrito = db.Column(db.Integer)
    id_producto = db.Column(db.Integer)
    cantidad = db.Column(db.Integer)

class orden(db.Model):
    id_orden = db.Column(db.Integer, primary_key = True)
    id_usuario = db.Column(db.Integer)
    fecha_orden = db.Column(db.String(45))
    monto_total = db.Column(db.Integer)

class factura(db.Model):
    id_factura = db.Column(db.Integer, primary_key = True)
    id_orden = db.Column(db.Integer)
    factura_fecha = db.Column(db.String(45))
    monto_total = db.Column(db.Integer)

class factura_items(db.Model):
    id_factura_detalle = db.Column(db.Integer, primary_key = True)
    id_factura = db.Column(db.Integer)
    id_producto = db.Column(db.Integer)
    cantidad = db.Column(db.Integer)
    precio_unitario = db.Column(db.Integer)






