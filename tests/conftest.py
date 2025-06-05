import sys
import os
from pathlib import Path
import pytest
from flaskr import create_app
from flaskr.modelos import db

# Configuración de paths
project_root = str(Path(__file__).parent.parent.parent)  # Sube hasta API_PROYECTO
sys.path.insert(0, project_root)

@pytest.fixture(scope='session')
def app():
    """Fixture de aplicación con base de datos de pruebas"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:@localhost/phphone_test',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'secret-key-de-prueba',  # Clave secreta para JWT en pruebas
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_pre_ping': True,
            'pool_recycle': 3600,
        }
    })

    # Crear todas las tablas al inicio
    with app.app_context():
        db.create_all()

    yield app

    # Limpieza post-pruebas
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de pruebas"""
    return app.test_client()

@pytest.fixture
def session(app):
    """Sesión de base de datos con rollback automático"""
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()