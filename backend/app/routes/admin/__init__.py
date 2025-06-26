from flask import Blueprint

from .dashboard import dashboard_bp
from .users import users_bp
from .salons import salons_bp
from .services import services_bp
from .notifications import notifications_bp
from .reviews import reviews_bp

admin_bp = Blueprint('admin', __name__)

# Alt blueprint'leri register et
admin_bp.register_blueprint(dashboard_bp)
admin_bp.register_blueprint(users_bp)
admin_bp.register_blueprint(salons_bp)
admin_bp.register_blueprint(services_bp)
admin_bp.register_blueprint(notifications_bp)
admin_bp.register_blueprint(reviews_bp)
