import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from flaskr.modelos import Usuario, Rol, Categoria, Producto, Carrito, CarritoProducto, Pago, TarjetaDetalle, TransferenciaDetalle, PaypalDetalle, db
from sqlalchemy.exc import IntegrityError

class TestUsuarioModel:
    """Pruebas unitarias para el modelo Usuario"""

    def test_creacion_usuario_valido(self, session):
        """Debe crear un usuario con datos válidos"""
        usuario = Usuario(
            nombre="Juan Pérez",
            numerodoc=123456789,
            correo="juan@example.com",
            contrasena="SecurePass123!"
        )
        session.add(usuario)
        session.commit()

        assert usuario.id_usuario is not None
        assert usuario.nombre == "Juan Pérez"
        assert usuario.verificar_contrasena("SecurePass123!") is True

    def test_correo_unico(self, session):
        """No debe permitir correos duplicados"""
        usuario1 = Usuario(
            correo="unique@example.com",
            contrasena="pass123",
            numerodoc=198765432,
            nombre="Usuario 1"
        )
        session.add(usuario1)
        session.commit()

        usuario2 = Usuario(
            correo="unique@example.com",  # Mismo correo
            contrasena="pass456",
            nombre="Usuario 2"
        )
        session.add(usuario2)
        
        with pytest.raises(IntegrityError):
            session.commit()

    def test_validacion_contrasena(self):
        """Debe validar la contraseña correctamente"""
        usuario = Usuario(correo="test@example.com")
        
        with pytest.raises(ValueError, match="no puede estar vacía"):
            usuario.contrasena = ""  # Contraseña vacía

        # Asignación correcta
        usuario.contrasena = "NuevaPass123"
        assert check_password_hash(usuario.contrasena_hash, "NuevaPass123")

    def test_propiedad_contrasena_no_legible(self):
        """No debe permitir leer la contraseña directamente"""
        usuario = Usuario(contrasena="secret")
        
        with pytest.raises(AttributeError, match="no es un atributo legible"):
            password = usuario.contrasena

    def test_relaciones(self, session):
        """Debe tener relaciones con Carrito y Envio configuradas"""
        usuario = Usuario(
            correo="relaciones@test.com",
            contrasena="test123",
            numerodoc=198765432,
            nombre="Test Relaciones"
        )
        session.add(usuario)
        session.commit()

        # Verificar relaciones
        assert isinstance(usuario.carritos, list)
        assert isinstance(usuario.envios, list)
        assert hasattr(usuario, 'rol_id')  # Clave foránea

    def test_campos_obligatorios(self, session):
        """Debe requerir correo y contraseña"""
        usuario = Usuario(nombre="Faltan campos")  # Sin correo/contrasena
        
        with pytest.raises(IntegrityError):
            session.add(usuario)
            session.commit()

class TestRolModel:
    """Pruebas unitarias para el modelo Rol"""

    def test_creacion_rol_valido(self, session):
        """Debe crear un rol con datos válidos"""
        rol = Rol(nombre_rol="Administrador")
        session.add(rol)
        session.commit()

        assert rol.rol_id is not None
        assert rol.nombre_rol == "Administrador"

    def test_nombre_rol_unico(self, session):
        """No debe permitir nombres de rol duplicados"""
        # Primero creamos un rol
        rol1 = Rol(nombre_rol="Cliente")
        session.add(rol1)
        session.commit()

        # Intentamos crear otro rol con el mismo nombre
        session.begin_nested()  # Usamos nested transaction para poder continuar después del error
        rol2 = Rol(nombre_rol="Cliente")
        session.add(rol2)
        
        with pytest.raises(IntegrityError):
            session.commit()
        
        session.rollback()  # Volvemos al estado anterior

    def test_longitud_nombre_rol(self):
        """Debe validar la longitud máxima del nombre del rol"""
        # Test de validación a nivel de aplicación (no esperamos IntegrityError)
        nombre_largo = "A" * 51
        with pytest.raises(ValueError):
            rol = Rol(nombre_rol=nombre_largo)

    def test_relacion_con_usuarios(self, session):
        """Debe tener relación con Usuarios configurada"""
        rol = Rol(nombre_rol="Moderador")
        session.add(rol)
        session.commit()
        usuario = Usuario(
            nombre="Usuario Test",
            correo="test@relacion.com",
            numerodoc=198765432,
            contrasena="test123",
            rol_id=rol.rol_id
        )
        session.add(usuario)
        session.commit()

        # Verificar la relación
        assert usuario.rol_id == rol.rol_id
        assert usuario in rol.usuarios

    def test_campos_obligatorios(self):
        """Debe requerir el nombre del rol"""
        with pytest.raises(ValueError):
            rol = Rol() 



class TestCategoriaModel:
    """Pruebas unitarias para el modelo Categoria"""
    
    def test_creacion_categoria_valida(self, session):
        """Debe crear una categoría con nombre válido"""
        categoria = Categoria(nombre="Electrónicos")
        session.add(categoria)
        session.commit()
        
        assert categoria.id_categoria is not None
        assert categoria.nombre == "Electrónicos"
    

class TestProductoModel:
    """Pruebas unitarias para el modelo Producto"""
    
    def test_creacion_producto_valido(self, session):
        """Debe crear un producto con datos válidos"""
        producto = Producto(
            producto_nombre="Smartphone X",
            producto_precio=999,
            producto_stock=50,
            descripcion="Último modelo con cámara profesional",
            producto_foto="smartphone.jpg",
            categoria_id=1
        )
        session.add(producto)
        session.commit()
        
        assert producto.id_producto is not None
        assert producto.producto_nombre == "Smartphone X"
        assert producto.producto_stock == 50
    
    def test_campos_obligatorios_producto(self, session):
        """Debe requerir todos los campos obligatorios"""
        producto_incompleto = Producto()  # Sin ningún campo requerido
        
        with pytest.raises(IntegrityError):
            session.add(producto_incompleto)
            session.commit()
    
    def test_ajuste_stock(self, session):
        """Debe ajustar correctamente el stock del producto"""
        # Crear producto de prueba
        producto = Producto(
            producto_nombre="Tablet",
            producto_precio=299,
            producto_stock=30,
            descripcion="Tablet 10 pulgadas",
            producto_foto="tablet.jpg",
            categoria_id=2
        )
        session.add(producto)
        session.commit()
        
        # Ajustar stock
        registro = producto.ajustar_stock(10, "Compra de proveedor")
        
        assert producto.producto_stock == 40
        assert registro.stock_anterior == 30
        assert registro.nuevo_stock == 40
        assert registro.motivo == "Compra de proveedor"
        
        # Verificar que no permite ajustes negativos
        with pytest.raises(ValueError, match="número positivo"):
            producto.ajustar_stock(-5)

class TestCarritoModel:
    """Pruebas unitarias para el modelo Carrito"""
    
    def test_creacion_carrito_valido(self, session):
        """Debe crear un carrito con datos válidos"""
        # Crear usuario de prueba
        usuario = Usuario(
            nombre="Cliente Test",
            correo="cliente@test.com",
            numerodoc=198765432,
            contrasena="test123"
        )
        session.add(usuario)
        session.commit()
        
        carrito = Carrito(
            id_usuario=usuario.id_usuario,
            total=0
        )
        session.add(carrito)
        session.commit()
        
        assert carrito.id_carrito is not None
        assert carrito.fecha is not None  # Se autogenera
        assert carrito.total == 0
        assert carrito.procesado is False
        assert carrito.usuario.id_usuario == usuario.id_usuario
    
    def test_relacion_con_productos(self, session):
        """Debe mantener relación con productos a través de CarritoProducto"""
        # Crear datos de prueba
        usuario = Usuario(id_usuario=90, nombre="Test", correo="test@test.com", numerodoc=198765432, contrasena="123")
        producto = Producto(
            producto_nombre="Producto Test",
            producto_precio=100,
            producto_stock=10,
            descripcion="Desc",
            producto_foto="test.jpg",
            categoria_id=1
        )
        carrito = Carrito(id_usuario=usuario.id_usuario, total=0)
        
        session.add_all([usuario, producto, carrito])
        session.commit()
        
        # Añadir producto al carrito
        carrito_producto = CarritoProducto(
            id_carrito=carrito.id_carrito,
            id_producto=producto.id_producto,
            cantidad=2
        )
        session.add(carrito_producto)
        session.commit()
        
        assert len(carrito.productos) == 1
        assert carrito.productos[0].producto.producto_nombre == "Producto Test"
        assert carrito.productos[0].cantidad == 2

class TestCarritoProductoModel:
    """Pruebas unitarias para el modelo CarritoProducto"""
    
    def test_creacion_carrito_producto_valido(self, session):
        """Debe crear una relación carrito-producto válida"""
        # Crear datos de prueba
        usuario = Usuario(id_usuario=20, nombre="Test", correo="testt@testt.com", numerodoc=198765432, contrasena="123")
        producto = Producto(
            producto_nombre="Producto Testt",
            producto_precio=100,
            producto_stock=10,
            descripcion="Desc",
            producto_foto="testt.jpg",
            categoria_id=1
        )
        carrito = Carrito(id_usuario=usuario.id_usuario, total=0)
        
        session.add_all([usuario, producto, carrito])
        session.commit()
        
        # Crear relación
        cp = CarritoProducto(
            id_carrito=carrito.id_carrito,
            id_producto=producto.id_producto,
            cantidad=3
        )
        session.add(cp)
        session.commit()
        
        assert cp.id_carrito_producto is not None
        assert cp.carrito.id_carrito == carrito.id_carrito
        assert cp.producto.id_producto == producto.id_producto
        assert cp.cantidad == 3
    
    def test_campos_obligatorios(self, session):
        """Debe requerir carrito, producto y cantidad"""
        # Intentar crear sin campos obligatorios
        cp = CarritoProducto()
        
        with pytest.raises(IntegrityError):
            session.add(cp)
            session.commit()

class TestPagoModel:
    """Pruebas unitarias para el modelo Pago"""

    def test_creacion_pago_valido(self, session):
        """Debe crear un pago con datos válidos"""
        # Crear carrito de prueba
        usuario = Usuario(
            id_usuario=21,
            nombre="Cliente Pago",
            correo="pago@test.com",
            numerodoc=198765432,
            contrasena="test123"
        )
        carrito = Carrito(id_usuario=usuario.id_usuario, total=1000)
        session.add_all([usuario, carrito])
        session.commit()

        pago = Pago(
            id_carrito=carrito.id_carrito,
            monto=1000,
            metodo_pago='tarjeta',
            estado='completado'
        )
        session.add(pago)
        session.commit()

        assert pago.id_pago is not None
        assert pago.monto == 1000
        assert pago.metodo_pago == 'tarjeta'
        assert pago.estado == 'completado'
        assert pago.fecha_pago is not None
        assert pago.id_carrito == carrito.id_carrito

    def test_campos_obligatorios(self, session):
        """Debe requerir monto y método de pago"""
        pago_incompleto = Pago()  # Sin campos obligatorios
        
        with pytest.raises(IntegrityError):
            session.add(pago_incompleto)
            session.commit()

    def test_estado_default(self, session):
        """Debe establecer 'completado' como estado por defecto"""
        usuario = Usuario(id_usuario=1, nombre="Test User", numerodoc="123456789", correo="default@gmail.com", contrasena="12345678") # Ajusta según tu modelo Usuario
        session.add(usuario)
        session.commit() 

        carrito = Carrito(id_usuario=usuario.id_usuario, total=500)
        session.add(carrito)
        session.commit()

        pago = Pago(
            id_carrito=carrito.id_carrito,
            monto=500,
            metodo_pago='transferencia'
        )
        session.add(pago)
        session.commit()

        assert pago.estado == 'completado'


class TestPaypalDetalleModel:
    """Pruebas unitarias para el modelo PaypalDetalle"""

    def test_creacion_paypal_valido(self, session):
        """Debe crear un detalle Paypal válido"""
        carrito = Carrito(id_carrito=20, id_usuario=1, total=750)
        pago = Pago(
            id_carrito=carrito.id_carrito,
            monto=750,
            metodo_pago='paypal'
        )
        session.add_all([carrito, pago])
        session.commit()

        detalle = PaypalDetalle(
            id_pago=pago.id_pago,
            email_paypal="comprador@example.com",
            confirmacion_id="PAYID-123456789"
        )
        session.add(detalle)
        session.commit()

        assert detalle.id_paypal is not None
        assert detalle.email_paypal == "comprador@example.com"
        assert detalle.pago.id_pago == pago.id_pago
        assert detalle.pago.metodo_pago == 'paypal'

    def test_relacion_unica_con_pago(self, session):
        """Un pago solo debe tener un detalle Paypal"""
        carrito = Carrito(id_carrito=21, id_usuario=1, total=800)
        pago = Pago(id_carrito=carrito.id_carrito, monto=800, metodo_pago='paypal')
        
        session.add_all([carrito, pago])
        session.flush() 

        detalle1 = PaypalDetalle(
            id_pago=pago.id_pago,
            email_paypal="test1@example.com",
            confirmacion_id=12345678
        )
        session.add(detalle1)
        session.commit() 

        detalle2 = PaypalDetalle(
            id_pago=pago.id_pago, 
            email_paypal="test2@example.com",
            confirmacion_id=12345678
        )
        session.add(detalle2)
        
        with pytest.raises(IntegrityError):
            session.commit() 


class TestTransferenciaDetalleModel:
    """Pruebas unitarias para el modelo TransferenciaDetalle"""

    def test_creacion_transferencia_valida(self, session):
        """Debe crear un detalle de transferencia válido"""
        carrito = Carrito(id_carrito= 23, id_usuario=1, total=1200)
        pago = Pago(
            id_carrito=carrito.id_carrito,
            monto=1200,
            metodo_pago='transferencia'
        )
        session.add_all([carrito, pago])
        session.commit()

        detalle = TransferenciaDetalle(
            id_pago=pago.id_pago,
            nombre_titular="Juan Pérez",
            banco_origen="Banco Nacional",
            numero_cuenta="1234567890",
            comprobante_url="http://example.com/comprobante.jpg"
        )
        session.add(detalle)
        session.commit()

        assert detalle.id_transferencia is not None
        assert detalle.nombre_titular == "Juan Pérez"
        assert detalle.banco_origen == "Banco Nacional"
        assert detalle.fecha_transferencia is not None
        assert detalle.pago.metodo_pago == 'transferencia'

    def test_campos_obligatorios(self, session):
        """Debe requerir nombre, banco y número de cuenta"""
        pago = Pago(id_carrito=1, monto=500, metodo_pago='transferencia')
        session.add(pago)
        session.commit()

        detalle_incompleto = TransferenciaDetalle(
            id_pago=pago.id_pago,
            # Faltan campos obligatorios
        )
        
        with pytest.raises(IntegrityError):
            session.add(detalle_incompleto)
            session.commit()


class TestTarjetaDetalleModel:
    """Pruebas unitarias para el modelo TarjetaDetalle"""

    def test_creacion_tarjeta_valida(self, session):
        """Debe crear un detalle de tarjeta válido"""
        carrito = Carrito(id_carrito=24, id_usuario=1, total=1500)
        pago = Pago(
            id_carrito=carrito.id_carrito,
            monto=1500,
            metodo_pago='tarjeta'
        )
        session.add_all([carrito, pago])
        session.commit()

        detalle = TarjetaDetalle(
            id_pago=pago.id_pago,
            nombre_en_tarjeta="JUAN PEREZ",
            fecha_expiracion="12/25"
        )
        # Asignar número y CVV usando los setters
        detalle.numero_tarjeta = "4111111111111111"
        detalle.cvv = "123"
        
        session.add(detalle)
        session.commit()

        assert detalle.id_tarjeta is not None
        assert detalle.nombre_en_tarjeta == "JUAN PEREZ"
        assert detalle.fecha_expiracion == "12/25"
        assert detalle.verificar_numero_tarjeta("4111111111111111") is True
        assert detalle.verificar_cvv("123") is True

    def test_no_acceso_directo_numero_cvv(self):
        """No debe permitir acceso directo al número de tarjeta o CVV"""
        detalle = TarjetaDetalle(
            id_pago=1,
            nombre_en_tarjeta="TEST USER",
            fecha_expiracion="01/30"
        )
        detalle.numero_tarjeta = "4222222222222"
        detalle.cvv = "456"

        with pytest.raises(AttributeError):
            numero = detalle.numero_tarjeta
        
        with pytest.raises(AttributeError):
            cvv = detalle.cvv


    def test_relacion_unica_con_pago(self, session):
        """Un pago solo debe tener un detalle de tarjeta"""
        pago = Pago(id_carrito=1, monto=600, metodo_pago='tarjeta')
        session.add(pago)
        session.flush()  # Asigna el id_pago

        detalle1 = TarjetaDetalle(
            id_pago=pago.id_pago,
            nombre_en_tarjeta="Primera Tarjeta",
            fecha_expiracion="01/25",
        )
        detalle1.numero_tarjeta = "5111111111111111"
        detalle1.cvv = 145  

        detalle2 = TarjetaDetalle(
            id_pago=pago.id_pago, 
            nombre_en_tarjeta="Segunda Tarjeta",
            fecha_expiracion="02/26",
        )
        detalle2.numero_tarjeta = "5222222222222222"
        detalle2.cvv = 765

        session.add(detalle1)
        session.commit()

        session.add(detalle2)
        with pytest.raises(IntegrityError):
            session.commit()