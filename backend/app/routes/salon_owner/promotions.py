from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Salon, Promotion
from app.extensions import db
from .utils import is_owner
from datetime import datetime

promotions_bp = Blueprint('salon_owner_promotions', __name__)

@promotions_bp.route('/owner/promotions', methods=['GET'])
@jwt_required()
def get_owner_promotions():
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.filter_by(owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    promotions = Promotion.query.filter_by(salon_id=salon.id).order_by(Promotion.start_date.desc()).all()

    result = [ {
        'id': p.id,
        'title': p.title,
        'code': p.code,
        'discount_percentage': p.discount_percentage,
        'start_date': p.start_date.isoformat(),
        'end_date': p.end_date.isoformat(),
        'is_active': p.is_active
    } for p in promotions ]

    return jsonify(result), 200

@promotions_bp.route('/owner/promotions', methods=['POST'])
@jwt_required()
def create_promotion():
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.filter_by(owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    data = request.get_json()
    try:
        new_promo = Promotion(
            title=data.get('title'),
            description=data.get('description'),
            code=data.get('code'),
            discount_percentage=data.get('discount_percentage'),
            min_purchase_amount=data.get('min_purchase_amount'),
            start_date=datetime.fromisoformat(data.get('start_date')),
            end_date=datetime.fromisoformat(data.get('end_date')),
            max_usage=data.get('max_usage'),
            is_active=True,
            salon_id=salon.id
        )
        db.session.add(new_promo)
        db.session.commit()
        return jsonify({'message': 'Promosyon oluşturuldu'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@promotions_bp.route('/owner/promotions/<int:promo_id>', methods=['PATCH'])
@jwt_required()
def update_promotion(promo_id):
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.filter_by(owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    promo = Promotion.query.filter_by(id=promo_id, salon_id=salon.id).first()
    if not promo:
        return jsonify({'error': 'Promosyon bulunamadı'}), 404

    data = request.get_json()
    promo.title = data.get('title', promo.title)
    promo.description = data.get('description', promo.description)
    promo.discount_percentage = data.get('discount_percentage', promo.discount_percentage)
    promo.min_purchase_amount = data.get('min_purchase_amount', promo.min_purchase_amount)
    promo.start_date = datetime.fromisoformat(data.get('start_date')) if data.get('start_date') else promo.start_date
    promo.end_date = datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else promo.end_date
    promo.max_usage = data.get('max_usage', promo.max_usage)
    promo.is_active = data.get('is_active', promo.is_active)

    db.session.commit()
    return jsonify({'message': 'Promosyon güncellendi'}), 200

@promotions_bp.route('/owner/promotions/<int:promo_id>', methods=['DELETE'])
@jwt_required()
def delete_promotion(promo_id):
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.filter_by(owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    promo = Promotion.query.filter_by(id=promo_id, salon_id=salon.id).first()
    if not promo:
        return jsonify({'error': 'Promosyon bulunamadı'}), 404

    db.session.delete(promo)
    db.session.commit()

    return jsonify({'message': 'Promosyon silindi'}), 200
