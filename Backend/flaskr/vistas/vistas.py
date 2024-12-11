import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..modelos import db, Usuario, Producto, Categoria, Rol, UsuarioSchema, ProductoSchema, CategoriaSchema, RolSchema, PagoSchema, EnvioSchema, OrdenSchema, CarritoSchema, FacturaSchema, DetalleCarritoSchema, DetalleFacturaSchema, DetalleCarrito, DetalleFactura, Factura, Pago, Orden, Envio, Carrito

# Uso de los schemas creados en modelos
usuario_schema = UsuarioSchema()
producto_schema = ProductoSchema()
categoria_schema = CategoriaSchema()
carrito_schema = CarritoSchema()
detalle_carrito_schema = DetalleCarritoSchema()
factura_schema = FacturaSchema()
orden_schema = OrdenSchema()
detalle_factura_schema = DetalleFacturaSchema()
envio_schema = EnvioSchema()
pago_schema = PagoSchema()


#insercion de productos con imagenees de manera local
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class VistaProtegida(Resource):
    @jwt_required()
    def get(self):
        usuario_actual = get_jwt_identity()
        return {"mensaje": f"Bienvenido {usuario_actual}"}, 200

class VistaUsuarios(Resource):
    @jwt_required()
    def get(self):
        usuarios = Usuario.query.all()
        return [usuario_schema.dump(usuario) for usuario in usuarios], 200

    @jwt_required()
    def post(self):
        if Usuario.query.filter_by(correo=request.json["correo"]).first():
            return {"message": "El correo ya está registrado."}, 400

        contrasena = request.json.get("contrasena")
        if not contrasena or contrasena.strip() == "":
            return {"message": "La contraseña no puede estar vacía."}, 400

        rol_cliente = Rol.query.filter_by(rol_id=2).first()
        if not rol_cliente:
            return {"message": "Rol 'Cliente' no encontrado."}, 400

        nuevo_usuario = Usuario(
            nombre=request.json["nombre"],
            numerodoc=request.json["numerodoc"],
            correo=request.json["correo"],
            contrasena=contrasena,
            rol_id=rol_cliente.rol_id
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return {
            "message": "Usuario creado exitosamente."
        }, 201


class VistaUsuario(Resource):
    @jwt_required()
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

    @jwt_required()
    def delete(self, id_usuario):
        usuario = Usuario.query.get(id_usuario)

        if not usuario:
            return {"message": "Usuario no encontrado."}, 404

        admin_rol = Rol.query.filter_by(rol_id=1).first()
        if not admin_rol:
            return {"message": "Rol de administrador no encontrado."}, 400

        if usuario.rol_id == admin_rol.rol_id:
            return {"message": "No se puede eliminar a un usuario con rol de administrador."}, 400

        db.session.delete(usuario)
        db.session.commit()

        return {"message": "Usuario eliminado exitosamente."}, 200

class VistaProductos(Resource):
    @jwt_required()
    def get(self):
        productos = Producto.query.all()
        return [producto_schema.dump(producto) for producto in productos], 200

    @jwt_required()
    def post(self):
        try:
            # Verificar si se ha enviado un archivo
            if 'producto_foto' not in request.files:
                return {'message': 'No se ha enviado una imagen para el producto'}, 400

            file = request.files['producto_foto']
            if file and allowed_file(file.filename):
                # Guardar la imagen en el directorio deseado
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                # Crear un nuevo producto con la imagen guardada
                nuevo_producto = Producto(
                    producto_nombre=request.form['producto_nombre'],
                    producto_precio=request.form['producto_precio'],
                    producto_stock=request.form['producto_stock'],
                    categoria_id=request.form['categoria_id'],
                    descripcion=request.form['descripcion'],
                    producto_foto=filename  # Guardar el nombre de la imagen
                )
                db.session.add(nuevo_producto)
                db.session.commit()

                return {'mensaje': 'Producto creado exitosamente'}, 201
            else:
                return {'message': 'Formato de imagen no permitido'}, 400
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400



class VistaProducto(Resource):
    @jwt_required()
    def put(self, id_producto):
        producto = Producto.query.get(id_producto)
        if not producto:
            return {'message': 'El producto no existe'}, 404

        # Verificar si se ha enviado una nueva imagen
        if 'producto_foto' in request.files:
            file = request.files['producto_foto']
            if file and allowed_file(file.filename):
                # Eliminar la imagen anterior si existe
                if producto.producto_foto:
                    try:
                        os.remove(os.path.join(UPLOAD_FOLDER, producto.producto_foto))
                    except FileNotFoundError:
                        pass

                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                producto.producto_foto = filename

        # Obtener los campos del cuerpo de la solicitud
        producto.producto_nombre = request.form.get('producto_nombre', producto.producto_nombre)
        producto.producto_precio = request.form.get('producto_precio', producto.producto_precio)
        producto.producto_stock = request.form.get('producto_stock', producto.producto_stock)
        producto.descripcion = request.form.get('descripcion', producto.descripcion)
        producto.categoria_id = request.form.get('categoria_id', producto.categoria_id)

        db.session.commit()
        return producto_schema.dump(producto), 200
    
    @jwt_required()
    def delete(self, id_producto):
        producto = Producto.query.get(id_producto)
        if not producto:
            return {'message': 'Producto no encontrado'}, 404

        if producto.producto_foto:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, producto.producto_foto))
            except FileNotFoundError:
                pass

        db.session.delete(producto)
        db.session.commit()
        return {'message': 'Producto eliminado'}, 200


class VistaCategoria(Resource):
    @jwt_required()
    def put(self, id_categoria):
        # Verificar si la categoría existe
        categoria = Categoria.query.get(id_categoria)
        if not categoria:
            return {'mensaje': 'La categoría no existe'}, 404

        # Actualizar el nombre de la categoría
        categoria.nombre = request.json.get('nombre', categoria.nombre)
        db.session.commit()

        # Retornar la categoría actualizada
        return categoria_schema.dump(categoria), 200

    @jwt_required()
    def delete(self, id_categoria):
        # Verificar si la categoría existe
        categoria = Categoria.query.get(id_categoria)
        if not categoria:
            return {'mensaje': 'La categoría no existe'}, 404

        # Eliminar la categoría
        db.session.delete(categoria)
        db.session.commit()

        return {'mensaje': 'Categoría eliminada exitosamente'}, 200


class VistaCategorias(Resource):
    @jwt_required()
    def get(self):
        categorias = Categoria.query.all()
        return [categoria_schema.dump(categoria) for categoria in categorias], 200

    @jwt_required()
    def post(self):
        nueva_categoria = Categoria(nombre=request.json['nombre'])
        db.session.add(nueva_categoria)
        db.session.commit()
        return {'mensaje': 'Categoria creada exitosamente'}, 201

class VistaLogin(Resource):
    def post(self):
        # Obtener las credenciales del usuario desde el cuerpo de la solicitud
        correo = request.json.get("correo")
        contrasena = request.json.get("contrasena")

        # Buscar al usuario por correo
        usuario = Usuario.query.filter_by(correo=correo).first()

        # Verificar que el usuario exista y que la contraseña sea correcta
        if usuario and usuario.verificar_contrasena(contrasena):
            # Generar el token de acceso, asegurándose de que 'identity' sea una cadena
            token_de_acceso = create_access_token(identity=str(usuario.id_usuario))

            return {
                "mensaje": "Inicio de sesión exitoso",
                "token": token_de_acceso,
                "rol": usuario.rol_id  # Aquí asumimos que 'rol_id' es un campo en el modelo Usuario
            }, 200

        return {"mensaje": "Usuario o contraseña incorrectos"}, 401


class VistaSignIn(Resource):
    def post(self):
        if Usuario.query.filter_by(correo=request.json["correo"]).first():
            return {"message": "El correo ya está registrado."}, 400

        contrasena = request.json.get("contrasena")
        if not contrasena or contrasena.strip() == "":
            return {"message": "La contraseña no puede estar vacía."}, 400

        rol_cliente = Rol.query.filter_by(rol_id=2).first()
        if not rol_cliente:
            return {"message": "Rol 'Cliente' no encontrado."}, 400

        nuevo_usuario = Usuario(
            nombre=request.json["nombre"],
            numerodoc=request.json["numerodoc"],
            correo=request.json["correo"],
            contrasena=contrasena,
            rol_id=rol_cliente.rol_id
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        access_token = create_access_token(identity=nuevo_usuario.id_usuario)

        return {
            "message": "Usuario creado exitosamente.",
            "token": access_token
        }, 201

class VistaCarritos(Resource):
    @jwt_required()
    def get(self):
        # Obtener todos los carritos
        carritos = Carrito.query.all()
        return [carrito_schema.dump(carrito) for carrito in carritos], 200

    @jwt_required()
    def post(self):
        # Obtener el id_usuario desde el token
        user_id = get_jwt_identity()  # Esto recupera el id del usuario desde el JWT
        
        if not user_id:
            return {"error": "No se pudo obtener el usuario del token"}, 400

        # Crear un nuevo carrito con la información recibida
        nuevo_carrito = Carrito(
            id_usuario=user_id,  # El id_usuario se obtiene del token
            fecha=db.func.now(),  # Fecha automática
            total=request.json['total']  # Total enviado desde el frontend
        )

        try:
            db.session.add(nuevo_carrito)
            db.session.commit()
            return {"message": "Carrito creado exitosamente", "cart_id": nuevo_carrito.id_carrito}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class VistaCarrito(Resource):
    @jwt_required()
    def put(self, id_carrito):
        carrito = Carrito.query.get(id_carrito)
        if not carrito:
            return {"message": "Carrito no encontrado"}, 404

        carrito.id_usuario = request.json.get('id_usuario', carrito.id_usuario)
        carrito.fecha = request.json.get('fecha', carrito.fecha)
        carrito.total = request.json.get('total', carrito.total)

        db.session.commit()
        return carrito_schema.dump(carrito), 200

    @jwt_required()
    def delete(self, id_carrito):
        carrito = Carrito.query.get(id_carrito)
        if not carrito:
            return {"message": "Carrito no encontrado"}, 404

        db.session.delete(carrito)
        db.session.commit()
        return {"message": "Carrito eliminado exitosamente"}, 200

class VistaDetalleCarritos(Resource):
    @jwt_required()
    def get(self):
        detalles = DetalleCarrito.query.all()
        return [detalle_carrito_schema.dump(detalle) for detalle in detalles], 200

    @jwt_required()
    def post(self):
        nuevo_detalle = DetalleCarrito(
            id_carrito=request.json['id_carrito'],
            id_producto=request.json['id_producto'],
            cantidad=request.json['cantidad']
        )
        db.session.add(nuevo_detalle)
        db.session.commit()
        return {"message": "Detalle del carrito creado exitosamente"}, 201

class VistaDetalleCarrito(Resource):
    @jwt_required()
    def put(self, id_detalle):
        detalle = DetalleCarrito.query.get(id_detalle)
        if not detalle:
            return {"message": "Detalle no encontrado"}, 404

        detalle.id_carrito = request.json.get('id_carrito', detalle.id_carrito)
        detalle.id_producto = request.json.get('id_producto', detalle.id_producto)
        detalle.cantidad = request.json.get('cantidad', detalle.cantidad)

        db.session.commit()
        return detalle_carrito_schema.dump(detalle), 200

    @jwt_required()
    def delete(self, id_detalle):
        detalle = DetalleCarrito.query.get(id_detalle)
        if not detalle:
            return {"message": "Detalle no encontrado"}, 404

        db.session.delete(detalle)
        db.session.commit()
        return {"message": "Detalle eliminado exitosamente"}, 200

class VistaFacturas(Resource):
    @jwt_required()
    def get(self):
        facturas = Factura.query.all()
        return [factura_schema.dump(factura) for factura in facturas], 200

    @jwt_required()
    def post(self):
        nueva_factura = Factura(
            id_orden=request.json['id_orden'],
            factura_fecha=request.json['factura_fecha'],
            monto_total=request.json['monto_total']
        )
        db.session.add(nueva_factura)
        db.session.commit()
        return {"message": "Factura creada exitosamente"}, 201

class VistaFactura(Resource):
    @jwt_required()
    def put(self, id_factura):
        factura = Factura.query.get(id_factura)
        if not factura:
            return {"message": "Factura no encontrada"}, 404

        factura.id_orden = request.json.get('id_orden', factura.id_orden)
        factura.factura_fecha = request.json.get('factura_fecha', factura.factura_fecha)
        factura.monto_total = request.json.get('monto_total', factura.monto_total)

        db.session.commit()
        return factura_schema.dump(factura), 200

    @jwt_required()
    def delete(self, id_factura):
        factura = Factura.query.get(id_factura)
        if not factura:
            return {"message": "Factura no encontrada"}, 404

        db.session.delete(factura)
        db.session.commit()
        return {"message": "Factura eliminada exitosamente"}, 200

class VistaOrdenes(Resource):
    @jwt_required()
    def get(self):
        ordenes = Orden.query.all()
        return [orden_schema.dump(orden) for orden in ordenes], 200

    @jwt_required()
    def post(self):
        nueva_orden = Orden(
            id_usuario=request.json['id_usuario'],
            fecha_orden=request.json['fecha_orden'],
            monto_total=request.json['monto_total'],
            estado=request.json['estado']
        )
        db.session.add(nueva_orden)
        db.session.commit()
        return {"message": "Orden creada exitosamente"}, 201

class VistaOrden(Resource):
    @jwt_required()
    def put(self, id_orden):
        orden = Orden.query.get(id_orden)
        if not orden:
            return {"message": "Orden no encontrada"}, 404

        orden.id_usuario = request.json.get('id_usuario', orden.id_usuario)
        orden.fecha_orden = request.json.get('fecha_orden', orden.fecha_orden)
        orden.monto_total = request.json.get('monto_total', orden.monto_total)
        orden.estado = request.json.get('estado', orden.estado)

        db.session.commit()
        return orden_schema.dump(orden), 200

    @jwt_required()
    def delete(self, id_orden):
        orden = Orden.query.get(id_orden)
        if not orden:
            return {"message": "Orden no encontrada"}, 404

        db.session.delete(orden)
        db.session.commit()
        return {"message": "Orden eliminada exitosamente"}, 200

class VistaDetalleFacturas(Resource):
    @jwt_required()
    def get(self):
        detalles = DetalleFactura.query.all()
        return [detalle_factura_schema.dump(detalle) for detalle in detalles], 200

    @jwt_required()
    def post(self):
        nuevo_detalle = DetalleFactura(
            id_factura=request.json['id_factura'],
            id_producto=request.json['id_producto'],
            cantidad=request.json['cantidad'],
            precio_unitario=request.json['precio_unitario']
        )
        db.session.add(nuevo_detalle)
        db.session.commit()
        return {"message": "Detalle de factura creado exitosamente"}, 201

class VistaDetalleFactura(Resource):
    @jwt_required()
    def put(self, id_detalle_factura):
        detalle = DetalleFactura.query.get(id_detalle_factura)
        if not detalle:
            return {"message": "Detalle no encontrado"}, 404

        detalle.id_factura = request.json.get('id_factura', detalle.id_factura)
        detalle.id_producto = request.json.get('id_producto', detalle.id_producto)
        detalle.cantidad = request.json.get('cantidad', detalle.cantidad)
        detalle.precio_unitario = request.json.get('precio_unitario', detalle.precio_unitario)

        db.session.commit()
        return detalle_factura_schema.dump(detalle), 200

    @jwt_required()
    def delete(self, id_detalle_factura):
        detalle = DetalleFactura.query.get(id_detalle_factura)
        if not detalle:
            return {"message": "Detalle no encontrado"}, 404

        db.session.delete(detalle)
        db.session.commit()
        return {"message": "Detalle eliminado exitosamente"}, 200

class VistaEnvios(Resource):
    @jwt_required()
    def get(self):
        envios = Envio.query.all()
        return [envio_schema.dump(envio) for envio in envios], 200

    @jwt_required()
    def post(self):
        nuevo_envio = Envio(
            id_orden=request.json['id_orden'],
            fecha_envio=request.json['fecha_envio'],
            direccion=request.json['direccion'],
            estado=request.json['estado'],
            metodo_envio=request.json['metodo_envio']
        )
        db.session.add(nuevo_envio)
        db.session.commit()
        return {"message": "Envío creado exitosamente"}, 201

class VistaEnvio(Resource):
    @jwt_required()
    def put(self, id_envio):
        envio = Envio.query.get(id_envio)
        if not envio:
            return {"message": "Envío no encontrado"}, 404

        envio.id_orden = request.json.get('id_orden', envio.id_orden)
        envio.fecha_envio = request.json.get('fecha_envio', envio.fecha_envio)
        envio.direccion = request.json.get('direccion', envio.direccion)
        envio.estado = request.json.get('estado', envio.estado)
        envio.metodo_envio = request.json.get('metodo_envio', envio.metodo_envio)

        db.session.commit()
        return envio_schema.dump(envio), 200

    @jwt_required()
    def delete(self, id_envio):
        envio = Envio.query.get(id_envio)
        if not envio:
            return {"message": "Envío no encontrado"}, 404

        db.session.delete(envio)
        db.session.commit()
        return {"message": "Envío eliminado exitosamente"}, 200

class VistaPagos(Resource):
    @jwt_required()
    def get(self):
        pagos = Pago.query.all()
        return [pago_schema.dump(pago) for pago in pagos], 200

    @jwt_required()
    def post(self):
        nuevo_pago = Pago(
            id_orden=request.json['id_orden'],
            fecha_pago=request.json['fecha_pago'],
            monto=request.json['monto'],
            metodo_pago=request.json['metodo_pago'],
            estado=request.json['estado']
        )
        db.session.add(nuevo_pago)
        db.session.commit()
        return {"message": "Pago creado exitosamente"}, 201

class VistaPago(Resource):
    @jwt_required()
    def put(self, id_pago):
        pago = Pago.query.get(id_pago)
        if not pago:
            return {"message": "Pago no encontrado"}, 404

        pago.id_orden = request.json.get('id_orden', pago.id_orden)
        pago.fecha_pago = request.json.get('fecha_pago', pago.fecha_pago)
        pago.monto = request.json.get('monto', pago.monto)
        pago.metodo_pago = request.json.get('metodo_pago', pago.metodo_pago)
        pago.estado = request.json.get('estado', pago.estado)

        db.session.commit()
        return pago_schema.dump(pago), 200

    @jwt_required()
    def delete(self, id_pago):
        pago = Pago.query.get(id_pago)
        if not pago:
            return {"message": "Pago no encontrado"}, 404

        db.session.delete(pago)
        db.session.commit()
        return {"message": "Pago eliminado exitosamente"}, 200    