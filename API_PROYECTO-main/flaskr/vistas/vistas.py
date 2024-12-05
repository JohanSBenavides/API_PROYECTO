from flask import request
from flask_restful import Resource
from ..modelos import db, Usuario, UsuarioSchema, Categoria, CategoriaSchema, Producto, ProductoSchema
from  flask_jwt_extended import create_access_token


#Uso de lo schemas creados en modelos
usuario_schema = UsuarioSchema()
producto_schema = ProductoSchema()
categoria_schema = CategoriaSchema()


#si la clase termina en s es para ver todos o para añadir, si es es x ejemplo solo usuario, es para editar o eliminar uno especifico
class VistaUsuarios(Resource):
    def post(self):
        nuevo_usuario = Usuario(nombre = request.json ['nombre'],
                                correo = request.json['correo'],    
                                contrasena = request.json['contraseña'])
        db.session.add(nuevo_usuario)
        db.session.commit()
        return usuario_schema.dump(nuevo_usuario)
    
    def get(self):
        return [usuario_schema.dump(Usuario) for Usuario in Usuario.query.all()]


class VistaUsuario(Resource):
    
    def put(self, id_usuario):
        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return 'El usuario no existe'
        
        usuario.nombre = request.json.get('nombre', usuario.nombre)
        usuario.numerodoc = request.json.get('numerodoc', usuario.numerodoc)
        usuario.correo = request.json.get('correo', usuario.correo)
        usuario.contrasena = request.json.get('contrasena', usuario.contrasena)

        db.session.commit()
        return usuario_schema.dump(usuario)
    
    def delete(self, id_usuario):
        
        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return 'Usuario no encontrado', 404
        
        db.session.delete(usuario)
        db.session.commit()
        return 'Usuario eliminado'
    
class VistaProductos(Resource):
    #Obtener todos los productos
    def get(self):
        return [producto_schema.dump(Producto) for Producto in Producto.query.all()]
#Agregar productos
    def post(self):
        nuevo_producto = Producto(producto_nombre = request.json ['producto_nombre'],
                                producto_precio = request.json['producto_precio'],    
                                producto_stock = request.json['producto_stock'],    
                                categoria_id = request.json['categoria_id'],
                                descripcion = request.json['descripcion'])
        db.session.add(nuevo_producto)
        db.session.commit()
        return {'mensaje': 'Producto creado exitosamente'}

#Editar algun producto
    def put(self, id_producto):
        producto = Producto.query.get(id_producto)
        if not producto:
            return 'El producto no existe'
        
        producto.producto_nombre = request.json.get('producto_nombre', producto.producto_nombre)
        producto.producto_precio = request.json.get('producto_precio', producto.producto_precio)
        producto.producto_precio = request.json.get('producto_precio', producto.producto_precio)
        producto.categoria_id = request.json.get('categoria_id', producto.categoria_id)
        producto.descripcion = request.json.get('descripcion', producto.descripcion)

        db.session.commit()
        return producto_schema.dump(producto)

    def delete(self, id_producto):
        producto = Producto.query.get(id_producto)
        if not producto:
            return 'Producto no encontrado', 404
        
        db.session.delete(producto)
        db.session.commit()
        return 'Producto eliminado'
    
class VistaCategoria(Resource):
    def put(self, id_categoria):
        categoria = Categoria.query.get(id_categoria)
        if not categoria:
            return 'La categoria no existe'
        
        categoria.nombre = request.json.get('nombre', categoria.nombre)


        db.session.commit()
        return categoria_schema.dump(categoria)
    
    
    
    #def delete(self, id_categoria):
        categoria = Categoria.query.get(id_categoria)
        if not categoria:
            return 'Categoria no encontrada', 404
        
        db.session.delete(categoria)
        db.session.commit()
        return 'Categoria eliminada'
    
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
        correo = request.json.get("correo")
        contrasena = request.json.get("contrasena")

        # Verificar que los datos lleguen correctamente
        print(f"Correo: {correo}, Contraseña: {contrasena}")

        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario:
            print(f"Usuario encontrado: {usuario.nombre}")
            if usuario.verificar_contrasena(contrasena):
                token_de_acceso = create_access_token(identity=correo)
                return {'mensaje': 'Inicio de sesión exitoso', 'token_de_acceso': token_de_acceso}, 200
            else:
                return {'mensaje': 'Correo o contraseña incorrectos'}, 401
        else:
            return {'mensaje': 'Correo no encontrado'}, 404

            
class VistaSignIn(Resource):

    def post(self):
        # Verificar si el correo ya existe en la base de datos
        correo_existente = Usuario.query.filter_by(correo=request.json["correo"]).first()
        if correo_existente:
            return {'mensaje': 'El correo ya está registrado. Por favor, ingrese otro correo.'}, 400
        
        # Crear el nuevo usuario
        nuevo_usuario = Usuario(
            nombre=request.json["nombre"],
            numerodoc=request.json["numerodoc"],
            correo=request.json["correo"]
        )
        # Encriptar la contraseña
        nuevo_usuario.contrasena = request.json["contrasena"]  # Esto asumirá que el setter encripta la contraseña
        
        # Generar el token de acceso
        token_de_acceso = create_access_token(identity=request.json['nombre'])
        
        # Guardar el usuario en la base de datos
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return {'mensaje': 'Usuario creado exitosamente', 'token': token_de_acceso}, 201

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.contrasena = request.json.get("contrasena", usuario.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204 

    

    

