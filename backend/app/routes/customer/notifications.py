from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Notification
from .utils import is_customer

notifications_bp = Blueprint('customer_notifications', __name__)

@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_my_notifications():
    user_id = get_jwt_identity()
    if not is_customer(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

    result = [{
        'id': n.id,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat()
    } for n in notifications]

    return jsonify(result), 200
