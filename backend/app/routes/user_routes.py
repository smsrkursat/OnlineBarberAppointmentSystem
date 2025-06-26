from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import User, UserRole, Barber
from app.extensions import db
from werkzeug.security import generate_password_hash

user_bp = Blueprint('users', __name__)

# 🟢 Mevcut: uygun berberleri getir
@user_bp.route('/users/available-barbers', methods=['GET'])
def get_available_barbers():
    assigned_user_ids = [b.user_id for b in Barber.query.all()]
    users = User.query.filter(
        User.is_active == True,
        User.is_verified == True,
        ~User.id.in_(assigned_user_ids)
    ).all()

    available_users = []
    for u in users:
        if u.role == UserRole.BARBER or any(er.extra_role == UserRole.BARBER for er in u.extra_roles):
            available_users.append(u)

    result = [ {'id': u.id, 'name': u.name, 'email': u.email} for u in available_users ]
    return jsonify(result), 200

# ✅ Yeni: kendi profilini getir
@user_bp.route('/users/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Kullanıcı bulunamadı'}), 404

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'role': user.role.value,
        'extra_roles': [er.extra_role.value for er in user.extra_roles],
        'is_active': user.is_active,
        'is_verified': user.is_verified
    }), 200


@user_bp.route('/users/me', methods=['PATCH'])
@jwt_required()
def update_my_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Kullanıcı bulunamadı'}), 404

    data = request.get_json()
    user.name = data.get('name', user.name)
    user.phone = data.get('phone', user.phone)

    if data.get('password'):
        user.password_hash = generate_password_hash(data['password'])

    db.session.commit()
    return jsonify({'message': 'Profil güncellendi'}), 200

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_public(user_id):
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({'error': 'Kullanıcı bulunamadı'}), 404

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    }), 200
