import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from bookings.tasks import celery, make_celery

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.path.dirname(__file__), "..", "instance", "arbonaida.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
    db.init_app(app)

    with app.app_context():
        from . import models  # Importa los modelos
        from . import routes  # Importa las rutas
        db.create_all()  # Crea las tablas en la base de datos si no existen

    make_celery(app)
    return app
