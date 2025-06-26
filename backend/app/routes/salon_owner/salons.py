from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import User, UserRole, Salon, Barber
from app.extensions import db
from .utils import is_owner

salons_bp = Blueprint('salon_owner_salons', __name__)

@salons_bp.route('/owner/salon', methods=['GET'])
@jwt_required()
def get_owner_salon():
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.filter_by(owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    return jsonify({
        'id': salon.id,
        'name': salon.name,
        'address': salon.address,
        'phone': salon.phone,
        'rating': salon.rating,
        'description': salon.description,
        'image': salon.salon_image
    }), 200

@salons_bp.route('/owner/salon', methods=['PATCH'])
@jwt_required()
def update_salon():
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.filter_by(owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    data = request.get_json()

    salon.name = data.get('name', salon.name)
    salon.address = data.get('address', salon.address)
    salon.phone = data.get('phone', salon.phone)
    salon.description = data.get('description', salon.description)

    db.session.commit()

    return jsonify({'message': 'Salon bilgileri güncellendi'}), 200

@salons_bp.route('/owner/salons', methods=['GET'])
@jwt_required()
def get_owner_salons():
    user_id = get_jwt_identity()
    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403
    salons = Salon.query.filter_by(owner_id=user_id).all()
    result = []
    for salon in salons:
        barber_count = Barber.query.filter_by(salon_id=salon.id).count()
        result.append({
            'id': salon.id,
            'name': salon.name,
            'address': salon.address,
            'phone': salon.phone,
            'rating': salon.rating,
            'description': salon.description,
            'image': salon.salon_image,
            'is_active': salon.is_active,
            'barber_count': barber_count
        })
    return jsonify(result), 200

@salons_bp.route('/owner/salons/<int:salon_id>', methods=['GET'])
@jwt_required()
def get_owner_salon_detail(salon_id):
    user_id = get_jwt_identity()
    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403
    salon = Salon.query.filter_by(id=salon_id, owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404
    barbers = Barber.query.filter_by(salon_id=salon.id).all()
    barber_list = [{
        'id': b.id,
        'user_id': b.user_id,
        'name': b.user.name if b.user else '',
        'rating': b.rating,
        'experience_years': b.experience_years,
        'bio': b.bio
    } for b in barbers]
    return jsonify({
        'id': salon.id,
        'name': salon.name,
        'address': salon.address,
        'phone': salon.phone,
        'rating': salon.rating,
        'description': salon.description,
        'image': salon.salon_image,
        'is_active': salon.is_active,
        'barbers': barber_list
    }), 200

@salons_bp.route('/owner/salons/<int:salon_id>', methods=['DELETE'])
@jwt_required()
def delete_owner_salon(salon_id):
    user_id = get_jwt_identity()
    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403
    salon = Salon.query.filter_by(id=salon_id, owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404
    db.session.delete(salon)
    db.session.commit()
    return jsonify({'message': 'Salon silindi'}), 200

@salons_bp.route('/owner/salons/<int:salon_id>', methods=['PATCH'])
@jwt_required()
def update_owner_salon(salon_id):
    user_id = get_jwt_identity()
    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403
    salon = Salon.query.filter_by(id=salon_id, owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404
    data = request.get_json()
    salon.name = data.get('name', salon.name)
    salon.address = data.get('address', salon.address)
    salon.phone = data.get('phone', salon.phone)
    salon.description = data.get('description', salon.description)
    db.session.commit()
    return jsonify({'message': 'Salon güncellendi'}), 200

@salons_bp.route('/owner/salon/barbers/<int:barber_id>', methods=['DELETE'])
@jwt_required()
def remove_barber_from_salon(barber_id):
    user_id = get_jwt_identity()
    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403
    salon = Salon.query.filter_by(owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404
    barber = Barber.query.filter_by(id=barber_id, salon_id=salon.id).first()
    if not barber:
        return jsonify({'error': 'Berber bulunamadı'}), 404
    db.session.delete(barber)
    db.session.commit()
    return jsonify({'message': 'Berber salondan çıkarıldı'}), 200
