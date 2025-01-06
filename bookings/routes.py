from flask import current_app as app, render_template, request, jsonify, flash, redirect, url_for
from utils import check_availability, make_booking, get_future_bookings, set_status_false, update_availability_slots
from .forms import ReservationForm
from datetime import datetime
from bookings import db
from .models import Booking


@app.route('/', methods=['GET', 'POST'])
def home():
    form = ReservationForm()

    if form.validate_on_submit():
        # Extracts data from the form
        date_str = form.date.data.strftime('%Y-%m-%d')
        booking_data = {
            'date': datetime.strptime(date_str, '%Y-%m-%d').date(),
            'timeslot': datetime.strptime(form.timeslot.data, '%H:%M').time(),
            'num_people': int(form.num_people.data),
            'location': form.location.data
        }

        customer_data = {
            'name': form.name.data,
            'phone': form.phone.data,
            'email': form.email.data
        }
        # Mak the booking
        success, message = make_booking(booking_data, customer_data)

        if success:
            flash('Booking confirmed.')
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

    available_times = check_availability(booking_data, request.args.get('booking_id'))

    # Convert time objects in serializable strings 'HH:MM'
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
    data = get_future_bookings()  # Get future bookings
    for booking in data:
        # Convert string '13:00:00' to '13:00'
        booking['time'] = booking['time'].strftime("%H:%M")
    return render_template('admin.html', data=data)


@app.route('/admin/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    """Rout to cancel a booking."""
    booking = Booking.query.get_or_404(booking_id)
    set_status_false(booking_id)
    update_availability_slots(booking.date, booking.table_id, booking.start_time, booking_id, action="remove")

    return redirect('/admin')


@app.route('/admin/edit/<int:booking_id>', methods=['POST'])
def edit_booking(booking_id):
    """Route to edit an existing booking."""
    booking = Booking.query.get_or_404(booking_id)

    try:
        update_availability_slots(booking.date, booking.table_id, booking.start_time, booking_id, action="remove")
        # Convert the form date to an date object
        new_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        new_time = datetime.strptime(request.form[
            'timeslot'], '%H:%M').time()
        new_num_people = int(request.form['num_people'])
        new_location = request.form['location']

        # Update booking with new values
        booking.date = new_date
        booking.start_time = new_time
        booking.num_people = new_num_people
        booking.location = new_location

        booking_data = {
            'date': new_date,
            'timeslot': new_time,
            'num_people': new_num_people,
            'location': new_location
        }

        available_times = check_availability(booking_data, booking_id)
        if not available_times:
            return False, "No availability for the requested time."

        selected_table_id = available_times[0]['table_id']

        # Update availability
        update_availability_slots(booking.date, selected_table_id, booking.start_time, booking_id, action="set")

        # Save changees in database
        db.session.commit()
        flash('Booking succesfully updated', 'success')
        return redirect(url_for('admin'))

    except Exception as e:
        db.session.rollback()
        flash(f'Unable to modify booking: {str(e)}', 'danger')
        return redirect(url_for('admin'))