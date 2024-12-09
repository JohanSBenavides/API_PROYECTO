from flask import request
from flask_restful import Resource
from ..modelos import db, Usuario, Producto, Categoria, Rol, UsuarioSchema, ProductoSchema, CategoriaSchema
from flask_jwt_extended import create_access_token
#Uso de lo schemas creados en modelos
usuario_schema = UsuarioSchema()
producto_schema = ProductoSchema()
categoria_schema = CategoriaSchema()

import logging

from flask import request
from flask_restful import Resource
from sqlalchemy.orm.exc import NoResultFound


#si la clase termina en s es para ver todos o para añadir, si es es x ejemplo solo usuario, es para editar o eliminar uno especifico
class VistaUsuarios(Resource):
    #Obtener todos los usuarios    
    def get(self):
        return [usuario_schema.dump(Usuario) for Usuario in Usuario.query.all()]


class VistaUsuario(Resource):
    
    def put(self, id_usuario):
        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return {'message': 'El usuario no existe'}, 404

        usuario.nombre = request.json.get('nombre', usuario.nombre)
        usuario.numerodoc = request.json.get('numerodoc', usuario.numerodoc)
        usuario.correo = request.json.get('correo', usuario.correo)

        nueva_contrasena = request.json.get('contrasena', None)
        if nueva_contrasena:
            usuario.contrasena = nueva_contrasena

        db.session.commit()
        return usuario_schema.dump(usuario)

    
    def delete(self, id_usuario):
        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return {'message': 'El usuario no existe'}, 404

        admin_rol = Rol.query.filter_by(nombre_rol="admin").first()

        if usuario.rol_id == admin_rol.rol_id:
            return {'message': 'No se puede eliminar al superadmin'}, 403

        db.session.delete(usuario)
        db.session.commit()
        return {'message': 'Usuario eliminado exitosamente'}
    
class VistaProductos(Resource):
    # Obtener todos los productos
    def get(self):
        productos = Producto.query.all()
        return [producto_schema.dump(producto) for producto in productos], 200

    # Agregar productos
    def post(self):
        try:
            nuevo_producto = Producto(
                producto_nombre=request.json['producto_nombre'],
                producto_precio=request.json['producto_precio'],
                producto_stock=request.json['producto_stock'],
                categoria_id=request.json['categoria_id'],
                descripcion=request.json['descripcion'],
                producto_foto=request.json.get('producto_foto', None)  # Recibimos la URL de la foto
            )
            db.session.add(nuevo_producto)
            db.session.commit()
            return {'mensaje': 'Producto creado exitosamente'}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

    
class VistaProducto(Resource):
    # Editar algún producto
    def put(self, id_producto):
        producto = Producto.query.get(id_producto)
        if not producto:
            return {'message': 'El producto no existe'}, 404

        # Actualizamos los campos del producto
        producto.producto_nombre = request.json.get('producto_nombre', producto.producto_nombre)
        producto.producto_precio = request.json.get('producto_precio', producto.producto_precio)
        producto.producto_stock = request.json.get('producto_stock', producto.producto_stock)
        producto.categoria_id = request.json.get('categoria_id', producto.categoria_id)
        producto.descripcion = request.json.get('descripcion', producto.descripcion)
        producto.producto_foto = request.json.get('producto_foto', producto.producto_foto)  # Actualizamos la foto

        db.session.commit()
        return producto_schema.dump(producto), 200

    # Eliminar producto
    def delete(self, id_producto):
        producto = Producto.query.get(id_producto)
        if not producto:
            return {'message': 'Producto no encontrado'}, 404
        
        db.session.delete(producto)
        db.session.commit()
        return {'message': 'Producto eliminado'}, 200

    
class VistaCategoria(Resource):
    def put(self, id_categoria):
        categoria = Categoria.query.get(id_categoria)
        if not categoria:
            return 'La categoria no existe'
        
        categoria.nombre = request.json.get('nombre', categoria.nombre)


        db.session.commit()
        return categoria_schema.dump(categoria)
    

    
class VistaCategorias(Resource):
    def get(self):
        return [categoria_schema.dump(Categoria) for Categoria in Categoria.query.all()]

    def post(self):
        nueva_categoria = Categoria(nombre = request.json ['nombre'])
        db.session.add(nueva_categoria)
        db.session.commit()
        return {'mensaje': 'Categoria creada exitosamente'}
    
    
    
class VistaLogin(Resource):
    def post(self):
        # Obtener los datos del JSON (correo y contraseña)
        correo = request.json.get('correo', None)
        contrasena = request.json.get('contrasena', None)

        # Verificar que se haya proporcionado correo y contraseña
        if not correo or not contrasena:
            return {"mensaje": "Correo y contraseña son requeridos."}, 400

        # Buscar el usuario por correo
        usuario = Usuario.query.filter_by(correo=correo).first()

        # Verificar si el usuario existe y si la contraseña es correcta
        if not usuario or not usuario.verificar_contrasena(contrasena):
            return {"mensaje": "Correo o contraseña incorrectos."}, 401

        # Devolver el mensaje y el token
        return {"mensaje": "INICIASTE SESION MI PAPÁ"}, 200

            
class VistaSignIn(Resource):
    def post(self):
        # Verificar si el correo ya está registrado
        if Usuario.query.filter_by(correo=request.json["correo"]).first():
            return {"message": "El correo ya está registrado."}, 400

        # Validar que la contraseña no esté vacía
        contrasena = request.json.get("contrasena")
        if not contrasena or contrasena.strip() == "":
            return {"message": "La contraseña no puede estar vacía."}, 400

        # Obtener el rol 'Cliente' (id_rol = 2)
        rol_cliente = Rol.query.filter_by(rol_id=2).first()
        if not rol_cliente:
            return {"message": "Rol 'Cliente' no encontrado."}, 400

        # Crear el nuevo usuario
        nuevo_usuario = Usuario(
            nombre=request.json["nombre"],
            numerodoc=request.json["numerodoc"],
            correo=request.json["correo"],
            contrasena=contrasena,  # Utiliza el setter de contrasena
            rol_id=rol_cliente.rol_id  
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        # Crear el token JWT
        access_token = create_access_token(identity=nuevo_usuario.id_usuario)

        return {
            "message": "Usuario creado exitosamente.",
            "token": access_token 
        }, 201


    