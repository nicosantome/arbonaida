from flask import current_app as app, render_template, request, jsonify, flash, redirect, url_for
from utils import check_availability, make_booking, get_future_bookings, release_table_availability, set_status_false
from .forms import ReservationForm
from datetime import datetime
from bookings import db
from .models import Booking


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
        # Información del cliente
        customer_data = {
            'name': form.name.data,
            'phone': form.phone.data,
            'email': form.email.data
        }
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


@app.route('/admin/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    """Ruta para cancelar una reserva."""
    set_status_false(booking_id)
    release_table_availability(booking_id)

    return redirect('/admin')


@app.route('/admin/edit/<int:booking_id>', methods=['POST'])
def edit_booking(booking_id):
    # Obtener la reserva a modificar
    booking = Booking.query.get_or_404(booking_id)

    try:
        release_table_availability(booking_id)
        # TODO Guardar nuevos timeslots en tableavailability
        # Convertir la fecha del formulario a un objeto de tipo date
        new_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()  # Convertir cadena a objeto date

        # Obtener otros datos del formulario
        new_time = datetime.strptime(request.form[
            'timeslot'], '%H:%M').time()
        new_num_people = int(request.form['num_people'])
        new_location = request.form['location']


        # Actualizar la reserva con los nuevos valores
        booking.date = new_date
        booking.start_time = new_time
        booking.num_people = new_num_people
        booking.location = new_location

        # Guardar los cambios en la base de datos
        db.session.commit()
        flash('Reserva modificada exitosamente', 'success')
        return redirect(url_for('admin'))  # Cambia 'admin_panel' por tu endpoint de vista deseado

    except Exception as e:
        db.session.rollback()
        flash(f'Error al modificar la reserva: {str(e)}', 'danger')
        return redirect(url_for('admin'))