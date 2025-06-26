from flask import Blueprint

from .salons import salons_bp
from .barbers import barbers_bp
from .invitations import invitations_bp
from .services import services_bp
from .promotions import promotions_bp
from .appointments import appointments_bp
from .reviews import reviews_bp
from .notifications import notifications_bp

owner_bp = Blueprint('owner', __name__)


owner_bp.register_blueprint(salons_bp)
owner_bp.register_blueprint(barbers_bp)
owner_bp.register_blueprint(invitations_bp)
owner_bp.register_blueprint(services_bp)
owner_bp.register_blueprint(promotions_bp)
owner_bp.register_blueprint(appointments_bp)
owner_bp.register_blueprint(reviews_bp)
owner_bp.register_blueprint(notifications_bp)
