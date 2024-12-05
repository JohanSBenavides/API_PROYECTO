from flaskr import create_app
from flaskr.modelos.modelos import Carrito, Categoria, DetalleCarrito, DetalleFactura, Envio, Orden, Pago, Producto, Rol, Usuario, Factura
from .modelos import db
from flask_restful import Api
from .vistas.vistas import VistaProductos, VistaUsuario, VistaUsuarios, VistaLogin, VistaSignIn, VistaCategoria, VistaCategorias

app = create_app('default')
app_context = app.app_context()
app_context.push()
db.create_all()

api = Api(app)
#Rutas para ver, editar o eliminar un id especifico
api.add_resource(VistaUsuario, '/usuario/<int:id_usuario>')
api.add_resource(VistaCategoria, '/categoria/<int:id_categoria>')


#rutas para ver todos y añadir
api.add_resource(VistaUsuarios, '/usuarios')
api.add_resource(VistaProductos, '/productos')
api.add_resource(VistaCategorias, '/categorias')

#rutas para login e iniciar sesion
api.add_resource(VistaLogin, '/login')
api.add_resource(VistaSignIn, '/signin')