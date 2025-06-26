from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import foreign
from sqlalchemy import and_
from app.extensions import db

# Kullanıcı Rolleri için Enum
class UserRole(Enum):
    CUSTOMER = 'CUSTOMER'
    BARBER = 'BARBER'
    ADMIN = 'ADMIN'
    SALON_OWNER = 'SALON_OWNER'

# Randevu Durumu için Enum
class AppointmentStatus(Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'

# Promosyon Türü için Enum (Basitleştirilmiş)
class PromotionType(Enum):
    PERCENTAGE = 'percentage'  # Yüzde indirim

# Berber-Saç Stili İlişki Tablosu (Uzmanlıklar için)
barber_specialties = db.Table('barber_specialties',
    db.Column('barber_id', db.Integer, db.ForeignKey('barbers.id'), primary_key=True),
    db.Column('haircut_style_id', db.Integer, db.ForeignKey('haircut_styles.id'), primary_key=True)
)

class WorkingHours(db.Model):
    __tablename__ = 'working_hours'

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(10), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_day_off = db.Column(db.Boolean, default=False)

    def __repr__(self):
        if self.is_day_off:
            return f'<WorkingHours {self.entity_type} {self.entity_id} - Day {self.day_of_week}: OFF>'
        return f'<WorkingHours {self.entity_type} {self.entity_id} - Day {self.day_of_week}: {self.start_time}-{self.end_time}>'


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.CUSTOMER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)

    appointments = db.relationship('Appointment', backref='customer', lazy=True, foreign_keys='Appointment.customer_id')
    reviews = db.relationship('Review', backref='customer', lazy=True)
    notifications = db.relationship('Notification', backref='recipient', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_verification_token(self):
        import uuid
        self.verification_token = str(uuid.uuid4())
        return self.verification_token

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<User {self.name}>'

class Salon(db.Model):
    __tablename__ = 'salons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Float, default=0.0)
    salon_image = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    barbers = db.relationship('Barber', backref='salon', lazy=True)
    services = db.relationship('Service', backref='salon', lazy=True)
    reviews = db.relationship('Review', backref='salon', lazy=True)
    appointments = db.relationship('Appointment', backref='salon', lazy=True)
    owner = db.relationship('User')
    promotions = db.relationship('Promotion', backref='salon', lazy=True)

    working_hours = db.relationship('WorkingHours', lazy=True,
        primaryjoin=and_(
            id == foreign(db.remote(WorkingHours.entity_id)),
            WorkingHours.entity_type == 'salon'
        ),
        backref='salon'
    )

    def __repr__(self):
        return f'<Salon {self.name}>'

class Barber(db.Model):
    __tablename__ = 'barbers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    salon_id = db.Column(db.Integer, db.ForeignKey('salons.id'), nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, default=0.0)

    appointments = db.relationship('Appointment', backref='barber', lazy=True)
    reviews = db.relationship('Review', backref='barber', lazy=True)
    specialties = db.relationship('HaircutStyle', secondary=barber_specialties, backref=db.backref('barbers', lazy='dynamic'))
    user = db.relationship('User')

    working_hours = db.relationship('WorkingHours', lazy=True,
        primaryjoin=and_(
            id == foreign(db.remote(WorkingHours.entity_id)),
            WorkingHours.entity_type == 'barber'
        ),
        backref='barber'
    )

    def __repr__(self):
        return f'<Barber {self.user.name}>'

class HaircutStyle(db.Model):
    __tablename__ = 'haircut_styles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    avg_duration = db.Column(db.Integer, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<HaircutStyle {self.name}>'

class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    salon_id = db.Column(db.Integer, db.ForeignKey('salons.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    haircut_style_id = db.Column(db.Integer, db.ForeignKey('haircut_styles.id'), nullable=True)

    appointments = db.relationship('Appointment', backref='service', lazy=True)
    haircut_style = db.relationship('HaircutStyle')

    def __repr__(self):
        return f'<Service {self.name}>'

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    salon_id = db.Column(db.Integer, db.ForeignKey('salons.id'), nullable=False)
    barber_id = db.Column(db.Integer, db.ForeignKey('barbers.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=True)
    discounted_price = db.Column(db.Float, nullable=True)
    promotion_code = db.Column(db.String(20), nullable=True)

    review = db.relationship('Review', backref='appointment', lazy=True, uselist=False)

    def can_cancel(self):
        now = datetime.utcnow()
        appointment_datetime = datetime.combine(self.appointment_date, self.start_time)
        cancel_limit = appointment_datetime - timedelta(hours=24)
        return now <= cancel_limit

    def __repr__(self):
        return f'<Appointment {self.id} - {self.appointment_date}>'

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    salon_id = db.Column(db.Integer, db.ForeignKey('salons.id'), nullable=False)
    barber_id = db.Column(db.Integer, db.ForeignKey('barbers.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False, unique=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id} - Rating: {self.rating}>'

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'
    
class UserExtraRole(db.Model):
    __tablename__ = 'user_extra_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    extra_role = db.Column(db.Enum(UserRole), nullable=False)

    user = db.relationship('User', backref='extra_roles')

    def __repr__(self):
        return f'<UserExtraRole user={self.user_id} role={self.extra_role}>'
    

class BarberInvitation(db.Model):
    __tablename__ = 'barber_invitations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    salon_id = db.Column(db.Integer, db.ForeignKey('salons.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending / accepted / rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='barber_invitations', lazy=True)
    salon = db.relationship('Salon', backref='barber_invitations', lazy=True)

    def __repr__(self):
        return f'<BarberInvitation user={self.user_id} salon={self.salon_id} status={self.status}>'


class Promotion(db.Model):
    __tablename__ = 'promotions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    discount_percentage = db.Column(db.Float, nullable=False)
    min_purchase_amount = db.Column(db.Float, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    max_usage = db.Column(db.Integer, nullable=True)
    current_usage = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    salon_id = db.Column(db.Integer, db.ForeignKey('salons.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid(self):
        now = datetime.utcnow()
        return (
            self.is_active and 
            self.start_date <= now <= self.end_date and 
            (self.max_usage is None or self.current_usage < self.max_usage)
        )

    def calculate_discount(self, amount):
        if not self.is_valid():
            return 0
        if self.min_purchase_amount and amount < self.min_purchase_amount:
            return 0
        discount = amount * (self.discount_percentage / 100)
        return round(discount, 2)

    def __repr__(self):
        return f'<Promotion {self.code}: {self.title}>'
