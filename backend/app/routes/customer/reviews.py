from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Review, Salon
from app.extensions import db
from .utils import is_customer

reviews_bp = Blueprint('customer_reviews', __name__)

@reviews_bp.route('/reviews', methods=['POST'])
@jwt_required()
def create_review():
    user_id = get_jwt_identity()
    if not is_customer(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    data = request.get_json()
    try:
        review = Review(
            customer_id=user_id,
            salon_id=data['salon_id'],
            barber_id=data['barber_id'],
            appointment_id=data['appointment_id'],
            rating=data['rating'],
            comment=data.get('comment')
        )
        db.session.add(review)
        db.session.commit()
        return jsonify({'message': 'Yorum eklendi'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@reviews_bp.route('/salons/<int:salon_id>/reviews', methods=['GET'])
def get_salon_reviews(salon_id):
    reviews = Review.query.filter_by(salon_id=salon_id).order_by(Review.created_at.desc()).all()

    result = [{
        'id': r.id,
        'rating': r.rating,
        'comment': r.comment,
        'created_at': r.created_at.isoformat(),
        'barber_name': r.barber.user.name if r.barber and r.barber.user else None,
        'customer_name': r.customer.name if r.customer else None
    } for r in reviews]

    return jsonify(result), 200
