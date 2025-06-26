from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import User, UserRole, Salon, Appointment
from .utils import is_owner
from datetime import date
from sqlalchemy import and_

appointments_bp = Blueprint('salon_owner_appointments', __name__)

@appointments_bp.route('/owner/appointments/today', methods=['GET'])
@jwt_required()
def get_today_appointments():
    user_id = get_jwt_identity()
    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    today = date.today()

    # Owner’a ait salonları al
    salons = Salon.query.filter_by(owner_id=user_id).all()
    salon_ids = [s.id for s in salons]

    appointments = Appointment.query.filter(
        and_(
            Appointment.salon_id.in_(salon_ids),
            Appointment.appointment_date == today
        )
    ).all()

    results = [format_appointment(a) for a in appointments]

    return jsonify(results), 200

@appointments_bp.route('/owner/appointments/history', methods=['GET'])
@jwt_required()
def get_past_appointments():
    user_id = get_jwt_identity()
    if not is_owner(user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    today = date.today()

    salons = Salon.query.filter_by(owner_id=user_id).all()
    salon_ids = [s.id for s in salons]

    appointments = Appointment.query.filter(
        and_(
            Appointment.salon_id.in_(salon_ids),
            Appointment.appointment_date < today
        )
    ).order_by(Appointment.appointment_date.desc()).all()

    results = [format_appointment(a) for a in appointments]

    return jsonify(results), 200

def format_appointment(a):
    return {
        'id': a.id,
        'date': a.appointment_date.isoformat(),
        'start_time': a.start_time.strftime('%H:%M'),
        'end_time': a.end_time.strftime('%H:%M'),
        'status': a.status.value,
        'service': a.service.name if a.service else None,
        'barber': a.barber.user.name if a.barber and a.barber.user else None,
        'salon': a.salon.name if a.salon else None,
        'customer': a.customer.name if a.customer else None
    }
