from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Barber, Salon
from .utils import is_owner

barbers_bp = Blueprint('salon_owner_barbers', __name__)

@barbers_bp.route('/owner/salon/barbers', methods=['GET'])
@jwt_required()
def get_owner_barbers():
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.filter_by(owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    barbers = Barber.query.filter_by(salon_id=salon.id).all()

    results = [{
        'id': b.id,
        'user_id': b.user_id,
        'rating': b.rating,
        'experience_years': b.experience_years,
        'bio': b.bio
    } for b in barbers]

    return jsonify(results), 200
