from flask import Flask
from dotenv import load_dotenv
from app.config import Config
from app.extensions import db, jwt, mail
from app.routes import register_routes  
from flask_cors import CORS

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions init
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    #  CORS aktif et (tüm domain'lere izin ver, sadece dev için)
    CORS(app, origins="http://localhost:4200", supports_credentials=True)

    # Route'lar
    register_routes(app)

    return app