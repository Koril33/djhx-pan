from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

jwt = JWTManager()
db = SQLAlchemy()

def init_app_extension(app):
    jwt.init_app(app)
    db.init_app(app)