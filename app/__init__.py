from flask import Flask
from .config import Config
from .extentions import db, migrate, bcrypt
from .routes import bps

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Blueprints
    for bp in bps:
        app.register_blueprint(bp)

    return app

