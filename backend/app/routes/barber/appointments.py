from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Appointment, AppointmentStatus, Barber
from app.extensions import db
from .utils import is_barber

appointments_bp = Blueprint('barber_appointments', __name__, url_prefix='/barber')

@appointments_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_barber_appointments():
    user_id = get_jwt_identity()
    if not is_barber(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    barber = Barber.query.filter_by(user_id=user_id).first()
    if not barber:
        return jsonify({'error': 'Berber profili bulunamadı'}), 404

    appointments = Appointment.query.filter_by(barber_id=barber.id).order_by(Appointment.appointment_date.desc()).all()

    result = [{
        'id': a.id,
        'customer_id': a.customer_id,
        'customer_name': a.customer.name if a.customer else None,
        'customer_phone': a.customer.phone if a.customer else None,
        'service_name': a.service.name if a.service else None,
        'salon_name': a.salon.name if a.salon else None,
        'date': a.appointment_date.strftime('%Y-%m-%d'),
        'start_time': a.start_time.strftime('%H:%M'),
        'end_time': a.end_time.strftime('%H:%M'),
        'status': a.status.value,
        'notes': a.notes,
        'total_price': a.total_price,
        'discounted_price': a.discounted_price
    } for a in appointments]

    return jsonify(result), 200


@appointments_bp.route('/appointments/<int:appointment_id>/status', methods=['PUT'])
@jwt_required()
def update_appointment_status(appointment_id):
    user_id = get_jwt_identity()
    if not is_barber(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    barber = Barber.query.filter_by(user_id=user_id).first()
    if not barber:
        return jsonify({'error': 'Berber profili bulunamadı'}), 404

    appointment = Appointment.query.filter_by(id=appointment_id, barber_id=barber.id).first()
    if not appointment:
        return jsonify({'error': 'Randevu bulunamadı'}), 404

    data = request.get_json()
    new_status = data.get("status", "").upper()

    try:
        appointment.status = AppointmentStatus[new_status]
    except KeyError:
        return jsonify({'error': 'Geçersiz randevu durumu'}), 400

    db.session.commit()
    return jsonify({'message': 'Durum güncellendi'}), 200
