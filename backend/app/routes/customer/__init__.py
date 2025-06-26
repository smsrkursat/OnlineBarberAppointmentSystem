from .appointments import appointments_bp
from .salons import salons_bp
from .reviews import reviews_bp
from .notifications import notifications_bp

from flask import Blueprint

customer_bp = Blueprint('customer', __name__)

customer_bp.register_blueprint(appointments_bp)
customer_bp.register_blueprint(salons_bp)
customer_bp.register_blueprint(reviews_bp)
customer_bp.register_blueprint(notifications_bp)
