import os
import re
import pytz
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask import request, current_app, jsonify
from flask_restful import Resource, reqparse
from flask_mail import Message
from flask import current_app
from flask import request, render_template
from flask import render_template
from sqlalchemy.exc import IntegrityError, NoResultFound
from flaskr.modelos.esquemas import PaypalDetalleSchema, TransferenciaDetalleSchema, TarjetaDetalleSchema, FacturaSchema, HistorialStockSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..modelos import db, Usuario, TarjetaDetalle, TransferenciaDetalle, PaypalDetalle, Producto, Categoria, CarritoProductoSchema, CarritoProducto, Rol, UsuarioSchema, ProductoSchema, CategoriaSchema, RolSchema, PagoSchema, EnvioSchema, OrdenSchema, CarritoSchema, FacturaSchema, DetalleFacturaSchema, DetalleFactura, Factura, Pago, Orden, Envio, Carrito, HistorialStock

# Uso de los schemas creados en modelos
usuario_schema = UsuarioSchema()
producto_schema = ProductoSchema()
categoria_schema = CategoriaSchema()
carrito_schema = CarritoSchema()
factura_schema = FacturaSchema()
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
    def get(self):
        usuarios = Usuario.query.all()
        return [usuario_schema.dump(usuario) for usuario in usuarios], 200

    def post(self):
        if not all(key in request.json for key in ['nombre', 'numerodoc', 'correo', 'contrasena']):
            return {"message": "Faltan campos obligatorios"}, 400
        if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', request.json["nombre"]):
            return {"message": "El nombre solo debe contener letras y espacios"}, 400
        if not str(request.json["numerodoc"]).isdigit():
            return {"message": "El número de documento debe contener solo números"}, 400
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', request.json["correo"]):
            return {"message": "Formato de correo electrónico inválido"}, 400
        if not re.match(r'^[A-Za-z0-9]{8,16}$', request.json["contrasena"]):
            return {"message": "La contraseña debe tener entre 8 y 16 caracteres alfanuméricos"}, 400
        if Usuario.query.filter_by(correo=request.json["correo"]).first():
            return {"message": "El correo ya está registrado"}, 400
        if Usuario.query.filter_by(numerodoc=request.json["numerodoc"]).first():
            return {"message": "El número de documento ya está registrado"}, 400
        rol_cliente = Rol.query.filter_by(nombre_rol="Cliente").first()
        if not rol_cliente:
            return {"message": "Rol Cliente no configurado en el sistema"}, 500

        try:
            nuevo_usuario = Usuario(
                nombre=request.json["nombre"],
                numerodoc=int(request.json["numerodoc"]),  
                correo=request.json["correo"],
                rol_id=rol_cliente.rol_id
            )
            nuevo_usuario.contrasena = request.json["contrasena"]  # Esto generará el hash
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            return {"message": "Usuario creado exitosamente"}, 201
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error al crear usuario: {str(e)}"}, 500


class VistaUsuario(Resource):
    @jwt_required()
    def put(self, id_usuario):
        try:
            # Obtener usuario dentro del contexto de la sesión
            usuario = Usuario.query.get(id_usuario)
            if not usuario:
                db.session.rollback()
                return {'mensaje': 'El usuario no existe'}, 404

            # Validar correo único
            nuevo_correo = request.json.get('correo')
            if nuevo_correo and nuevo_correo != usuario.correo:
                if Usuario.query.filter(Usuario.correo == nuevo_correo, Usuario.id_usuario != id_usuario).first():
                    db.session.rollback()
                    return {'mensaje': 'El correo ya está registrado'}, 400

            # Actualizar campos
            if 'nombre' in request.json:
                usuario.nombre = request.json['nombre']
            if 'numerodoc' in request.json:
                usuario.numerodoc = request.json['numerodoc']
            if 'correo' in request.json:
                usuario.correo = request.json['correo']
            
            # Actualizar rol si se proporciona
            if 'rol_id' in request.json:
                rol = Rol.query.get(request.json['rol_id'])
                if not rol:
                    db.session.rollback()
                    return {'mensaje': 'Rol no encontrado'}, 400
                usuario.rol_id = request.json['rol_id']

            # Actualizar contraseña si se proporciona
            if 'contrasena' in request.json:
                usuario.contrasena = request.json['contrasena']

            db.session.commit()
            return {'mensaje': 'Usuario actualizado correctamente'}, 200

        except NoResultFound:
            db.session.rollback()
            return {'mensaje': 'Recurso no encontrado'}, 404
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Error de integridad: {str(e)}")
            return {'mensaje': 'Error de integridad en la base de datos'}, 400
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error inesperado: {str(e)}")
            return {'mensaje': 'Error interno del servidor'}, 500
        
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

class VistaPerfilUsuario(Resource):
    @jwt_required()
    def get(self):
        id_usuario = get_jwt_identity()
        usuario = Usuario.query.get(id_usuario)
        
        if not usuario:
            return {"message": "Usuario no encontrado"}, 404
            
        return usuario_schema.dump(usuario), 200

    @jwt_required()
    def put(self):
        id_usuario = get_jwt_identity()
        usuario = Usuario.query.get(id_usuario)
        
        if not usuario:
            return {"message": "Usuario no encontrado"}, 404

        data = request.json

        # Validación obligatoria de contraseña actual
        if 'contrasena_actual' not in data or not usuario.verificar_contrasena(data['contrasena_actual']):
            return {"message": "Contraseña actual incorrecta"}, 401

        # Validación del nombre
        if 'nombre' in data:
            if not re.match("^[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+$", data['nombre']):
                return {"message": "El nombre solo debe contener letras y espacios"}, 400
            usuario.nombre = data['nombre']

        # Validación del documento (MODIFICADO)
        if 'numerodoc' in data:
            # Convertir a string primero
            numerodoc_str = str(data['numerodoc'])
            if not re.match("^\\d{1,15}$", numerodoc_str):
                return {"message": "El documento debe contener solo números (máx. 15 dígitos)"}, 400
            usuario.numerodoc = numerodoc_str  # Guardar como string

        # Validación del correo
        if 'correo' in data:
            if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", data['correo']):
                return {"message": "Ingrese un correo electrónico válido"}, 400
            if Usuario.query.filter(Usuario.correo == data['correo'], Usuario.id_usuario != id_usuario).first():
                return {"message": "Este correo ya está registrado por otro usuario"}, 400
            usuario.correo = data['correo']

        # Validación de nueva contraseña (solo si se proporciona)
        if 'nueva_contrasena' in data and data['nueva_contrasena']:
            if not re.match("^[A-Za-z0-9]{8,16}$", data['nueva_contrasena']):
                return {"message": "La nueva contraseña debe ser alfanumérica (8-16 caracteres)"}, 400
            if data['nueva_contrasena'] != data.get('confirmar_contrasena', ''):
                return {"message": "Las nuevas contraseñas no coinciden"}, 400
            usuario.contrasena = data['nueva_contrasena']

        db.session.commit()
        
        return {
            "message": "Perfil actualizado exitosamente",
            "usuario": usuario_schema.dump(usuario)
        }, 200

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
        data = request.get_json(force=True)  # obtener JSON, forzando si necesario

        nombre = data.get("nombre", "").strip()
        correo = data.get("correo", "").strip()
        contrasena = data.get("contrasena", "")
        numerodoc = data.get("numerodoc")

        # Validaciones básicas
        if not nombre:
            return {"mensaje": "El nombre es obligatorio"}, 400
        if not correo:
            return {"mensaje": "El correo es obligatorio"}, 400
        if contrasena.strip() == "":
            return {"mensaje": "La contraseña no puede estar vacía"}, 400
        if numerodoc is None:
            return {"mensaje": "El número de documento es obligatorio"}, 400
        if not isinstance(numerodoc, int):
            return {"mensaje": "El número de documento debe ser un número entero"}, 400

        # Verificar si el correo ya existe
        usuario_existente = Usuario.query.filter_by(correo=correo).first()
        if usuario_existente:
            return {"mensaje": "El correo ya existe"}, 400

        # Obtener el rol "Cliente" para asignar por defecto
        rol_cliente = Rol.query.filter_by(nombre_rol="CLIENTE").first()
        if not rol_cliente:
            return {"mensaje": "El rol Cliente no está configurado en la base de datos"}, 500

        try:
            nuevo_usuario = Usuario(
                nombre=nombre,
                correo=correo,
                numerodoc=numerodoc,
                rol_id=rol_cliente.rol_id
            )
            nuevo_usuario.contrasena = contrasena 

            db.session.add(nuevo_usuario)
            db.session.commit()

            return {"mensaje": "Usuario creado exitosamente"}, 201

        except Exception as e:
            db.session.rollback()
            return {"mensaje": f"Error al crear usuario: {str(e)}"}, 500

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
        
        # Validaciones
        if not datos.get('numero_tarjeta') or not re.match(r'^\d{16}$', str(datos.get('numero_tarjeta'))):
            return {"mensaje": "El número de tarjeta debe tener exactamente 16 dígitos"}, 400
            
        if not datos.get('nombre_en_tarjeta') or not re.match(r'^[a-zA-Z\s]+$', datos.get('nombre_en_tarjeta')):
            return {"mensaje": "El nombre en la tarjeta solo debe contener letras"}, 400
            
        if not datos.get('cvv') or not re.match(r'^\d{3}$', str(datos.get('cvv'))):
            return {"mensaje": "El CVV debe tener exactamente 3 dígitos"}, 400
            
        if not datos.get('fecha_expiracion') or not re.match(r'^\d{4}$', str(datos.get('fecha_expiracion'))):
            return {"mensaje": "La fecha de expiración debe tener 4 dígitos (MMAA)"}, 400
            
        # Validar fecha no expirada
        try:
            mes = int(str(datos.get('fecha_expiracion'))[:2])
            ano = int(str(datos.get('fecha_expiracion'))[2:]) + 2000
            if ano < datetime.now().year or (ano == datetime.now().year and mes < datetime.now().month):
                return {"mensaje": "La tarjeta está expirada"}, 400
        except:
            return {"mensaje": "Formato de fecha inválido"}, 400

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
        
        # Validaciones
        if not datos.get('nombre_titular') or not re.match(r'^[a-zA-Z\s]+$', datos.get('nombre_titular')):
            return {"mensaje": "El nombre del titular solo debe contener letras"}, 400
            
        if not datos.get('banco_origen') or not re.match(r'^[a-zA-Z\s]+$', datos.get('banco_origen')):
            return {"mensaje": "El nombre del banco solo debe contener letras"}, 400
            
        if not datos.get('numero_cuenta') or not re.match(r'^\d{1,16}$', str(datos.get('numero_cuenta'))):
            return {"mensaje": "El número de cuenta debe contener solo números (máximo 16 dígitos)"}, 400
            
        if datos.get('comprobante_url') and not re.match(r'^[a-zA-Z0-9]{1,30}$', datos.get('comprobante_url')):
            return {"mensaje": "El URL del comprobante debe contener solo letras y números (máximo 30 caracteres)"}, 400

        nueva_transferencia = TransferenciaDetalle(
            id_pago=datos.get('id_pago'),
            nombre_titular=datos.get('nombre_titular'),
            banco_origen=datos.get('banco_origen'),
            numero_cuenta=datos.get('numero_cuenta'),
            comprobante_url=datos.get('comprobante_url')
        )
        db.session.add(nueva_transferencia)
        db.session.commit()
        return {"message": "Detalles de transferencia guardados exitosamente"}, 201

class VistaPaypal(Resource):
    @jwt_required()
    def post(self):
        datos = request.json
        
        # Validaciones
        if not datos.get('email_paypal') or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', datos.get('email_paypal')):
            return {"mensaje": "Por favor ingrese un correo electrónico válido para PayPal"}, 400
            
        if not datos.get('confirmacion_id') or not re.match(r'^\d+$', str(datos.get('confirmacion_id'))):
            return {"mensaje": "El ID de confirmación de PayPal debe contener solo números"}, 400

        nuevo_paypal = PaypalDetalle(
            id_pago=datos.get('id_pago'),
            email_paypal=datos.get('email_paypal'),
            confirmacion_id=datos.get('confirmacion_id')
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
            # Buscar detalles de factura por id_factura con join a Producto
            detalles = db.session.query(
                DetalleFactura,
                Producto.producto_nombre
            ).join(
                Producto,
                DetalleFactura.id_producto == Producto.id_producto
            ).filter(
                DetalleFactura.id_factura == id_factura
            ).all()
            
            if not detalles:
                return {"message": "No se encontraron detalles para esta factura"}, 404
            
            return [
                {
                    "id_detalle_factura": detalle.DetalleFactura.id_detalle_factura,
                    "id_factura": detalle.DetalleFactura.id_factura,
                    "id_producto": detalle.DetalleFactura.id_producto,
                    "producto_nombre": detalle.producto_nombre,  # Nombre del producto incluido
                    "cantidad": detalle.DetalleFactura.cantidad,
                    "precio_unitario": detalle.DetalleFactura.precio_unitario,
                    "monto_total": detalle.DetalleFactura.monto_total
                } for detalle in detalles
            ], 200
        else:
            # Obtener todos los detalles de facturas (versión básica sin join para mantener performance)
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
        
class VistaUltimaFactura(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        
        # Obtener la última factura del usuario
        factura = Factura.query.join(Pago).join(Carrito).filter(
            Carrito.id_usuario == usuario_id
        ).order_by(Factura.factura_fecha.desc()).first()
        
        if not factura:
            return {"error": "No se encontraron facturas para este usuario"}, 404
            
        return factura_schema.dump(factura), 200
        

class VistaEnvio(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()

        # Validar campos requeridos
        required_fields = ['direccion', 'ciudad', 'departamento', 'codigo_postal', 'pais', 'id_factura']
        for field in required_fields:
            if field not in data:
                return {"error": f"Falta el campo '{field}' en el cuerpo JSON"}, 400

        try:
            # Obtener el ID del usuario desde el token JWT
            usuario_id = get_jwt_identity()
            factura = Factura.query.get(data['id_factura'])

            # Obtener el pago asociado a la factura
            pago = Pago.query.get(factura.id_pago)
            if not pago:
                return {"error": "No se encontró el pago asociado a la factura"}, 404

            # Crear zona horaria de Bogotá
            bogota_timezone = pytz.timezone('America/Bogota')
            fecha_bogota = datetime.now(bogota_timezone)

            # Crear nuevo envío
            nuevo_envio = Envio(
                direccion=data['direccion'],
                ciudad=data['ciudad'],
                departamento=data['departamento'],
                codigo_postal=data['codigo_postal'],
                pais=data['pais'],
                estado_envio=data.get('estado_envio', "Empacando"),
                fecha_creacion=fecha_bogota,
                usuario_id=usuario_id,
                id_factura=data['id_factura']
            )

            db.session.add(nuevo_envio)
            db.session.flush()  # Para obtener el ID del envío

            # Calcular el monto total de la factura
            detalles_factura = DetalleFactura.query.filter_by(id_factura=factura.id_factura).all()
            monto_total = sum(detalle.monto_total for detalle in detalles_factura)

            # Crear nueva orden asociada al envío y factura
            nueva_orden = Orden(
                id_usuario=usuario_id,
                id_factura=data['id_factura'],
                fecha_orden=fecha_bogota,
                monto_total=monto_total,
                estado='enviada'  # Estado inicial
            )

            db.session.add(nueva_orden)
            db.session.commit()

            # Formatear fechas para la respuesta
            fecha_creacion_str = nuevo_envio.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            fecha_orden_str = nueva_orden.fecha_orden.strftime('%Y-%m-%d %H:%M:%S')

            return {
                "message": "Envío y orden creados exitosamente",
                "envio": envio_schema.dump(nuevo_envio),
                "orden": orden_schema.dump(nueva_orden)
            }, 201

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al crear envío y orden: {str(e)}")
            return {"error": f"Error al crear envío y orden: {str(e)}"}, 500
        
##ESTADOS DEL ENVIO 


class VistaEstadoEnvio(Resource):
    @jwt_required()
    def get(self, id_orden):
        try:
            # Obtener el usuario actual desde el token JWT
            usuario_id = get_jwt_identity()
            usuario = Usuario.query.get(usuario_id)
            
            if not usuario:
                return {'error': 'Usuario no encontrado'}, 404
            
            # Buscar el envío asociado a la orden
            query = Envio.query \
                .join(Factura, Envio.id_factura == Factura.id_factura) \
                .join(Orden, Factura.id_factura == Orden.id_factura) \
                .filter(Orden.id_orden == id_orden)
            
            # Si no es admin (rol_id != 1), filtrar por usuario
            if getattr(usuario, 'rol_id', 0) != 1:
                query = query.filter(Envio.usuario_id == usuario_id)
            
            envio = query.first()
            
            if not envio:
                return {'error': 'Envío no encontrado o no tienes permisos'}, 404
                
            # Formatear la respuesta
            response_data = {
                'id_envio': envio.id,
                'estado_envio': envio.estado_envio,
                'fecha_creacion': envio.fecha_creacion.isoformat(),
                'direccion_completa': {
                    'direccion': envio.direccion,
                    'ciudad': envio.ciudad,
                    'departamento': envio.departamento,
                    'codigo_postal': envio.codigo_postal,
                    'pais': envio.pais
                },
                'detalles_factura': {
                    'id_factura': envio.id_factura
                },
                'detalles_usuario': {
                    'usuario_id': envio.usuario_id,
                    'nombre_usuario': envio.usuario.nombre if envio.usuario else None
                },
                'estados_disponibles': list(Envio.ESTADOS_VALIDOS) if hasattr(Envio, 'ESTADOS_VALIDOS') else []
            }
            
            if envio.fecha_actualizacion:
                response_data['ultima_actualizacion'] = envio.fecha_actualizacion.isoformat()
                
            return response_data, 200
            
        except Exception as e:
            current_app.logger.error(f"Error en VistaEstadoEnvio: {str(e)}", exc_info=True)
            return {'error': 'Error al obtener el estado de envío'}, 500

estado_parser = reqparse.RequestParser()
estado_parser.add_argument('nuevo_estado', type=str, required=True, help='Nuevo estado es requerido')

class VistaEnviosAdmin(Resource):
    @jwt_required()
    def get(self):
        # Verificar si el usuario es admin (rol_id = 1)
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        if not usuario or getattr(usuario, 'rol_id', 0) != 1:
            return {'error': 'Acceso no autorizado'}, 403

        # Obtener todos los envíos con detalles de usuario
        envios = Envio.query.join(Usuario).all()
        
        # Formatear respuesta
        envios_data = []
        for envio in envios:
            envios_data.append({
                'id_envio': envio.id,
                'usuario_id': envio.usuario_id,
                'nombre_usuario': envio.usuario.nombre,
                'estado_actual': envio.estado_envio,
                'fecha_creacion': envio.fecha_creacion.isoformat(),
                'id_factura': envio.id_factura
            })
        
        return {'envios': envios_data}, 200

class VistaActualizarEstadoAdmin(Resource):
    @jwt_required()
    def patch(self, id_envio):
        # Verificar permisos de admin (rol_id = 1)
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        if not usuario or getattr(usuario, 'rol_id', 0) != 1:
            return {'error': 'Acceso no autorizado'}, 403

        args = estado_parser.parse_args()
        nuevo_estado = args['nuevo_estado']

        # Validar estado
        estados_validos = ['Empacando', 'Validando', 'En Camino a Tu Hogar', 'Tu Pedido Ya Ha Sido Entregado']
        if nuevo_estado not in estados_validos:
            return {'error': f'Estado no válido. Los estados permitidos son: {", ".join(estados_validos)}'}, 400

        # Actualizar envío
        envio = Envio.query.get(id_envio)
        if not envio:
            return {'error': 'Envío no encontrado'}, 404

        envio.estado_envio = nuevo_estado
        envio.fecha_actualizacion = datetime.utcnow()
        
        try:
            db.session.commit()
            return {'mensaje': 'Estado actualizado correctamente'}, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al actualizar estado: {str(e)}", exc_info=True)
            return {'error': 'Error al actualizar el estado'}, 500


        
        
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
        
class VistaPedidosUsuario(Resource):
    @jwt_required()
    def get(self):
        id_usuario = get_jwt_identity()
        ordenes = Orden.query.filter_by(id_usuario=id_usuario).all()
        
        if not ordenes:
            return {"message": "No se encontraron pedidos para este usuario"}, 404
        
        pedidos = []
        for orden in ordenes:
            factura = Factura.query.get(orden.id_factura)
            detalles_factura = DetalleFactura.query.filter_by(id_factura=factura.id_factura).all()
            pago = Pago.query.get(factura.id_pago)
            
            # Cambia esta línea para usar la relación con factura
            envio = Envio.query.filter_by(id_factura=factura.id_factura).first()
            
            productos = []
            for detalle in detalles_factura:
                producto = Producto.query.get(detalle.id_producto)
                productos.append({
                    "id_producto": producto.id_producto,
                    "nombre": producto.producto_nombre,
                    "precio_unitario": detalle.precio_unitario,
                    "cantidad": detalle.cantidad,
                    "subtotal": detalle.monto_total,
                    "imagen": producto.producto_foto
                })
            
            pedidos.append({
                "id_orden": orden.id_orden,
                "fecha": orden.fecha_orden.strftime('%Y-%m-%d %H:%M:%S'),
                "estado": orden.estado,
                "total": orden.monto_total,
                "metodo_pago": pago.metodo_pago,
                "estado_pago": pago.estado,
                "direccion_envio": {
                    "direccion": envio.direccion if envio else None,
                    "ciudad": envio.ciudad if envio else None,
                    "estado_envio": envio.estado_envio if envio else None
                } if envio else None,
                "productos": productos
            })
        
        return {"pedidos": pedidos}, 200
    
class VistaProductosBajoStock(Resource):
    @jwt_required()
    def get(self):
        # Verificar que el usuario es administrador
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario or usuario.rol_id != 1:  # Asumiendo que 1 es admin
            return {"message": "No autorizado"}, 403

        # Obtener productos con menos de 10 unidades
        productos_bajo_stock = Producto.query.filter(
            Producto.producto_stock < 10
        ).all()

        # Formatear la respuesta
        productos_formateados = [{
            "id_producto": producto.id_producto,
            "nombre": producto.producto_nombre,
            "stock_actual": producto.producto_stock,
            "precio": producto.producto_precio,
            "foto": producto.producto_foto
        } for producto in productos_bajo_stock]

        return {
            "count": len(productos_bajo_stock),
            "productos": productos_formateados
        }, 200