from flask import Flask
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from .config import Config
from .models import db
from .routes import bp as main_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    jwt = JWTManager(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(main_bp)

    SWAGGER_URL = '/swagger'
    API_URL = '/swagger.json'  

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Book Management API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
