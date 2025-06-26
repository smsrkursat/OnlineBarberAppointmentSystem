from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Notification
from .utils import is_owner
from app.extensions import db

notifications_bp = Blueprint('salon_owner_notifications', __name__)

@notifications_bp.route('/owner/notifications', methods=['GET'])
@jwt_required()
def get_owner_notifications():
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

    result = [ {
        'id': n.id,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat()
    } for n in notifications ]

    return jsonify(result), 200

@notifications_bp.route('/owner/notifications/<int:notif_id>/read', methods=['PATCH'])
@jwt_required()
def mark_notification_read(notif_id):
    user_id = get_jwt_identity()

    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
    if not notif:
        return jsonify({'error': 'Bildirim bulunamadı'}), 404

    notif.is_read = True
    db.session.commit()

    return jsonify({'message': 'Bildirim okundu olarak işaretlendi'}), 200
