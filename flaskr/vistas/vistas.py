import os
import pytz
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask import request, current_app, jsonify
from flask_restful import Resource
from flask_mail import Message
from flask import current_app
from flask import request, render_template
from flask import render_template
from flaskr.modelos.esquemas import PaypalDetalleSchema, TransferenciaDetalleSchema, TarjetaDetalleSchema, FacturaSchema, HistorialStockSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..modelos import db, Usuario, TarjetaDetalle, TransferenciaDetalle, PaypalDetalle, Producto, Categoria, CarritoProductoSchema, CarritoProducto, Rol, UsuarioSchema, ProductoSchema, CategoriaSchema, RolSchema, PagoSchema, EnvioSchema, OrdenSchema, CarritoSchema, FacturaSchema, DetalleFacturaSchema, DetalleFactura, Factura, Pago, Orden, Envio, Carrito, HistorialStock

# Uso de los schemas creados en modelos
usuario_schema = UsuarioSchema()
producto_schema = ProductoSchema()
categoria_schema = CategoriaSchema()
carrito_schema = CarritoSchema()
facturas_schema = FacturaSchema(many=True)
orden_schema = OrdenSchema()
detalle_factura_schema = DetalleFacturaSchema()
envio_schema = EnvioSchema()
pago_schema = PagoSchema()
carrito_producto_schema = CarritoProductoSchema(many=True)
paypal_schema = PaypalDetalleSchema()
transferencia_schema = TransferenciaDetalleSchema()
tarjeta_schema = TarjetaDetalleSchema()
historial_stock_schema = HistorialStockSchema()
historiales_stock_schema = HistorialStockSchema(many=True)

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
    
    #Intentar añadir getsegun ID para la persona LOGUEADA
    
class VistaPerfilUsuario(Resource):
    @jwt_required()
    def get(self):
        # Obtiene el ID del usuario logueado a partir del JWT
        id_usuario = get_jwt_identity()

        # Verifica si el id_usuario es válido
        if not id_usuario:
            return {"message": "ID de usuario no encontrado en el token."}, 400

        # Buscar al usuario por su ID
        usuario = Usuario.query.get(id_usuario)
        
        if not usuario:
            return {"message": "Usuario no encontrado."}, 404

        # Devuelve los datos del usuario logueado
        return usuario_schema.dump(usuario), 200

    @jwt_required()
    def put(self):
        # Obtiene el ID del usuario logueado a partir del JWT
        id_usuario = get_jwt_identity()

        # Buscar al usuario por su ID
        usuario = Usuario.query.get(id_usuario)
        
        if not usuario:
            return {"message": "Usuario no encontrado."}, 404

        # Actualizar la información del usuario con los datos proporcionados
        usuario.nombre = request.json.get('nombre', usuario.nombre)
        usuario.numerodoc = request.json.get('numerodoc', usuario.numerodoc)
        usuario.correo = request.json.get('correo', usuario.correo)

        # Si se proporciona una nueva contraseña, actualizarla
        nueva_contrasena = request.json.get('contrasena', None)
        if nueva_contrasena:
            usuario.contrasena = nueva_contrasena

        db.session.commit()

        # Devolver la información actualizada del usuario
        return usuario_schema.dump(usuario), 200

class VistaProductos(Resource):
    def get(self):
        """Obtener todos los productos o filtrar por término de búsqueda, precio, categoría y stock."""
        search_term = request.args.get('q')  # Término de búsqueda
        min_price = request.args.get('min_price')  # Precio mínimo
        max_price = request.args.get('max_price')  # Precio máximo
        category_id = request.args.get('category_id')  # ID de la categoría
        in_stock = request.args.get('in_stock')  # Productos con stock disponible

        # Consulta base
        query = Producto.query

        # Filtro por nombre del producto
        if search_term:
            query = query.filter(Producto.producto_nombre.ilike(f'%{search_term}%'))

        # Filtro por rango de precios
        if min_price and min_price.replace('.', '', 1).isdigit():
            query = query.filter(Producto.producto_precio >= float(min_price))
        if max_price and max_price.replace('.', '', 1).isdigit():
            query = query.filter(Producto.producto_precio <= float(max_price))

        # Filtro por categoría
        if category_id and category_id.isdigit():
            query = query.filter(Producto.categoria_id == int(category_id))

        # Filtro por stock disponible
        if in_stock and in_stock.lower() == 'true':
            query = query.filter(Producto.producto_stock > 0)

        # Ejecutar la consulta y devolver los resultados
        productos = query.all()
        return [producto_schema.dump(producto) for producto in productos], 200

    @jwt_required()
    def post(self):
        """Crear un nuevo producto con su respectiva imagen."""
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

                # Obtener los datos del formulario
                producto_nombre = request.form.get('producto_nombre')
                producto_precio = request.form.get('producto_precio')
                producto_stock = request.form.get('producto_stock')
                categoria_id = request.form.get('categoria_id')
                descripcion = request.form.get('descripcion')

                # Validar que todos los campos requeridos estén presentes
                if not producto_nombre or not producto_precio or not producto_stock or not categoria_id or not descripcion:
                    return {'message': 'Faltan datos necesarios para el producto'}, 400

                # Crear un nuevo producto con la imagen guardada
                nuevo_producto = Producto(
                    producto_nombre=producto_nombre,
                    producto_precio=float(producto_precio),  # Convertir el precio a float
                    producto_stock=int(producto_stock),      # Convertir el stock a entero
                    categoria_id=int(categoria_id),          # Convertir la categoría a entero
                    descripcion=descripcion,
                    producto_foto=filename  # Guardar el nombre de la imagen
                )
                db.session.add(nuevo_producto)
                db.session.commit()

                return {'mensaje': 'Producto creado exitosamente'}, 201
            else:
                return {'message': 'Formato de imagen no permitido'}, 400
        except Exception as e:
            db.session.rollback()
            return {'message': f'Ocurrió un error: {str(e)}'}, 400


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
        categorias_data = [categoria_schema.dump(categoria) for categoria in categorias]
        return categorias_data, 200  # ✅ NO uses jsonify


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

            # Verificar si el usuario ya tiene un carrito abierto (no procesado)
            carrito = Carrito.query.filter_by(id_usuario=usuario.id_usuario, procesado=False).first()

            if not carrito:
                # Si no existe un carrito, crearlo
                carrito = Carrito(id_usuario=usuario.id_usuario, total=0)
                db.session.add(carrito)
                db.session.commit()

            # Devolver el mensaje, token y el carrito (si es necesario)
            return {
                "mensaje": "Inicio de sesión exitoso",
                "token": token_de_acceso,
                "rol": usuario.rol_id,  # Asumiendo que 'rol_id' es un campo en el modelo Usuario
                "carrito": CarritoSchema().dump(carrito)  # Devolver el carrito al frontend
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

class VistaCarritoProducto(Resource):
    @jwt_required()
    def get(self, id_carrito):
        """
        Obtener los productos de un carrito específico
        """
        # Buscar los productos asociados al carrito
        productos = CarritoProducto.query.filter_by(id_carrito=id_carrito).all()
        
        # Si no hay productos, responder con un mensaje adecuado
        if not productos:
            return {'message': 'No hay productos en este carrito'}, 404
        
        # Devolver los productos encontrados
        return carrito_producto_schema.dump(productos), 200


            
class VistaCarrito(Resource):
    # Crear un nuevo carrito de compras o ver el carrito de un usuario existente
    @jwt_required()
    def post(self):
        # Obtenemos el usuario desde el token JWT
        user_id = get_jwt_identity()
        
        # Verificar si el usuario ya tiene un carrito abierto
        carrito = Carrito.query.filter_by(id_usuario=user_id, procesado=False).first()

        if not carrito:
            # Si no existe, se crea un carrito vacío
            carrito = Carrito(id_usuario=user_id, total=0)
            db.session.add(carrito)
            db.session.commit()

        return CarritoSchema().dump(carrito), 201

    # Obtener los detalles del carrito de un usuario
    @jwt_required()
    def get(self):
        # Obtener el usuario desde el token JWT
        user_id = get_jwt_identity()
        
        # Buscar el carrito de compras activo del usuario
        carrito = Carrito.query.filter_by(id_usuario=user_id, procesado=False).first()

        if not carrito:
            return {"message": "No se encontró un carrito activo para el usuario."}, 404

        return CarritoSchema().dump(carrito), 200

    # Agregar un producto al carrito de compras
    @jwt_required()
    def put(self, id_carrito):
        """Método PUT para actualizar la cantidad de un producto en el carrito."""
        
        carrito = Carrito.query.get(id_carrito)
        if not carrito:
            return {"message": "Carrito no encontrado."}, 404

        user_id = int(get_jwt_identity())
        if carrito.id_usuario != user_id:
            return {"message": "No tienes permiso para modificar este carrito."}, 403

        producto_id = request.json.get('id_producto')
        cantidad = request.json.get('cantidad', 1)

        if cantidad < 0:
            return {"message": "La cantidad no puede ser negativa."}, 400

        producto = Producto.query.get(producto_id)
        if not producto:
            return {"message": "Producto no encontrado."}, 404

        if cantidad > producto.producto_stock:
            return {"message": "No hay suficiente stock disponible."}, 400

        carrito_producto = CarritoProducto.query.filter_by(id_carrito=id_carrito, id_producto=producto_id).first()

        if carrito_producto:
            # Recalcular total restando el anterior
            carrito.total -= carrito_producto.cantidad * producto.producto_precio
            if cantidad == 0:
                db.session.delete(carrito_producto)
            else:
                carrito_producto.cantidad = cantidad
                carrito.total += cantidad * producto.producto_precio
        else:
            if cantidad == 0:
                return {"message": "No se puede agregar una cantidad 0."}, 400
            carrito_producto = CarritoProducto(id_carrito=id_carrito, id_producto=producto_id, cantidad=cantidad)
            db.session.add(carrito_producto)
            carrito.total += cantidad * producto.producto_precio

        db.session.commit()

        return CarritoSchema().dump(carrito), 200


    @jwt_required()
    def delete(self, id_carrito):
        carrito = Carrito.query.get(id_carrito)

        if not carrito:
            return {"message": "Carrito no encontrado."}, 404

        user_id = int(get_jwt_identity())
        if carrito.id_usuario != user_id:
            return {"message": "No tienes permiso para modificar este carrito."}, 403

        data = request.get_json()
        producto_id = data.get('id_producto')
        
        if not producto_id:
            return {"message": "Falta id_producto"}, 400

        carrito_producto = CarritoProducto.query.filter_by(id_carrito=id_carrito, id_producto=producto_id).first()

        if not carrito_producto:
            return {"message": "Producto no encontrado en el carrito."}, 404

        producto = Producto.query.get(producto_id)
        carrito.total -= producto.producto_precio * carrito_producto.cantidad

        db.session.delete(carrito_producto)
        db.session.commit()

        return {"message": "Producto eliminado del carrito exitosamente."}, 200

    
class VistaCarritoActivo(Resource):
    @jwt_required()
    def get(self):
        id_usuario = get_jwt_identity()

        carrito = Carrito.query.filter_by(id_usuario=id_usuario, procesado=False).first()

        if not carrito:
            carrito = Carrito(
                id_usuario=id_usuario,
                fecha=datetime.now(),
                total=0,
                procesado=False
            )
            db.session.add(carrito)
            db.session.commit()

        productos_carrito = []
        for item in carrito.productos:  # Asegúrate de tener esta relación en tu modelo
            producto = item.producto
            productos_carrito.append({
                "id_producto": producto.id_producto,
                "producto_nombre": producto.producto_nombre,
                "producto_precio": producto.producto_precio,
                "producto_stock": producto.producto_stock,
                "descripcion": producto.descripcion,
                "producto_foto": producto.producto_foto,
                "cantidad": item.cantidad
            })

        return {
            "id_carrito": carrito.id_carrito,
            "productos": productos_carrito
        }, 200

class VistaPagos(Resource):
    @jwt_required()
    def get(self):
        pagos = Pago.query.all()
        return [pago_schema.dump(pago) for pago in pagos], 200

class VistaFacturas(Resource):
    @jwt_required()
    def get(self):
        facturas = Factura.query.all()
        return facturas_schema.dump(facturas), 200



class VistaPagoTarjeta(Resource):
    @jwt_required()
    def get(self, id_pago):
        tarjeta = TarjetaDetalle.query.filter_by(id_pago=id_pago).first()
        if not tarjeta:
            return {"message": "Detalles de tarjeta no encontrados"}, 404
        return tarjeta_schema.dump(tarjeta), 200

class VistaPagoTransferencia(Resource):
    @jwt_required()
    def get(self, id_pago):
        transferencia = TransferenciaDetalle.query.filter_by(id_pago=id_pago).first()
        if not transferencia:
            return {"message": "Detalles de transferencia no encontrados"}, 404
        return transferencia_schema.dump(transferencia), 200

class VistaPagoPaypal(Resource):
    @jwt_required()
    def get(self, id_pago):
        paypal = PaypalDetalle.query.filter_by(id_pago=id_pago).first()
        if not paypal:
            return {"message": "Detalles de PayPal no encontrados"}, 404
        return paypal_schema.dump(paypal), 200

class VistaPago(Resource):
    @jwt_required()
    def post(self):
        # Obtener el id_usuario desde el token JWT
        id_usuario = get_jwt_identity()

        # Consultar el carrito del usuario
        carrito = Carrito.query.filter_by(id_usuario=id_usuario, procesado=False).first()

        # Verificar si el carrito existe y tiene productos
        if not carrito:
            return {"message": "No hay carrito encontrado o el carrito ya fue procesado"}, 400

        # Obtener el monto total del carrito
        monto_total = carrito.total

        # Obtener el método de pago del cuerpo de la solicitud
        metodo_pago = request.json.get('metodo_pago')

        # Crear un nuevo registro de pago
        nuevo_pago = Pago(
            id_carrito=carrito.id_carrito,
            monto=monto_total,
            metodo_pago=metodo_pago,
            estado='completado',  # Asumimos que el pago está pendiente
            fecha_pago=datetime.utcnow()  # Fecha actual en UTC
        )

        # Agregar el pago a la base de datos
        db.session.add(nuevo_pago)
        db.session.commit()

        # Obtener los productos del carrito y actualizamos el stock
        for carrito_producto in carrito.productos:
            producto = carrito_producto.producto  # Accedemos al producto desde la relación CarritoProducto
            if producto.producto_stock >= carrito_producto.cantidad:
                # Restamos la cantidad comprada del stock del producto
                producto.producto_stock -= carrito_producto.cantidad
            else:
                # Si no hay suficiente stock, devolvemos un mensaje de error
                return {"message": f"No hay suficiente stock para el producto {producto.producto_nombre}"}, 400
        
        # Guardar los cambios de stock
        db.session.commit()

        # Marcar el carrito como procesado
        carrito.procesado = True
        db.session.commit()

        # Crear un nuevo carrito para el usuario
        nuevo_carrito = Carrito(
            id_usuario=id_usuario,
            total=0,  # El nuevo carrito comienza vacío, con total 0
            procesado=False  # El nuevo carrito aún no está procesado
        )

        # Agregar el nuevo carrito a la base de datos
        db.session.add(nuevo_carrito)
        db.session.commit()

        return {"message": "Pago creado exitosamente, productos actualizados, nuevo carrito creado", "id_pago": nuevo_pago.id_pago}, 201

class VistaTarjeta(Resource):
    @jwt_required()
    def post(self):
        datos = request.json
        nueva_tarjeta = TarjetaDetalle(
            id_pago=datos.get('id_pago'),
            nombre_en_tarjeta=datos.get('nombre_en_tarjeta'),
            numero_tarjeta=datos.get('numero_tarjeta'),
            fecha_expiracion=datos.get('fecha_expiracion'),
            cvv=datos.get('cvv')
        )
        db.session.add(nueva_tarjeta)
        db.session.commit()
        return {"message": "Detalles de tarjeta guardados exitosamente"}, 201

class VistaTransferencia(Resource):
    @jwt_required()
    def post(self):
        datos = request.json
        nueva_transferencia = TransferenciaDetalle(
            id_pago=datos.get('id_pago'),
            nombre_titular=datos.get('nombre_titular'),  # Ahora se espera el nombre del titular
            banco_origen=datos.get('banco_origen'),
            numero_cuenta=datos.get('numero_cuenta'),
            comprobante_url=datos.get('comprobante_url')  # Si es que se incluye
        )
        db.session.add(nueva_transferencia)
        db.session.commit()
        return {"message": "Detalles de transferencia guardados exitosamente"}, 201

class VistaPaypal(Resource):
    @jwt_required()
    def post(self):
        datos = request.json
        nuevo_paypal = PaypalDetalle(
            id_pago=datos.get('id_pago'),
            email_paypal=datos.get('email_paypal'),  # Corregido el nombre
            confirmacion_id=datos.get('confirmacion_id')  # Corregido el nombre
        )
        db.session.add(nuevo_paypal)
        db.session.commit()
        return {"message": "Detalles de PayPal guardados exitosamente"}, 201



class VistaRolUsuario(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.filter_by(id=current_user_id).first()
        if usuario:
            return {'rol_id': usuario.rol_id}, 200
        else:
            return {'message': 'Usuario no encontrado'}, 404


class VistaProductosRecomendados(Resource):
    @jwt_required()
    def get(self):
        # Obtener el usuario desde el token JWT
        user_id = get_jwt_identity()

        # Obtener el carrito no procesado del usuario
        carrito = Carrito.query.filter_by(id_usuario=user_id, procesado=False).first()

        # Si el usuario no tiene un carrito activo, devolvemos todos los productos
        if not carrito:
            productos = Producto.query.all()
        else:
            # Obtener los productos que NO están en el carrito
            productos = Producto.query.filter(
                ~Producto.id_producto.in_(
                    db.session.query(CarritoProducto.id_producto)
                    .join(Carrito, Carrito.id_carrito == CarritoProducto.id_carrito)
                    .filter(Carrito.id_usuario == user_id)
                )
            ).all()

        # Convertir los productos a una lista de diccionarios
        productos_lista = ProductoSchema(many=True).dump(productos)

        return productos_lista, 200


class VistaFactura(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()

        if not data or 'id_pago' not in data:
            return {"error": "Falta el campo 'id_pago' en el cuerpo JSON"}, 400

        try:
            # 1. Obtener el pago
            pago = Pago.query.get(data['id_pago'])
            if not pago:
                return {"error": "Pago no encontrado"}, 404

            # 2. Obtener el carrito asociado a ese pago
            carrito = Carrito.query.get(pago.id_carrito)
            if not carrito:
                return {"error": "Carrito no encontrado para el pago"}, 404

            # 3. Calcular el total de la factura sumando los productos en el carrito y redondearlo
            total_factura = sum(cp.cantidad * cp.producto.producto_precio for cp in carrito.productos)
            total_factura_int = int(total_factura)  # Convertimos el total a entero

            # 4. Crear la factura con hora de Bogotá
            bogota_timezone = pytz.timezone('America/Bogota')
            fecha_bogota = datetime.now(bogota_timezone)

            nueva_factura = Factura(
                id_pago=pago.id_pago,
                factura_fecha=fecha_bogota,
                total=total_factura_int  # Asignamos el total como entero
            )

            db.session.add(nueva_factura)
            db.session.flush()  # Para obtener el id_factura antes del commit

            # 5. Crear detalles de factura por cada producto en el carrito
            for cp in carrito.productos:  # Suponiendo relación: carrito.productos -> CarritoProducto
                detalle = DetalleFactura(
                    id_factura=nueva_factura.id_factura,
                    id_producto=cp.producto.id_producto,
                    cantidad=cp.cantidad,
                    precio_unitario=cp.producto.producto_precio,
                    monto_total=int(cp.cantidad * cp.producto.producto_precio)  # Convertimos el monto total a entero
                )
                db.session.add(detalle)

            # 6. Confirmar todo
            db.session.commit()

            # 7. Obtener el correo del usuario asociado al pago
            carrito = Carrito.query.get(pago.id_carrito)  # Obtener el carrito asociado al pago
            if not carrito:
                return {"error": "No se encontró el carrito asociado al pago"}, 404

            usuario = Usuario.query.get(carrito.id_usuario)  # Obtener el usuario asociado al carrito
            if not usuario or not usuario.correo:
                return {"error": "No se encontró el correo electrónico del usuario"}, 404

            # 8. Crear el mensaje de correo electrónico
            msg = Message(
                'Factura de Compra - PHPhone',  # Asunto
                sender='dilanf1506@gmail.com',  # Correo del admin
                recipients=[usuario.correo]  # Correo del usuario
            )

            # Convertir la fecha y total a string con formato 'YYYY-MM-DD HH:MM:SS'
            factura_fecha_str = nueva_factura.factura_fecha.strftime('%Y-%m-%d %H:%M:%S')
            total_factura_str = f"${total_factura_int:,.0f}"  # Formatear el total con signo de pesos y miles

            # 9. Enviar el correo
            msg.html = render_template(
                'factura_email.html',
                factura_id=nueva_factura.id_factura,
                factura_fecha=factura_fecha_str,
                total=total_factura_int,  # Aquí mandamos el total formateado
                detalles=carrito.productos  # Enviamos los productos también
            )
            from flaskr import mail 
            # 9. Enviar el correo
            mail.send(msg)

            return {
                "message": "Factura y detalles creados exitosamente, y correo enviado.",
                "id_factura": nueva_factura.id_factura,
                "factura_fecha": factura_fecha_str,
                "total": total_factura_str  # Devolver el total formateado como cadena
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al crear factura: {str(e)}"}, 500




    @jwt_required()
    def get(self):
        facturas = Factura.query.all()
        return [
            {
                "id_factura": factura.id_factura,
                "id_pago": factura.id_pago,
                "factura_fecha": factura.factura_fecha
            } for factura in facturas
        ], 200


class VistaDetalleFactura(Resource):
    @jwt_required()
    def get(self, id_factura=None):
        if id_factura:
            # Buscar detalles de factura por id_factura
            detalles = DetalleFactura.query.filter_by(id_factura=id_factura).all()
            if not detalles:
                return {"message": "No se encontraron detalles para esta factura"}, 404
        else:
            # Obtener todos los detalles de facturas
            detalles = DetalleFactura.query.all()

        return [
            {
                "id_detalle_factura": detalle.id_detalle_factura,
                "id_factura": detalle.id_factura,
                "id_producto": detalle.id_producto,
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "monto_total": detalle.monto_total
            } for detalle in detalles
        ], 200

    @jwt_required()
    def post(self):
        data = request.get_json()

        if not data:
            return {"error": "No se envió un cuerpo JSON"}, 400

        required_fields = ['id_factura', 'id_producto', 'cantidad', 'precio_unitario', 'monto_total']
        for field in required_fields:
            if field not in data:
                return {"error": f"Falta el campo: {field}"}, 400

        # Validar que cantidad, precio_unitario y monto_total sean valores numéricos positivos
        if not isinstance(data['cantidad'], (int, float)) or data['cantidad'] <= 0:
            return {"error": "La cantidad debe ser un número positivo"}, 400

        if not isinstance(data['precio_unitario'], (int, float)) or data['precio_unitario'] <= 0:
            return {"error": "El precio unitario debe ser un número positivo"}, 400

        if not isinstance(data['monto_total'], (int, float)) or data['monto_total'] <= 0:
            return {"error": "El monto total debe ser un número positivo"}, 400

        try:
            nuevo_detalle = DetalleFactura(
                id_factura=data['id_factura'],
                id_producto=data['id_producto'],
                cantidad=data['cantidad'],
                precio_unitario=data['precio_unitario'],
                monto_total=data['monto_total']
            )

            db.session.add(nuevo_detalle)
            db.session.commit()

            return {
                "message": "Detalle de factura creado exitosamente",
                "id_detalle_factura": nuevo_detalle.id_detalle_factura
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
        

class VistaEnvio(Resource):
    @jwt_required()
    def post(self):
        id_usuario = get_jwt_identity()
        
        if not id_usuario:
            return {"message": "No se pudo identificar al usuario"}, 401

        datos_envio = request.get_json()

        if not datos_envio:
            return {"message": "No se recibieron datos en el cuerpo de la solicitud"}, 400

        campos_requeridos = ['direccion', 'ciudad', 'departamento', 'codigo_postal', 'pais']
        campos_faltantes = [campo for campo in campos_requeridos if campo not in datos_envio or not datos_envio[campo]]

        if campos_faltantes:
            return {"message": f"Faltan los siguientes campos requeridos: {', '.join(campos_faltantes)}"}, 400

        try:
            # Estados de envío con tiempos estimados y emojis
            estados_envio = [
                {
                    "estado": "Pedido recibido 🛒",
                    "descripcion": "Hemos recibido tu pedido correctamente",
                    "tiempo_estimado": "1 min",
                    "completado": False
                },
                {
                    "estado": "Procesando pago 💳",
                    "descripcion": "Verificamos los datos de tu pago",
                    "tiempo_estimado": "2 mins",
                    "completado": False
                },
                {
                    "estado": "Preparando tu pedido 👨‍🍳",
                    "descripcion": "Estamos preparando todo con cuidado",
                    "tiempo_estimado": "10 mins",
                    "completado": False
                },
                {
                    "estado": "Empacando productos 🎁",
                    "descripcion": "Todo está siendo empaquetado",
                    "tiempo_estimado": "5 mins",
                    "completado": False
                },
                {
                    "estado": "En bodega para despacho 📦",
                    "descripcion": "Tu pedido está listo para salir",
                    "tiempo_estimado": "3 mins",
                    "completado": False
                },
                {
                    "estado": "En camino a tu ubicación 🚚",
                    "descripcion": "Nuestro repartidor está en camino",
                    "tiempo_estimado": "20 mins",
                    "completado": False
                },
                {
                    "estado": "¡Pedido entregado! 🎉",
                    "descripcion": "Disfruta tu pedido",
                    "tiempo_estimado": "",
                    "completado": False
                }
            ]

            return {
                "mensaje": "Datos de envío procesados exitosamente",
                "estados": estados_envio,
                "tiempo_total_estimado": "40 mins",
                "fecha_estimada": (datetime.now() + timedelta(minutes=40)).strftime('%H:%M')
            }, 201

        except Exception as e:
            return {"error": f"Ocurrió un error al procesar el envío: {str(e)}"}, 500


class SeguimientoEnvio(Resource):
    @jwt_required()
    def get(self, id_envio):
        # En una implementación real, aquí buscarías el estado actual del envío
        # Pero para la simulación, avanzamos los estados cada 5-10 segundos
        
        # Simulamos un ID de envío válido
        if not id_envio:
            return {"message": "ID de envío no proporcionado"}, 400
        
        # Simulamos el avance del envío
        estados = [
            {"estado": "Pedido recibido 🛒", "completado": True},
            {"estado": "Procesando pago 💳", "completado": True},
            {"estado": "Preparando tu pedido 👨‍🍳", "completado": True},
            {"estado": "Empacando productos 🎁", "completado": False},
            {"estado": "En bodega para despacho 📦", "completado": False},
            {"estado": "En camino a tu ubicación 🚚", "completado": False},
            {"estado": "¡Pedido entregado! 🎉", "completado": False}
        ]
        
        # Avanzamos un estado cada vez que se consulta (para la simulación)
        for i, estado in enumerate(estados):
            if not estado["completado"]:
                estado["completado"] = True
                break
        
        return {
            "estado_actual": estados,
            "progreso": f"{int((sum(1 for e in estados if e['completado']) / len(estados)) * 100)}%"
        }, 200

class VistaAjusteStock(Resource):
    @jwt_required()
    def post(self, id_producto):
        # Verificar permisos (solo administradores pueden ajustar stock)
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        if usuario.rol_id != 1:  # Asumiendo que 1 es el rol de administrador
            return {"message": "No tienes permisos para realizar esta acción"}, 403

        data = request.get_json()
        cantidad = data.get('cantidad')
        motivo = data.get('motivo', 'Ajuste de stock')

        if not cantidad or not isinstance(cantidad, int):
            return {"message": "La cantidad debe ser un número entero"}, 400

        producto = Producto.query.get(id_producto)
        if not producto:
            return {"message": "Producto no encontrado"}, 404

        try:
            # Usamos el método ajustar_stock del modelo Producto
            registro = producto.ajustar_stock(cantidad, motivo)
            db.session.commit()
            
            return {
                "message": "Stock actualizado correctamente",
                "stock_anterior": registro.stock_anterior,
                "ajuste": registro.cantidad_ajuste,
                "nuevo_stock": registro.nuevo_stock,
                "fecha_ajuste": registro.fecha_ajuste.isoformat(),
                "motivo": registro.motivo
            }, 200
        except ValueError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error al actualizar el stock: {str(e)}"}, 500


class VistaHistorialStockProducto(Resource):
    @jwt_required()
    def get(self, id_producto):
        # Verificar permisos (solo administradores pueden ver el historial)
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        if usuario.rol_id != 1:  # Asumiendo que 1 es el rol de administrador
            return {"message": "No tienes permisos para ver este historial"}, 403

        producto = Producto.query.get(id_producto)
        if not producto:
            return {"message": "Producto no encontrado"}, 404

        # Obtener todo el historial ordenado por fecha descendente
        historial = HistorialStock.query.filter_by(id_producto=id_producto)\
                          .order_by(HistorialStock.fecha_ajuste.desc())\
                          .all()

        return historiales_stock_schema.dump(historial), 200


class VistaHistorialStockGeneral(Resource):
    @jwt_required()
    def get(self):
        # Verificar permisos (solo administradores pueden ver el historial)
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        if usuario.rol_id != 1:  # Asumiendo que 1 es el rol de administrador
            return {"message": "No tienes permisos para ver este historial"}, 403

        # Obtener todo el historial ordenado por fecha descendente
        historial = HistorialStock.query\
                      .join(Producto, HistorialStock.id_producto == Producto.id_producto)\
                      .order_by(HistorialStock.fecha_ajuste.desc())\
                      .all()

        # Añadir información del producto a cada registro
        historial_data = []
        for registro in historial:
            registro_data = historial_stock_schema.dump(registro)
            registro_data['producto_nombre'] = registro.producto.producto_nombre
            historial_data.append(registro_data)

        return historial_data, 200


class VistaStockProductos(Resource):
    @jwt_required()
    def get(self):
        # Verificar permisos (solo administradores pueden ver este reporte)
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        if usuario.rol_id != 1:  # Asumiendo que 1 es el rol de administrador
            return {"message": "No tienes permisos para ver este reporte"}, 403

        # Obtener todos los productos con su stock actual
        productos = Producto.query.order_by(Producto.producto_nombre).all()
        
        productos_data = []
        for producto in productos:
            producto_data = producto_schema.dump(producto)
            # Añadir información adicional si es necesario
            productos_data.append(producto_data)
        
        return productos_data, 200

class VistaReportesProductos(Resource):
    @jwt_required()
    def get(self):
        try:
            periodo = request.args.get('periodo', 'hoy')
            limite = request.args.get('limite', 10, type=int)

            if periodo not in ['hoy', 'semana', 'mes', 'año', 'personalizado']:
                return {'mensaje': 'Período no válido'}, 400

            # Zona horaria fija Bogotá
            tz = pytz.timezone('America/Bogota')
            ahora = datetime.now(tz)

            query = db.session.query(
                Producto.id_producto,
                Producto.producto_nombre,
                db.func.sum(DetalleFactura.cantidad).label('total_vendido')
            ).join(DetalleFactura, Producto.id_producto == DetalleFactura.id_producto
            ).join(Factura, DetalleFactura.id_factura == Factura.id_factura)

            if periodo == 'hoy':
                inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(Factura.factura_fecha >= inicio)
            elif periodo == 'semana':
                inicio = ahora - timedelta(days=7)
                query = query.filter(Factura.factura_fecha >= inicio)
            elif periodo == 'mes':
                inicio = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(Factura.factura_fecha >= inicio)
            elif periodo == 'año':
                inicio = ahora.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(Factura.factura_fecha >= inicio)
            elif periodo == 'personalizado':
                fecha_inicio = request.args.get('fecha_inicio')
                fecha_fin = request.args.get('fecha_fin')
                if not fecha_inicio or not fecha_fin:
                    return {'mensaje': 'Se requieren fecha_inicio y fecha_fin para período personalizado'}, 400
                try:
                    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').replace(tzinfo=tz)
                    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').replace(
                        hour=23, minute=59, second=59, tzinfo=tz)
                    query = query.filter(Factura.factura_fecha.between(fecha_inicio, fecha_fin))
                except ValueError:
                    return {'mensaje': 'Formato de fecha inválido. Use YYYY-MM-DD'}, 400

            resultados = query.group_by(Producto.id_producto, Producto.producto_nombre
                ).order_by(db.desc('total_vendido')
                ).limit(limite).all()

            if not resultados:
                return {'mensaje': 'No se encontraron ventas en el período especificado'}, 404
            total_general = sum([float(r.total_vendido) for r in resultados]) or 1  # Convertir a float
            reporte = [{
                'id_producto': r.id_producto,
                'producto_nombre': r.producto_nombre,
                'total_vendido': float(r.total_vendido),  # Convertir Decimal a float
                'porcentaje': round((float(r.total_vendido) / total_general) * 100, 2)  # Asegúrate de convertir aquí también
            } for r in resultados]
            return jsonify(reporte)

        except Exception as e:
            current_app.logger.error(f"Error en reportes: {str(e)}")
            return {'mensaje': 'Error interno al generar el reporte', 'error': str(e)}, 500
