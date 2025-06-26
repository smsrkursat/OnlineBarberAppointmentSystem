from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import BarberInvitation, Barber
from app.extensions import db

invitations_bp = Blueprint('barber_invitations', __name__, url_prefix='/barber/invitations')

@invitations_bp.route('', methods=['GET'])
@jwt_required()
def get_invitations():
    user_id = get_jwt_identity()
    invitations = BarberInvitation.query.filter_by(user_id=user_id, status='pending').all()

    result = [{
        'id': i.id,
        'salon_id': i.salon_id,
        'salon_name': i.salon.name,
        'status': i.status,
        'created_at': i.created_at.isoformat()
    } for i in invitations]

    return jsonify(result), 200


@invitations_bp.route('/<int:invitation_id>/accept', methods=['POST'])
@jwt_required()
def accept_invitation(invitation_id):
    user_id = get_jwt_identity()
    invitation = BarberInvitation.query.filter_by(id=invitation_id, user_id=user_id).first()

    if not invitation or invitation.status != 'pending':
        return jsonify({'error': 'Geçerli davet bulunamadı'}), 404

    new_barber = Barber(user_id=user_id, salon_id=invitation.salon_id)
    db.session.add(new_barber)

    invitation.status = 'accepted'
    db.session.commit()

    return jsonify({'message': 'Davet kabul edildi ve salon ile eşleştirildiniz'}), 200


@invitations_bp.route('/<int:invitation_id>/reject', methods=['POST'])
@jwt_required()
def reject_invitation(invitation_id):
    user_id = get_jwt_identity()
    invitation = BarberInvitation.query.filter_by(id=invitation_id, user_id=user_id).first()

    if not invitation or invitation.status != 'pending':
        return jsonify({'error': 'Geçerli davet bulunamadı'}), 404

    invitation.status = 'rejected'
    db.session.commit()

    return jsonify({'message': 'Davet reddedildi'}), 200
