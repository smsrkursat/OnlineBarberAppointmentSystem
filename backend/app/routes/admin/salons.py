from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Salon
from app.extensions import db
from app.routes.admin.utils import is_admin

salons_bp = Blueprint('admin_salons', __name__)

@salons_bp.route('/admin/salons', methods=['GET'])
@jwt_required()
def get_all_salons():
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salons = Salon.query.all()
    result = [{
        'id': s.id,
        'name': s.name,
        'address': s.address,
        'phone': s.phone,
        'owner_id': s.owner_id,
        'owner_name': s.owner.name if s.owner else 'Bilinmiyor',
        'rating': s.rating,
        'is_active': s.is_active
    } for s in salons]

    return jsonify(result), 200

@salons_bp.route('/admin/salons/<int:salon_id>', methods=['GET'])
@jwt_required()
def get_salon_detail(salon_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.get_or_404(salon_id)

    salon_data = {
        'id': salon.id,
        'name': salon.name,
        'address': salon.address,
        'phone': salon.phone,
        'description': salon.description,
        'owner_id': salon.owner_id,
        'owner_name': salon.owner.name if salon.owner else 'Bilinmiyor',
        'rating': salon.rating,
        'is_active': salon.is_active,
        'services': [{
            'id': service.id,
            'name': service.name,
            'price': service.price,
            'duration': service.duration,
            'description': service.description
        } for service in salon.services],
        'barbers': [{
            'id': barber.id,
            'name': barber.user.name if barber.user else 'Bilinmiyor'
        } for barber in salon.barbers],
        'reviews': [{
            'id': review.id,
            'comment': review.comment,
            'rating': review.rating
        } for review in salon.reviews]
    }
    return jsonify(salon_data), 200

@salons_bp.route('/admin/salons/<int:salon_id>', methods=['DELETE'])
@jwt_required()
def delete_salon(salon_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.get(salon_id)
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    db.session.delete(salon)
    db.session.commit()
    return jsonify({'message': 'Salon başarıyla silindi'}), 200
