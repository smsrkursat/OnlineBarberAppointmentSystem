from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import User, UserRole, Salon, Appointment, Review
from app.routes.admin.utils import is_admin

dashboard_bp = Blueprint('admin_dashboard', __name__)

@dashboard_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({'error': 'Erişim reddedildi'}), 403

    total_users = User.query.count()
    role_counts = {
        'CUSTOMER': User.query.filter_by(role=UserRole.CUSTOMER).count(),
        'BARBER': User.query.filter_by(role=UserRole.BARBER).count(),
        'SALON_OWNER': User.query.filter_by(role=UserRole.SALON_OWNER).count(),
        'ADMIN': User.query.filter_by(role=UserRole.ADMIN).count()
    }
    total_salons = Salon.query.count()
    total_appointments = Appointment.query.count()
    status_counts = {
        'PENDING': Appointment.query.filter_by(status='PENDING').count(),
        'CONFIRMED': Appointment.query.filter_by(status='CONFIRMED').count(),
        'CANCELLED': Appointment.query.filter_by(status='CANCELLED').count(),
        'COMPLETED': Appointment.query.filter_by(status='COMPLETED').count()
    }
    total_reviews = Review.query.count()

    return jsonify({
        'total_users': total_users,
        'role_counts': role_counts,
        'total_salons': total_salons,
        'total_appointments': total_appointments,
        'appointment_status_counts': status_counts,
        'total_reviews': total_reviews
    }), 200
