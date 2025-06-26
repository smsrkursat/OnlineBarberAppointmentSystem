from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.models import Appointment, AppointmentStatus
from datetime import datetime
from .utils import is_customer

appointments_bp = Blueprint('customer_appointments', __name__)

@appointments_bp.route('/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    user_id = get_jwt_identity()
    if not is_customer(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    data = request.get_json()
    try:
        appointment = Appointment(
            customer_id=user_id,
            salon_id=data['salon_id'],
            barber_id=data['barber_id'],
            service_id=data['service_id'],
            appointment_date=datetime.strptime(data['appointment_date'], "%Y-%m-%d").date(),
            start_time=datetime.strptime(data['start_time'], "%H:%M").time(),
            end_time=datetime.strptime(data['end_time'], "%H:%M").time(),
            status=AppointmentStatus.PENDING,
            notes=data.get('notes'),
            total_price=data.get('total_price')
        )
        db.session.add(appointment)
        db.session.commit()
        return jsonify({'message': 'Randevu başarıyla oluşturuldu.'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@appointments_bp.route('/appointments/mine', methods=['GET'])
@jwt_required()
def get_my_appointments():
    user_id = get_jwt_identity()
    if not is_customer(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    appointments = Appointment.query.filter_by(customer_id=user_id).order_by(Appointment.appointment_date.desc()).all()

    results = [{
        'id': a.id,
        'date': a.appointment_date.strftime("%Y-%m-%d"),
        'start_time': a.start_time.strftime("%H:%M"),
        'end_time': a.end_time.strftime("%H:%M"),
        'status': a.status.value,
        'salon_id': a.salon_id,
        'salon_name': a.salon.name if a.salon else None,
        'barber_id': a.barber_id,
        'barber_name': a.barber.user.name if a.barber and a.barber.user else None,
        'service_id': a.service_id,
        'service_name': a.service.name if a.service else None,
        'notes': a.notes
    } for a in appointments]

    return jsonify(results), 200

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
def cancel_appointment(appointment_id):
    user_id = get_jwt_identity()
    if not is_customer(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    appointment = Appointment.query.filter_by(id=appointment_id, customer_id=user_id).first()
    if not appointment:
        return jsonify({'error': 'Randevu bulunamadı'}), 404

    if not appointment.can_cancel():
        return jsonify({'error': 'Bu randevu artık iptal edilemez (24 saat kuralı)'}), 400

    appointment.status = AppointmentStatus.CANCELLED
    db.session.commit()
    return jsonify({'message': 'Randevu iptal edildi'}), 200
