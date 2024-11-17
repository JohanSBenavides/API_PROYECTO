from flask import request
from flaskr.modelos.modelos import Usuario
from flask_restful import Resource
from ..modelos import db
Usuario_schema = ()
class VistaUsuario(Resource):
    def get(self):
        return [Usuario_schema.dump(Usuario) for Usuario in Usuario.query.all()]

    def post(self):
        nuevo_Usuario = Usuario (
            id = request.json['id'],
            nombre = request.json ['nombre'],
            apellido = request.json['apellido'],
            usuariousuario = request.json ['usuariousuario'],
            usuarioclave = request.json['usuarioclave'],    
            usuarioemail= request.json['usuarioemail'],
            id_rol = request.json['id_rol'])
        db.session.add(nuevo_Usuario)
        db.session.commit()
        return Usuario_schema.dump(nuevo_Usuario)
       

    def put(self, id):
        Usuario = Usuario.query.get(id)
        if not Usuario:
            return 'Usuario no encontrado', 404
       
        Usuario.id = request.json.get('id', Usuario.id)
        Usuario.nombre = request.json.get('nombre',Usuario.nombre)
        Usuario.apellido = request.json.get('apellido',Usuario.nombre)
        Usuario.usuariousuario = request.json.get('usuariousuario', Usuario.nombreusuario)
        Usuario.usuarioclave = request.json.get('usuarioclave', Usuario.usuarioclave)
        Usuario.usuarioemail = request.json.get('usuarioemail', Usuario.usuarioemail)
        Usuario.id_rol = request.json.get('id_rol', Usuario.id_rol)

    def delete(self, id):
        Usuario = Usuario.query.get(id)
        if not Usuario:
            return 'Usuario no encontrado', 404
       
        db.session.delete(Usuario)
        db.session.commit()
        return 'El usuario fue eliminado' 