from flask import current_app as app, render_template, request, jsonify, flash, redirect, url_for
from utils import check_availability, make_booking, get_future_bookings
from .forms import ReservationForm
from datetime import datetime
from bookings import db


@app.route('/', methods=['GET', 'POST'])
def home():
    form = ReservationForm()

    if form.validate_on_submit():
        # Extraer datos del formulario
        date_str = form.date.data.strftime('%Y-%m-%d')
        booking_data = {
            'date': datetime.strptime(date_str, '%Y-%m-%d').date(),
            'timeslot': datetime.strptime(form.timeslot.data, '%H:%M').time(),
            'num_people': int(form.num_people.data),
            'location': form.location.data
        }
        print(booking_data['timeslot'], type(booking_data['timeslot']))
        # Información del cliente
        customer_data = {
            'name': form.name.data,
            'phone': form.phone.data,
            'email': form.email.data
        }
        print('route')
        # Hacer la reserva
        success, message = make_booking(booking_data, customer_data)

        if success:
            flash('Reserva confirmada con éxito.')
        else:
            flash(message)

        return redirect(url_for('home'))

    return render_template('home.html', form=form)


@app.route('/check_availability', methods=['GET'])
def check_availability_route():
    date_str = request.args.get('date')
    booking_data = {
        'date': datetime.strptime(date_str, '%Y-%m-%d').date(),
        'num_people': int(request.args.get('num_people')),
        'location': request.args.get('location')
    }

    available_times = check_availability(booking_data)

    # Convertir objetos de tiempo a cadena 'HH:MM'
    available_times_serializable = [
        {
            'start_time': time_data['start_time'].strftime('%H:%M'),
            'table_id': time_data['table_id']
        }
        for time_data in available_times
    ]

    return jsonify({'available_times': available_times_serializable})


@app.route('/admin', methods=['GET'])
def admin():
    data = get_future_bookings()  # Llamar a la función para obtener las reservas futuras
    return render_template('admin.html', data=data)


@app.route('/admin/edit/<int:booking_id>', methods=['GET', 'POST'])
def edit_booking(booking_id):
    # Lógica para obtener los detalles de la reserva y procesar la edición
    # Implementa la lógica para manejar el formulario de edición aquí
    pass


@app.route('/admin/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    """Ruta para cancelar una reserva."""
    from models import Booking
    from utils import release_table_availability  # Importamos la función para liberar la disponibilidad de la mesa

    booking = Booking.query.get(booking_id)
    if booking:
        booking.status = False  # Cambiar el estado de la reserva a cancelado
        db.session.commit()

        # Liberar la disponibilidad de la mesa para la reserva cancelada
        release_table_availability(booking.date, booking.table_id, booking.start_time)

        return redirect('/admin')
    else:
        return "Reserva no encontrada", 404