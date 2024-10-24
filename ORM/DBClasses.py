
from __init__ import db


class Role(db.Model):
    __tablename__ = 'role'

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False)

    users = db.relationship('User', backref='role', lazy=True)


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    secondname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    bookings = db.relationship('Booking', backref='user', lazy=True)
    payment_details = db.relationship('PaymentDetail', backref='user', lazy=True)


class Event(db.Model):
    __tablename__ = 'event'

    event_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    venue = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_tickets = db.Column(db.Integer, nullable=False)
    available_tickets = db.Column(db.Integer, nullable=False)

    bookings = db.relationship('Booking', backref='event', lazy=True)
    seats = db.relationship('Seat', backref='event', lazy=True)
    ticket_tiers = db.relationship('EventTicketTier', backref='event', lazy=True)


class Booking(db.Model):
    __tablename__ = 'booking'

    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    booking_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    booking_status = db.Column(db.Enum('confirmed', 'cancelled'), default='confirmed')

    seats = db.relationship('BookingSeat', backref='booking', lazy=True)
    tickets = db.relationship('Ticket', backref='booking', lazy=True)


class Seat(db.Model):
    __tablename__ = 'seat'

    seat_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    booking_seats = db.relationship('BookingSeat', backref='seat', lazy=True)


class BookingSeat(db.Model):
    __tablename__ = 'booking_seat'

    seat_id = db.Column(db.Integer, db.ForeignKey('seat.seat_id'), primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id'), primary_key=True)


class TicketTier(db.Model):
    __tablename__ = 'ticket_tier'

    tier_id = db.Column(db.Integer, primary_key=True)
    tier_name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    event_ticket_tiers = db.relationship('EventTicketTier', backref='ticket_tier', lazy=True)


class EventTicketTier(db.Model):
    __tablename__ = 'event_ticket_tier'

    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'), primary_key=True)
    tier_id = db.Column(db.Integer, db.ForeignKey('ticket_tier.tier_id'), primary_key=True)
    total_tickets = db.Column(db.Integer, nullable=False)


class Ticket(db.Model):
    __tablename__ = 'ticket'

    ticket_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.seat_id'), nullable=False)
    tier_id = db.Column(db.Integer, db.ForeignKey('ticket_tier.tier_id'), nullable=False)


class Notification(db.Model):
    __tablename__ = 'notification'

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'), nullable=False)
    message = db.Column(db.Text)
    notification_type = db.Column(db.Text)
    notification_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.Enum('sent', 'pending'), default='pending')


class PaymentDetail(db.Model):
    __tablename__ = 'payment_detail'

    payment_detail_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    card_type = db.Column(db.Enum('Visa', 'MasterCard', 'AmEx', 'Discover'), nullable=False)
    card_number = db.Column(db.String(20), nullable=False)
    cardholder_name = db.Column(db.String(100), nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)
    billing_address = db.Column(db.Text, nullable=False)


class Payment(db.Model):
    __tablename__ = 'payment'

    payment_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id'), nullable=False)
    payment_detail_id = db.Column(db.Integer, db.ForeignKey('payment_detail.payment_detail_id'))
    payment_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed', 'refunded'), default='pending')
    payment_date = db.Column(db.DateTime, default=db.func.current_timestamp())
