from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Salon, Service
from app.extensions import db
from .utils import is_owner

services_bp = Blueprint('salon_owner_services', __name__)

@services_bp.route('/owner/salon/services', methods=['GET'])
@jwt_required()
def get_salon_services():
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.filter_by(owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    services = [ {
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'price': s.price,
        'duration': s.duration
    } for s in salon.services ]

    return jsonify(services), 200

@services_bp.route('/owner/salon/services', methods=['POST'])
@jwt_required()
def add_service():
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.filter_by(owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    data = request.get_json()

    new_service = Service(
        salon_id=salon.id,
        name=data.get('name'),
        description=data.get('description'),
        price=data.get('price'),
        duration=data.get('duration')
    )
    db.session.add(new_service)
    db.session.commit()

    return jsonify({'message': 'Hizmet eklendi'}), 201

@services_bp.route('/owner/salon/services/<int:service_id>', methods=['PATCH'])
@jwt_required()
def update_service(service_id):
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.filter_by(owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    service = Service.query.filter_by(id=service_id, salon_id=salon.id).first()
    if not service:
        return jsonify({'error': 'Hizmet bulunamadı'}), 404

    data = request.get_json()
    service.name = data.get('name', service.name)
    service.description = data.get('description', service.description)
    service.price = data.get('price', service.price)
    service.duration = data.get('duration', service.duration)

    db.session.commit()
    return jsonify({'message': 'Hizmet güncellendi'}), 200

@services_bp.route('/owner/salon/services/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_service(service_id):
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    salon = Salon.query.filter_by(owner_id=user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    service = Service.query.filter_by(id=service_id, salon_id=salon.id).first()
    if not service:
        return jsonify({'error': 'Hizmet bulunamadı'}), 404

    db.session.delete(service)
    db.session.commit()

    return jsonify({'message': 'Hizmet silindi'}), 200
