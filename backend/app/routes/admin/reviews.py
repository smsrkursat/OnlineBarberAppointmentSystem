from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Review, Salon, Barber, User
from app.routes.admin.utils import is_admin

reviews_bp = Blueprint('admin_reviews', __name__)

@reviews_bp.route('/admin/reviews', methods=['GET'])
@jwt_required()
def get_all_reviews():
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    reviews = Review.query.all()
    result = []
    for r in reviews:
        result.append({
            'id': r.id,
            'comment': r.comment,
            'rating': r.rating,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M'),
            'salon_name': r.salon.name if r.salon else None,
            'barber_name': r.barber.user.name if r.barber and r.barber.user else None,
            'customer_name': r.customer.name if r.customer else None
        })
    return jsonify(result), 200 