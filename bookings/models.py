from bookings import db
from sqlalchemy import Time


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    bookings = db.relationship('Booking', backref='customer', lazy=True)
    comments = db.relationship('Comment', backref='customer', lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    table_id = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    num_people = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(10), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=True)
    task_id = db.Column(db.String(50), nullable=True)


class TableAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    table_id = db.Column(db.String(5), nullable=False)  # Ejemplo: '2pA'
    time_slot = db.Column(Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))


class TableConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    shift = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(10), nullable=False)
    config_index = db.Column(db.Integer, nullable=False)
    config = db.Column(db.String, nullable=False)