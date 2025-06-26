from .auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.admin import admin_bp
from app.routes.salon_owner import owner_bp
from app.routes.barber import barber_bp
from app.routes.customer import customer_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(owner_bp, url_prefix='/api')
    app.register_blueprint(barber_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(customer_bp, url_prefix='/api')

