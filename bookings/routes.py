from flask import current_app as app, render_template, request, jsonify, flash, redirect, url_for
from utils import check_availability, make_booking
from .forms import ReservationForm
from datetime import datetime


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