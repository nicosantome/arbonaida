from flask import current_app as app, render_template, request, jsonify, flash, redirect, url_for
from utils import check_availability
from .forms import ReservationForm
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
def home():
    form = ReservationForm()

    if form.validate_on_submit():
        num_people = form.num_people.data
        date = form.date.data.strftime('%Y-%m-%d')
        location = form.location.data
        timeslot = form.timeslot.data
        name = form.name.data
        phone = form.phone.data
        email = form.email.data
        # create booking, block avail
        flash('Reserva confirmada con éxito.')
        return redirect(url_for('home'))

    return render_template('home.html', form=form)


@app.route('/check_availability', methods=['GET'])
def check_availability_route():
    num_people = int(request.args.get('num_people'))
    date_str = request.args.get('date')
    location = request.args.get('location')

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    available_times = check_availability(num_people, date_obj, location)
    return jsonify({'available_times': available_times})