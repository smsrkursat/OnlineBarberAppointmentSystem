from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Service
from app.routes.admin.utils import is_admin

services_bp = Blueprint('admin_services', __name__)

@services_bp.route('/admin/services', methods=['GET'])
@jwt_required()
def get_all_services():
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    services = Service.query.all()
    result = []
    for s in services:
        result.append({
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'price': s.price,
            'duration': s.duration,
            'salon_id': s.salon_id,
            'salon_name': s.salon.name if s.salon else None,
            'haircut_style': s.haircut_style.name if s.haircut_style else None
        })

    return jsonify(result), 200

@services_bp.route('/admin/services/<int:service_id>', methods=['GET'])
@jwt_required()
def get_service_detail(service_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    service = Service.query.get_or_404(service_id)
    result = {
        'id': service.id,
        'name': service.name,
        'description': service.description,
        'price': service.price,
        'duration': service.duration,
        'salon_id': service.salon_id,
        'salon_name': service.salon.name if service.salon else None,
        'haircut_style': service.haircut_style.name if service.haircut_style else None
    }
    return jsonify(result), 200

@services_bp.route('/admin/services/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_service(service_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    service = Service.query.get_or_404(service_id)
    from app.extensions import db
    db.session.delete(service)
    db.session.commit()
    return jsonify({'message': 'Hizmet başarıyla silindi.'}), 200
