from flask import Blueprint
from .appointments import appointments_bp
from .invitations import invitations_bp
from .reviews import reviews_bp
from .notifications import notifications_bp

barber_bp = Blueprint('barber', __name__)
barber_bp.register_blueprint(appointments_bp)
barber_bp.register_blueprint(invitations_bp)
barber_bp.register_blueprint(reviews_bp)
barber_bp.register_blueprint(notifications_bp)
