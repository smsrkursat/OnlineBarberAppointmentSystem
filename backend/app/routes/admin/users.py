# routes/admin/users.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import User, UserRole, Salon, Appointment, Barber
from app.extensions import db
from app.routes.admin.utils import is_admin

users_bp = Blueprint('admin_users', __name__)

def has_role(user, role: UserRole):
    if user.role == role:
        return True
    return any(er.extra_role == role for er in user.extra_roles)

@users_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    users = User.query.all()
    result = [{
        'id': u.id,
        'name': u.name,
        'email': u.email,
        'role': u.role.value,
        'is_active': u.is_active,
        'extra_roles': [er.extra_role.value for er in u.extra_roles]
    } for u in users]

    return jsonify(result), 200

@users_bp.route('/admin/users/<int:user_id>/status', methods=['PATCH'])
@jwt_required()
def update_user_status(user_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Kullanıcı bulunamadı'}), 404

    data = request.get_json()
    is_active = data.get('is_active')
    if is_active is None:
        return jsonify({'error': 'is_active alanı gerekli'}), 400

    user.is_active = is_active
    db.session.commit()
    return jsonify({'message': 'Kullanıcı durumu güncellendi'}), 200

@users_bp.route('/admin/users/<int:user_id>', methods=['PATCH'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Kullanıcı bulunamadı'}), 404

    data = request.get_json()
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    user.is_active = data.get('is_active', user.is_active)

    new_role = data.get('role')
    if new_role:
        try:
            user.role = UserRole[new_role]
        except KeyError:
            return jsonify({'error': 'Geçersiz rol'}), 400

    db.session.commit()
    return jsonify({'message': 'Kullanıcı başarıyla güncellendi'}), 200

@users_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_detail(user_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Kullanıcı bulunamadı'}), 404

    user_data = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'role': user.role.value,
        'is_active': user.is_active,
        'is_verified': user.is_verified,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'extra_roles': [er.extra_role.value for er in user.extra_roles]
    }

    if has_role(user, UserRole.SALON_OWNER):
        owned_salons = Salon.query.filter_by(owner_id=user.id).all()
        user_data['owned_salons'] = [{
            'id': s.id,
            'name': s.name,
            'address': s.address,
            'phone': s.phone
        } for s in owned_salons]

    if has_role(user, UserRole.CUSTOMER):
        appointments = Appointment.query.filter_by(customer_id=user.id).all()
        user_data['appointment_count'] = len(appointments)
        user_data['appointments_summary'] = [{
            'id': a.id,
            'date': a.appointment_date.isoformat(),
            'status': a.status.value,
            'salon': a.salon.name if a.salon else None,
            'barber': a.barber.user.name if a.barber and a.barber.user else None,
            'service': a.service.name if a.service else None
        } for a in appointments]

    if has_role(user, UserRole.BARBER):
        barber = Barber.query.filter_by(user_id=user.id).first()
        if barber:
            user_data['barber_salon'] = {
                'id': barber.salon.id,
                'name': barber.salon.name
            } if barber.salon else None
            user_data['barber_appointments'] = [{
                'id': a.id,
                'customer_name': a.customer.name if a.customer else None,
                'date': a.appointment_date.isoformat(),
                'status': a.status.value
            } for a in barber.appointments]

    return jsonify(user_data), 200
