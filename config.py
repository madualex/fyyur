import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# TODO IMPLEMENT DATABASE URL
DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
DB_USER = os.getenv('DB_USER', 'alexmadu')
DB_PASSWORD = os.getenv('DB_PASSWORD', '242842')
DB_NAME = os.getenv('DB_NAME', 'postgres')

DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

SQLALCHEMY_DATABASE_URI = DB_PATH
