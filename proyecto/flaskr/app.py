from flaskr.modelos import db
from flaskr import create_app
app = create_app('default')
app_context = app.app_context()
app_context.push()
db.init_app(app)
db.create_all()


from flask import Flask, request

app = Flask(__name__)

@app.route('/username/<username>/password/<password>', methods=['GET', 'POST'])
def login(username, password):
    app.logger.info(f'Solicitud de la ruta {request.path}')
    return f"Tu username es {username}."

if __name__ == '__main__':
    app.run(debug=True)

@app.route ('/username/<username>/certificado/<certificado>', methods=['GET', 'POST'])
def certificado(username, certificado):
    app.logger.info(f'solicitud de la ruta {request.path}')
    return f"querido usuario {username}, tu certificado es {certificado}"   
