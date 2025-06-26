from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Barber, Review
from .utils import is_barber

reviews_bp = Blueprint('barber_reviews', __name__, url_prefix='/barber/reviews')

@reviews_bp.route('', methods=['GET'])
@jwt_required()
def get_my_reviews():
    user_id = get_jwt_identity()
    if not is_barber(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    barber = Barber.query.filter_by(user_id=user_id).first()
    if not barber:
        return jsonify({'error': 'Berber profili bulunamadı'}), 404

    reviews = Review.query.filter_by(barber_id=barber.id).order_by(Review.created_at.desc()).all()

    result = [{
        'id': r.id,
        'customer_name': r.customer.name if r.customer else None,
        'salon_name': r.salon.name if r.salon else None,
        'appointment_id': r.appointment_id,
        'rating': r.rating,
        'comment': r.comment,
        'created_at': r.created_at.isoformat()
    } for r in reviews]

    return jsonify(result), 200
