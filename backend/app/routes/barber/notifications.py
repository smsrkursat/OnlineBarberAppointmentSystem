from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Notification
from app.extensions import db
from .utils import is_barber

notifications_bp = Blueprint('barber_notifications', __name__, url_prefix='/barber/notifications')

@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_my_notifications():
    user_id = get_jwt_identity()
    if not is_barber(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

    result = [{
        'id': n.id,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat()
    } for n in notifications]

    return jsonify(result), 200


@notifications_bp.route('/<int:notification_id>/mark-read', methods=['PATCH'])
@jwt_required()
def mark_as_read(notification_id):
    user_id = get_jwt_identity()
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()

    if not notification:
        return jsonify({'error': 'Bildirim bulunamadı'}), 404

    notification.is_read = True
    db.session.commit()
    return jsonify({'message': 'Bildirim okundu olarak işaretlendi'}), 200
