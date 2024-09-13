import os

# Obtener la ruta absoluta del directorio que contiene este archivo
basedir = os.path.abspath(os.path.dirname(__file__))

# Clave secreta para la aplicación Flask
SECRET_KEY = "VARCHAR"

# URI de la base de datos para SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///datos.sqlite3'

# Desactivar el seguimiento de modificaciones de objetos en SQLAlchemy
SQLALCHEMY_TRACK_MODIFICATIONS = False