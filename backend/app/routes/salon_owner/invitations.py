from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Salon, BarberInvitation
from app.extensions import db
from .utils import is_owner

invitations_bp = Blueprint('salon_owner_invitations', __name__)

@invitations_bp.route('/owner/invite-barber', methods=['POST'])
@jwt_required()
def invite_barber():
    current_user_id = get_jwt_identity()

    if not is_owner(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id gerekli'}), 400

    salon = Salon.query.filter_by(owner_id=current_user_id).first()
    if not salon:
        return jsonify({'error': 'Salon bulunamadı'}), 404

    # Zaten davet gönderilmiş mi kontrolü
    existing = BarberInvitation.query.filter_by(
        user_id=user_id,
        salon_id=salon.id,
        status='pending'
    ).first()

    if existing:
        return jsonify({'error': 'Zaten bekleyen bir davet var'}), 400

    invitation = BarberInvitation(user_id=user_id, salon_id=salon.id)
    db.session.add(invitation)
    db.session.commit()

    return jsonify({'message': 'Berber daveti gönderildi'}), 201
