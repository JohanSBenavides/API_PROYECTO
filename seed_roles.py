from flaskr import create_app
from flaskr.modelos import db, Rol, Usuario

def seed_roles():
    app = create_app()  # Crear la aplicación Flask
    with app.app_context():  # Asegurarse de que la app esté en contexto
        db.create_all()  # Crear todas las tablas de la base de datos si no existen

        # Inicialización de roles
        if not Rol.query.first():  # Si no existe ningún rol en la base de datos
            roles = [
                Rol(nombre_rol="ADMINISTRADOR"),  # Rol Administrador
                Rol(nombre_rol="CLIENTE")  # Rol Cliente
            ]
            db.session.bulk_save_objects(roles)  # Guardar los roles en la base de datos
            db.session.commit()  # Confirmar los cambios
            print("Roles inicializados correctamente.")
        else:
            print("Los roles ya están inicializados.")  # Si ya existen roles

        # Crear un superadmin si no existe
        if not Usuario.query.filter_by(correo="superadmin@example.com").first():  # Si no existe el superadmin
            superadmin = Usuario(
                nombre="Super Admin",
                numerodoc=1013598175,
                correo="dilanf1506@gmail.com",  
                contrasena="superadmin123", 
                rol_id=1  
            )
            db.session.add(superadmin)  # Añadir al superadmin a la base de datos
            db.session.commit()  # Confirmar los cambios
            print("Superadmin creado correctamente.")
        else:
            print("El superadmin ya existe.")  # Si ya existe un superadmin

# Esto asegura que el script solo se ejecuta cuando se llama directamente
if __name__ == "__main__":
    seed_roles()
