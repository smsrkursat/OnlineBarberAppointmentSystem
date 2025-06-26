from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import User, UserRole, Salon, Review
from .utils import is_owner

reviews_bp = Blueprint('salon_owner_reviews', __name__)

@reviews_bp.route('/owner/reviews', methods=['GET'])
@jwt_required()
def get_owner_reviews():
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salons = Salon.query.filter_by(owner_id=user_id).all()
    salon_ids = [s.id for s in salons]

    reviews = Review.query.filter(Review.salon_id.in_(salon_ids)).order_by(Review.created_at.desc()).all()

    result = []
    for r in reviews:
        result.append({
            'id': r.id,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.isoformat(),
            'customer_name': r.customer.name if r.customer else None,
            'salon_name': r.salon.name if r.salon else None,
            'barber_name': r.barber.user.name if r.barber and r.barber.user else None
        })

    return jsonify(result), 200
