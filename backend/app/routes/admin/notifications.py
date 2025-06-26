from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Notification, User
from app.extensions import db
from app.routes.admin.utils import is_admin

notifications_bp = Blueprint('admin_notifications', __name__)

@notifications_bp.route('/admin/notifications', methods=['POST'])
@jwt_required()
def send_notification():
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    data = request.get_json()
    user_id = data.get('user_id')
    message = data.get('message')

    if not user_id or not message:
        return jsonify({'error': 'user_id ve message zorunludur'}), 400

    recipient = User.query.get(user_id)
    if not recipient:
        return jsonify({'error': 'Hedef kullanıcı bulunamadı'}), 404

    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()

    return jsonify({'message': 'Bildirim başarıyla gönderildi'}), 201

@notifications_bp.route('/admin/notifications', methods=['GET'])
@jwt_required()
def get_all_notifications():
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    result = []
    for n in notifications:
        result.append({
            'id': n.id,
            'message': n.message,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
            'user_id': n.user_id,
            'user_name': n.user.name if n.user else None
        })
    return jsonify(result), 200
