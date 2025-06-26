from flask import Blueprint, jsonify
from app.models.models import Salon, Barber, Service

salons_bp = Blueprint('customer_salons', __name__)

@salons_bp.route('/salons', methods=['GET'])
def get_all_salons():
    salons = Salon.query.filter_by(is_active=True).all()

    result = [{
        'id': s.id,
        'name': s.name,
        'address': s.address,
        'phone': s.phone,
        'rating': s.rating,
        'description': s.description,
        'image': s.salon_image
    } for s in salons]

    return jsonify(result), 200

@salons_bp.route('/salons/<int:salon_id>/barbers', methods=['GET'])
def get_salon_barbers(salon_id):
    barbers = Barber.query.filter_by(salon_id=salon_id).all()
    result = [{
        'id': b.id,
        'user_id': b.user_id,
        'experience_years': b.experience_years,
        'rating': b.rating,
        'bio': b.bio
    } for b in barbers]
    return jsonify(result), 200

@salons_bp.route('/salons/<int:salon_id>/services', methods=['GET'])
def get_salon_services(salon_id):
    services = Service.query.filter_by(salon_id=salon_id).all()
    result = [{
        'id': s.id,
        'name': s.name,
        'price': s.price,
        'duration': s.duration,
        'description': s.description
    } for s in services]
    return jsonify(result), 200
