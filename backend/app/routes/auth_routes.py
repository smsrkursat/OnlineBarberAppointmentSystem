from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.models import User
from app.utils.auth import generate_access_token
from app.utils.mail import send_verification_email
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email zaten kayıtlı'}), 400

    user = User(
        email=email,
        name=name,
        password_hash=generate_password_hash(password),
        is_verified=False
    )

    # Token oluştur
    token = str(uuid.uuid4())
    user.verification_token = token
    db.session.add(user)
    db.session.commit()

    # Doğrulama maili gönder
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:4200')
    verify_url = f"{frontend_url}/verify-email/{token}"
    send_verification_email(user.email, verify_url)

    return jsonify({'message': 'Kayıt başarılı. Lütfen e-postanızı doğrulayın.'}), 201

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        return jsonify({'error': 'Geçersiz token'}), 400

    user.is_verified = True
    user.verification_token = None
    db.session.commit()

    return jsonify({'message': 'Email başarıyla doğrulandı.'})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Geçersiz email veya şifre'}), 401

    if not user.is_verified:
        return jsonify({'error': 'Email adresi doğrulanmamış'}), 403

    token = generate_access_token(identity=user.id)

    return jsonify({
        'access_token': token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role.value.lower(),  
            'extra_roles': [r.extra_role.value.lower() for r in user.extra_roles]  
        }
    })


