import pytest
from flask import json
from flask_jwt_extended import create_access_token
from flaskr.modelos import Usuario, Rol, Factura, DetalleFactura, Producto, Pago, Categoria, Carrito, CarritoProducto, db
from io import BytesIO
import os
from datetime import datetime
import pytz
from unittest.mock import patch, MagicMock


class TestVistaUsuarios:
    """Pruebas integradas para la VistaUsuarios"""
    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        """Configuración inicial para cada test"""
        self.client = client
        with self.client.application.app_context():
            db.session.query(Usuario).delete()
            db.session.query(Rol).delete()

            admin = Rol(nombre_rol="Administrador")
            cliente = Rol(nombre_rol="Cliente")
            db.session.add_all([admin, cliente])
            db.session.commit()

    def test_crear_usuario_valido(self):
        """Debe crear un usuario con datos válidos"""
        datos_usuario = {
            "nombre": "Ana López",
            "numerodoc": "1234567890",
            "correo": "ana@gmail.com",
            "contrasena": "123456789"
        }

        response = self.client.post('/usuarios', 
                                 data=json.dumps(datos_usuario),
                                 content_type='application/json')
        
        assert response.status_code == 201
        assert response.json["message"] == "Usuario creado exitosamente"

    def test_crear_usuario_campos_faltantes(self):
        """Debe fallar si faltan campos obligatorios"""
        datos_incompletos = {
            "nombre": "Usuario Incompleto",
            "correo": "incompleto@gmail.com"
        }

        response = self.client.post('/usuarios',
                                  data=json.dumps(datos_incompletos),
                                  content_type='application/json')

        assert response.status_code == 400
        assert "Faltan campos obligatorios" in response.json["message"]

    def test_crear_usuario_correo_duplicado(self):
        """Debe fallar si el correo ya está registrado"""
        datos_usuario1 = {
            "nombre": "Usuario correo",
            "numerodoc": "111111111",
            "correo": "duplicado@gmail.com",
            "contrasena": "12345678"
        }

        self.client.post('/usuarios',
                        data=json.dumps(datos_usuario1),
                        content_type='application/json')

        datos_usuario2 = {
            "nombre": "Usuario correo dup",
            "numerodoc": "222222222",
            "correo": "duplicado@gmail.com",  
            "contrasena": "123456789"
        }

        response = self.client.post('/usuarios',
                                  data=json.dumps(datos_usuario2),
                                  content_type='application/json')

        assert response.status_code == 400
        assert "El correo ya está registrado" in response.json["message"]

    def test_crear_usuario_documento_duplicado(self):
        """Debe fallar si el número de documento ya está registrado"""
        datos_usuario1 = {
            "nombre": "Usuario documento",
            "numerodoc": "333333333",
            "correo": "doc1@gmail.com",
            "contrasena": "98765432111"
        }

        self.client.post('/usuarios',
                        data=json.dumps(datos_usuario1),
                        content_type='application/json')

        datos_usuario2 = {
            "nombre": "Usuario documento",
            "numerodoc": "333333333", 
            "correo": "doc2@gmail.com",
            "contrasena": "987654321"
        }

        response = self.client.post('/usuarios',
                                  data=json.dumps(datos_usuario2),
                                  content_type='application/json')

        assert response.status_code == 400
        assert "El número de documento ya está registrado" in response.json["message"]

    def test_validacion_formato_nombre(self):
        """Debe fallar si el nombre contiene caracteres inválidos"""
        datos_invalidos = {
            "nombre": "Usuario 123",  # Números no permitidos
            "numerodoc": "444444444",
            "correo": "nombre@invalido.com",
            "contrasena": "pass123"
        }

        response = self.client.post('/usuarios',
                                  data=json.dumps(datos_invalidos),
                                  content_type='application/json')

        assert response.status_code == 400
        assert "El nombre solo debe contener letras y espacios" in response.json["message"]

    def test_validacion_formato_documento(self):
        """Debe fallar si el documento no es numérico o es muy largo"""
        datos_invalidos = {
            "nombre": "Usuario Válido",
            "numerodoc": "123ABC456", 
            "correo": "doc@invalido.com",
            "contrasena": "pass123"
        }

        response = self.client.post('/usuarios',
                                  data=json.dumps(datos_invalidos),
                                  content_type='application/json')

        assert response.status_code == 400
        assert "El número de documento debe contener solo números" in response.json["message"]

    def test_validacion_formato_correo(self):
        """Debe fallar si el correo no tiene formato válido"""
        datos_invalidos = {
            "nombre": "Dilan",
            "numerodoc": "555555555",
            "correo": "correosinarroba",
            "contrasena": "pass123"
        }

        response = self.client.post('/usuarios',
                                  data=json.dumps(datos_invalidos),
                                  content_type='application/json')

        assert response.status_code == 400
        assert "Formato de correo electrónico inválido" in response.json["message"]

    def test_validacion_contrasena(self):
        """Debe fallar si la contraseña no cumple con los requisitos"""
        datos_invalidos = {
            "nombre": "Usuario exitoso",
            "numerodoc": "666666666",
            "correo": "contrasena@invalida.com",
            "contrasena": "123Hola" 
        }

        response = self.client.post('/usuarios',
                                  data=json.dumps(datos_invalidos),
                                  content_type='application/json')

        assert response.status_code == 400
        assert "La contraseña debe tener entre 8 y 16 caracteres alfanuméricos" in response.json["message"]


class TestVistaUsuario:
    """Pruebas integradas para VistaUsuario (actualización de usuario)"""

    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        """Configuración inicial para cada test"""
        self.client = client
        
        with self.client.application.app_context():
            db.session.rollback()
            db.session.query(Usuario).delete()
            db.session.query(Rol).delete()
            db.session.commit()

            self.rol_admin = Rol(nombre_rol="Administrador")
            self.rol_cliente = Rol(nombre_rol="Cliente")
            db.session.add_all([self.rol_admin, self.rol_cliente])
            db.session.commit()
            db.session.refresh(self.rol_admin)
            db.session.refresh(self.rol_cliente)

            self.rol_admin_id = self.rol_admin.rol_id
            self.rol_cliente_id = self.rol_cliente.rol_id

            self.usuario_prueba = Usuario(
                nombre="Usuario Original",
                numerodoc=123456789,
                correo="original@gmail.com",
                contrasena="123456789",
                rol_id=self.rol_cliente_id
            )
            db.session.add(self.usuario_prueba)
            db.session.commit()
            db.session.refresh(self.usuario_prueba)

            self.token = create_access_token(identity=str(self.usuario_prueba.id_usuario))

    def test_actualizar_usuario_valido(self):
        """Debe actualizar correctamente un usuario existente"""
        datos_actualizacion = {
            "nombre": "Usuario Modificado",
            "numerodoc": 987654321,
            "correo": "modificado@gmail.com",
            "rol_id": self.rol_cliente_id
        }

        response = self.client.put(
            f'/usuario/{self.usuario_prueba.id_usuario}',
            data=json.dumps(datos_actualizacion),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.token}'}
        )

        assert response.status_code == 200
        assert response.json["mensaje"] == "Usuario actualizado correctamente"

        with self.client.application.app_context():
            usuario = Usuario.query.get(self.usuario_prueba.id_usuario)
            rol = Rol.query.get(self.rol_cliente_id)
            
            assert usuario.nombre == "Usuario Modificado"
            assert usuario.numerodoc == 987654321
            assert usuario.correo == "modificado@gmail.com"
            assert usuario.rol_id == rol.rol_id

class TestVistaProductos:
    """Pruebas integradas para VistaProductos"""

    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        self.client = client

        with self.client.application.app_context():
            db.session.rollback()
            db.session.query(Producto).delete()
            db.session.query(Categoria).delete()
            db.session.commit()

            self.categoria = Categoria(nombre="Categoría Test")
            db.session.add(self.categoria)
            db.session.commit()
            db.session.refresh(self.categoria)
            self.categoria_id = self.categoria.id_categoria

            self.producto_prueba = Producto(
                producto_nombre="Producto Test",
                producto_precio=100,
                producto_stock=10,
                descripcion="Descripción de prueba",
                producto_foto="foto.jpg",
                categoria_id=self.categoria_id
            )
            db.session.add(self.producto_prueba)
            db.session.commit()
            db.session.refresh(self.producto_prueba)
            #TOKENN
            self.token = create_access_token(identity="test_user")

    def test_productos_filtrados(self):
        """Debe obtener productos filtrados correctamente"""
        response = self.client.get('/productos')
        assert response.status_code == 200
        data = response.json
        assert any(p['producto_nombre'] == "Producto Test" for p in data)

        # Filtrar por nombre
        response = self.client.get('/productos?q=Producto')
        assert response.status_code == 200
        data = response.json
        assert any("Producto Test" in p['producto_nombre'] for p in data)

        # Filtrar por rango de precio
        response = self.client.get('/productos?min_price=50&max_price=150')
        assert response.status_code == 200
        data = response.json
        assert any(p['producto_precio'] == 100 for p in data)

        # Filtrar por categoría
        response = self.client.get(f'/productos?category_id={self.categoria_id}')
        assert response.status_code == 200
        data = response.json
        assert any(p['categoria_id'] == self.categoria_id for p in data)

        # Filtrar por stock disponible
        response = self.client.get('/productos?in_stock=true')
        assert response.status_code == 200
        data = response.json
        assert all(p['producto_stock'] > 0 for p in data)

    def test_crear_producto_valido(self):
        os.makedirs('static/uploads', exist_ok=True)

        data = {
            'producto_nombre': 'Producto Nuevo',
            'producto_precio': '50',
            'producto_stock': '5',
            'categoria_id': str(self.categoria_id),
            'descripcion': 'Descripción nueva',
            'producto_foto': (BytesIO(b'test'), 'prueba.jpg')
        }

        response = self.client.post(
            '/productos',
            data=data,
            headers={'Authorization': f'Bearer {self.token}'},
            content_type='multipart/form-data'
        )

        if response.status_code != 201:
            print("Error detalle:", response.json)

        assert response.status_code == 201
        assert response.json['mensaje'] == "Producto creado exitosamente"

        with self.client.application.app_context():
            producto = Producto.query.filter_by(producto_nombre='Producto Nuevo').first()
            assert producto is not None
            assert producto.producto_precio == 50
            assert producto.producto_stock == 5
            assert producto.categoria_id == self.categoria_id
            assert producto.descripcion == 'Descripción nueva'
            assert producto.producto_foto == 'prueba.jpg'


    def test_sin_imagen_devuelve_error(self):
        """Debe devolver error si no se envía imagen"""

        data = {
            'producto_nombre': 'Producto Sin Imagen',
            'producto_precio': '50',
            'producto_stock': '5',
            'categoria_id': str(self.categoria_id),
            'descripcion': 'nueva descrip'
        }

        response = self.client.post(
            '/productos',
            data=data,
            headers={'Authorization': f'Bearer {self.token}'},
            content_type='multipart/form-data'
        )

        assert response.status_code == 400
        assert response.json['message'] == 'No se ha enviado una imagen para el producto'

class TestVistaProducto:
    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        self.client = client

        with self.client.application.app_context():
            # Limpiar la tabla productos
            db.session.query(Producto).delete()
            db.session.commit()

            # Crear un producto de prueba
            self.producto = Producto(
                producto_nombre="Producto Test",
                producto_precio=100,
                producto_stock=10,
                descripcion="Descripcion test",
                producto_foto="foto_test.jpg",
                categoria_id=1
            )
            db.session.add(self.producto)
            db.session.commit()
            db.session.refresh(self.producto)

            self.token = create_access_token(identity="testuser")
            ruta_foto = os.path.join('static/uploads', self.producto.producto_foto)
            if not os.path.exists(ruta_foto):
                with open(ruta_foto, 'wb') as f:
                    f.write(b'test')

    def test_actualizar_producto_con_imagen(self):
        """Debe actualizar producto y cambiar imagen correctamente"""
        data = {
            'producto_nombre': 'Producto Actualizado',
            'producto_precio': '150',
            'producto_stock': '20',
            'descripcion': 'Descripción nueva',
            'categoria_id': '2',
            'producto_foto': (BytesIO(b'nueva imagen'), 'nueva_imagen.jpg')
        }

        response = self.client.put(
            f'/productos/{self.producto.id_producto}',
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {self.token}'}
        )

        assert response.status_code == 200
        json_resp = response.json
        assert json_resp['producto_nombre'] == 'Producto Actualizado'
        assert json_resp['producto_precio'] == 150
        assert json_resp['producto_stock'] == 20
        assert json_resp['descripcion'] == 'Descripción nueva'
        assert json_resp['categoria_id'] == 2
        assert json_resp['producto_foto'] == 'nueva_imagen.jpg'

        # Verificar en base de datos
        with self.client.application.app_context():
            prod_db = Producto.query.get(self.producto.id_producto)
            assert prod_db.producto_nombre == 'Producto Actualizado'
            assert prod_db.producto_foto == 'nueva_imagen.jpg'

    def test_actualizar_producto_sin_imagen(self):
        """Debe actualizar producto sin cambiar la imagen"""
        data = {
            'producto_nombre': 'Producto Solo Texto',
            'producto_precio': '200',
            'producto_stock': '30',
            'descripcion': 'Sin imagen nueva',
            'categoria_id': '3'
        }

        response = self.client.put(
            f'/productos/{self.producto.id_producto}',
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {self.token}'}
        )

        assert response.status_code == 200
        json_resp = response.json
        assert json_resp['producto_nombre'] == 'Producto Solo Texto'
        assert json_resp['producto_foto'] == self.producto.producto_foto

    def test_producto_no_existente(self):
        """Debe devolver 404 al actualizar producto inexistente"""
        data = {
            'producto_nombre': 'No existe'
        }
        response = self.client.put(
            '/productos/9999',
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        assert response.status_code == 404
        assert response.json['message'] == 'El producto no existe'

    def test_delete_producto_exitoso(self):
        """Debe eliminar un producto correctamente"""
        response = self.client.delete(
            f'/productos/{self.producto.id_producto}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        assert response.status_code == 200
        assert response.json['message'] == 'Producto eliminado'

        with self.client.application.app_context():
            prod_db = Producto.query.get(self.producto.id_producto)
            assert prod_db is None

    def test_delete_producto_no_existente(self):
        """Debe devolver 404 al eliminar producto que no existe"""
        response = self.client.delete(
            '/productos/9999',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        assert response.status_code == 404
        assert response.json['message'] == 'Producto no encontrado'
class TestVistaLogin:
    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        self.client = client

        with self.client.application.app_context():
            db.session.rollback()
            db.session.query(Carrito).delete()
            db.session.query(Usuario).delete()
            db.session.query(Rol).delete()
            db.session.commit()

            self.rol_admin = Rol(nombre_rol="Administrador")
            self.rol_cliente = Rol(nombre_rol="Cliente")
            db.session.add_all([self.rol_admin, self.rol_cliente])
            db.session.commit()
            db.session.refresh(self.rol_admin)
            db.session.refresh(self.rol_cliente)

            self.rol_cliente_id = self.rol_cliente.rol_id

            self.usuario = Usuario(
                nombre="Usuario Test",
                numerodoc=12345678,
                correo="test@gmail.com",
                rol_id=self.rol_cliente_id
            )
            self.usuario.contrasena = "123456789"
            db.session.add(self.usuario)
            db.session.commit()
            db.session.refresh(self.usuario)

            self.usuario_rol_id = self.usuario.rol_id

    def test_login_exitoso(self):
        payload = {
            "correo": "test@gmail.com",
            "contrasena": "123456789"
        }

        response = self.client.post('/login', json=payload)

        assert response.status_code == 200
        json_resp = response.json
        assert json_resp['mensaje'] == "Inicio de sesión exitoso"
        assert 'token' in json_resp
        assert json_resp['rol'] == self.usuario_rol_id  
        assert 'carrito' in json_resp

    def test_login_usuario_incorrecto(self):
        """Debe fallar al iniciar sesión con usuario incorrecto"""
        payload = {
            "correo": "noexiste@gmail.com",
            "contrasena": "123456789"
        }

        response = self.client.post('/login', json=payload)
        assert response.status_code == 401
        assert response.json['mensaje'] == "Usuario o contraseña incorrectos"

    def test_login_contrasena_incorrecta(self):
        """Debe fallar al iniciar sesión con contraseña incorrecta"""
        payload = {
            "correo": "test@gmail.com",
            "contrasena": "contrasena_incorrecta"
        }

        response = self.client.post('/login', json=payload)
        assert response.status_code == 401
        assert response.json['mensaje'] == "Usuario o contraseña incorrectos"

class TestVistaSignIn:
    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        self.client = client

        with self.client.application.app_context():
            db.session.rollback()
            db.session.query(Usuario).delete()
            db.session.query(Rol).delete()
            db.session.commit()

            self.rol_admin = Rol(nombre_rol="Administrador")
            self.rol_cliente = Rol(nombre_rol="Cliente")
            db.session.add_all([self.rol_admin, self.rol_cliente])
            db.session.commit()
            db.session.refresh(self.rol_cliente)

            self.rol_cliente_id = self.rol_cliente.rol_id

    def test_signin_exitoso(self):
        """Debe registrar un usuario nuevo correctamente"""
        payload = {
            "nombre": "Nuevo Dilan",
            "numerodoc": 98765432,
            "correo": "nuevod@gmail.com",
            "contrasena": "123456789"
        }

        response = self.client.post('/signin', json=payload)

        assert response.status_code == 201
        json_resp = response.json
        assert json_resp['mensaje'] == "Usuario creado exitosamente"

        # Verificar que el usuario está en BD con rol cliente
        with self.client.application.app_context():
            usuario = Usuario.query.filter_by(correo=payload['correo']).first()
            assert usuario is not None
            assert usuario.nombre == payload['nombre']
            assert usuario.numerodoc == payload['numerodoc']
            assert usuario.rol_id == self.rol_cliente_id
            assert usuario.verificar_contrasena(payload['contrasena']) is True

    def test_signin_correo_existente(self):
        """Debe fallar al intentar registrar un usuario con correo ya existente"""
        with self.client.application.app_context():
            usuario_existente = Usuario(
                nombre="Existente",
                numerodoc=11111111,
                correo="existente@example.com",
                rol_id=self.rol_cliente_id
            )
            usuario_existente.contrasena = "password123"
            db.session.add(usuario_existente)
            db.session.commit()

        payload = {
            "nombre": "Otro Usuario",
            "numerodoc": 22222222,
            "correo": "existente@example.com",
            "contrasena": "otra_pass"
        }

        response = self.client.post('/signin', json=payload)

        assert response.status_code == 400
        json_resp = response.json
        assert "correo ya existe" in json_resp['mensaje'].lower()

    def test_signin_contrasena_vacia(self):
        """Debe fallar si la contraseña está vacía o sólo espacios"""
        payload = {
            "nombre": "Usuario Vacío",
            "numerodoc": 33333333,
            "correo": "vacío@example.com",
            "contrasena": "   "
        }

        response = self.client.post('/signin', json=payload)

        assert response.status_code == 400
        json_resp = response.json
        assert "contraseña no puede estar vacía" in json_resp['mensaje'].lower()

class TestVistaCarrito:

    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.client = client

        with self.client.application.app_context():
            # Limpiar tablas
            db.session.query(CarritoProducto).delete()
            db.session.query(Carrito).delete()
            db.session.query(Producto).delete()
            db.session.query(Usuario).delete()
            db.session.query(Rol).delete()
            db.session.commit()

            # Crear rol y usuario
            rol_cliente = Rol(nombre_rol="Cliente")
            db.session.add(rol_cliente)
            db.session.commit()

            usuario = Usuario(
                nombre="Test User",
                correo="testuser@example.com",
                numerodoc=12345678,
                rol_id=rol_cliente.rol_id
            )
            usuario.contrasena = "testpass"
            db.session.add(usuario)

            producto = Producto(
                producto_nombre="Producto Test",
                producto_precio=100,
                producto_stock=10,
                descripcion="Descripcion test",
                producto_foto="foto_test.jpg",
                categoria_id=1
            )
            db.session.add(producto)
            db.session.commit()

            self.usuario = usuario
            self.rol_cliente = rol_cliente
            self.producto = producto
            self.token = create_access_token(identity=str(usuario.id_usuario))


    def test_crea_carrito_si_no_existe(self):
        headers = {"Authorization": f"Bearer {self.token}"}

        response = self.client.post('/carrito', headers=headers)
        assert response.status_code == 201
        data = response.json
        assert data["id_usuario"] == self.usuario.id_usuario
        assert data["total"] == 0
        assert data["procesado"] is False

        # Si se vuelve a crear, debe devolver el mismo carrito activo
        response2 = self.client.post('/carrito', headers=headers)
        assert response2.status_code == 201
        assert response2.json["id_carrito"] == data["id_carrito"]

    def test_obtiene_carrito_existente(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        with self.client.application.app_context():
            carrito = Carrito(id_usuario=self.usuario.id_usuario, total=200)
            db.session.add(carrito)
            db.session.commit()
            carrito_id = carrito.id_carrito  # Guardar id para usar fuera

        response = self.client.get('/carrito', headers=headers)
        assert response.status_code == 200
        assert response.json["id_carrito"] == carrito_id

    def test_sin_carrito_activo_devuelve_404(self):
        headers = {"Authorization": f"Bearer {self.token}"}

        response = self.client.get('/carrito', headers=headers)
        assert response.status_code == 404
        assert "no se encontró" in response.json["message"].lower()

    def test_delete_sin_producto_en_carrito_rechaza(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        with self.client.application.app_context():
            carrito = Carrito(id_usuario=self.usuario.id_usuario, total=0)
            db.session.add(carrito)
            db.session.commit()
            carrito_id = carrito.id_carrito 

        payload = {"id_producto": 9999}
        response = self.client.delete(f'/carrito/{carrito_id}', json=payload, headers=headers)
        assert response.status_code == 404
        assert "producto no encontrado" in response.json["message"].lower()

class TestVistaPago:

    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.client = client

        with self.client.application.app_context():
            # Limpiar tablas
            db.session.query(CarritoProducto).delete()
            db.session.query(Pago).delete()
            db.session.query(CarritoProducto).delete()
            db.session.query(Carrito).delete()
            db.session.query(Carrito).delete()
            db.session.query(Producto).delete()
            db.session.query(Usuario).delete()
            db.session.query(Rol).delete()
            db.session.query(Pago).delete()
            db.session.commit()

            # Crear rol y usuario
            rol_cliente = Rol(nombre_rol="Cliente")
            db.session.add(rol_cliente)
            db.session.commit()

            usuario = Usuario(
                nombre="Test User",
                correo="testuser@example.com",
                numerodoc=12345678,
                rol_id=rol_cliente.rol_id
            )
            usuario.contrasena = "testpass"
            db.session.add(usuario)

            producto = Producto(
                producto_nombre="Producto Test",
                producto_precio=100,
                producto_stock=10,
                descripcion="Descripcion test",
                producto_foto="foto_test.jpg",
                categoria_id=1
            )
            db.session.add(producto)
            db.session.commit()

            self.usuario_id = usuario.id_usuario
            self.rol_cliente = rol_cliente
            self.producto_id = producto.id_producto
            self.token = create_access_token(identity=str(usuario.id_usuario))


    def test_pago_exitoso(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        
        with self.client.application.app_context():
            # Primero obtenemos todos los IDs necesarios
            producto_id = self.producto_id
            usuario_id = self.usuario_id

            
            # Luego obtenemos los objetos frescos desde la base de datos
            producto = Producto.query.get(producto_id)
            precio = producto.producto_precio

            # Crear carrito de compras
            carrito = Carrito(
                id_usuario=usuario_id, 
                total=precio * 2, 
                procesado=False
            )
            db.session.add(carrito)
            db.session.commit()

            # Agregar producto al carrito
            carrito_producto = CarritoProducto(
                id_carrito=carrito.id_carrito,
                id_producto=producto_id,
                cantidad=2
            )
            db.session.add(carrito_producto)
            db.session.commit()

            carrito_id = carrito.id_carrito

        # Realizar pago
        payload = {"metodo_pago": "tarjeta"}
        response = self.client.post(
            '/pago', 
            json=payload, 
            headers=headers
        )

        # Verificaciones
        assert response.status_code == 201
        data = response.json
        assert "id_pago" in data
        assert "Pago creado exitosamente" in data["message"]

        with self.client.application.app_context():
            # Verificar pago en base de datos
            pago = Pago.query.get(data["id_pago"])
            assert pago is not None
            assert pago.id_carrito == carrito_id
            assert pago.monto == precio * 2
            assert pago.metodo_pago == "tarjeta"
            assert pago.estado == "completado"

            # Verificar stock actualizado
            producto_actualizado = Producto.query.get(producto_id)
            assert producto_actualizado.producto_stock == 8  # 10 inicial - 2 comprados

            # Verificar carrito marcado como procesado
            carrito_actualizado = Carrito.query.get(carrito_id)
            assert carrito_actualizado.procesado is True

            # Verificar nuevo carrito creado
            nuevo_carrito = Carrito.query.filter_by(
                id_usuario=usuario_id, 
                procesado=False
            ).order_by(Carrito.id_carrito.desc()).first()
            assert nuevo_carrito is not None
            assert nuevo_carrito.id_carrito != carrito_id
            assert nuevo_carrito.total == 0

    def test_post_pago_sin_carrito_activo(self):
        headers = {"Authorization": f"Bearer {self.token}"}

        # No se crea carrito alguno, entonces debe fallar
        payload = {"metodo_pago": "tarjeta"}
        response = self.client.post(
            '/pago', 
            json=payload, 
            headers=headers
        )
        
        assert response.status_code == 400
        assert "no hay carrito encontrado" in response.json["message"].lower()

class TestVistaFactura:
    """Pruebas integradas para VistaFactura"""

    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        """Configuración inicial para cada test"""
        self.client = client

        with self.client.application.app_context():
            # Limpiar todas las tablas relacionadas
            db.session.query(DetalleFactura).delete()
            db.session.query(Factura).delete()
            db.session.query(CarritoProducto).delete()
            db.session.query(Pago).delete()
            db.session.query(Carrito).delete()
            db.session.query(Producto).delete()
            db.session.query(Usuario).delete()
            db.session.query(Rol).delete()
            db.session.commit()

            # Crear roles
            rol_cliente = Rol(nombre_rol="Cliente")
            db.session.add(rol_cliente)
            db.session.commit()
            self.rol_id = rol_cliente.rol_id

            # Crear usuario
            usuario = Usuario(
                nombre="Usuario Test",
                correo="test@example.com",
                numerodoc="12345678",
                rol_id=self.rol_id
            )
            usuario.contrasena = "password123"
            db.session.add(usuario)
            db.session.commit()
            self.usuario_id = usuario.id_usuario

            # Crear producto
            producto = Producto(
                producto_nombre="Producto Test",
                producto_precio=15000,
                producto_stock=10,
                descripcion="Descripción test",
                producto_foto="test.jpg",
                categoria_id=1
            )
            db.session.add(producto)
            db.session.commit()
            self.producto_id = producto.id_producto

            # Crear carrito
            carrito = Carrito(
                id_usuario=self.usuario_id,
                total=30000,
                procesado=True
            )
            db.session.add(carrito)
            db.session.commit()
            self.carrito_id = carrito.id_carrito

            # Agregar producto al carrito
            carrito_producto = CarritoProducto(
                id_carrito=self.carrito_id,
                id_producto=self.producto_id,
                cantidad=2
            )
            db.session.add(carrito_producto)
            db.session.commit()

            # Crear pago
            pago = Pago(
                id_carrito=self.carrito_id,
                monto=30000,
                metodo_pago="tarjeta",
                estado="completado"
            )
            db.session.add(pago)
            db.session.commit()
            self.pago_id = pago.id_pago

            # Token JWT para autenticación
            self.token = create_access_token(identity=str(self.usuario_id))


    def test_crear_factura_exitosa(self):
        """Debe crear una factura correctamente con todos sus detalles"""
        payload = {
            "id_pago": self.pago_id
        }

        response = self.client.post(
            '/factura',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.token}'}
        )

        assert response.status_code == 201

        # Verificar respuesta JSON
        json_data = response.json

        # Validar campos que sí vienen en la respuesta
        assert "id_factura" in json_data
        assert json_data["total"] == "$30,000"
        assert "factura_fecha" in json_data
        assert "message" in json_data
        assert json_data["message"] == "Factura y detalles creados exitosamente, y correo enviado."



    def test_crear_factura_sin_id_pago(self):
        """Debe fallar si no se proporciona el id_pago"""
        payload = {}  # Falta el campo id_pago

        response = self.client.post(
            '/factura',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.token}'}
        )

        assert response.status_code == 400
        assert "error" in response.json
        assert "Falta el campo 'id_pago'" in response.json["error"]

    def test_crear_factura_pago_no_existente(self):
        """Debe fallar si el pago no existe"""
        payload = {
            "id_pago": 9999  # ID que no existe
        }

        response = self.client.post(
            '/factura',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.token}'}
        )

        assert response.status_code == 404
        assert "error" in response.json
        assert "Pago no encontrado" in response.json["error"]
