from flask import current_app as app, render_template, request, jsonify, flash, redirect, url_for
from utils import check_availability
from .forms import ReservationForm


@app.route('/', methods=['GET', 'POST'])
def home():
    form = ReservationForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            num_people = form.num_people.data
            date = form.date.data.strftime('%Y-%m-%d')
            location = 'indoor' if form.location.data else 'outdoor'
            timeslot = form.timeslot.data
            name = form.name.data
            phone = form.phone.data
            email = form.email.data

            # Aquí puedes procesar la reserva, guardar en la base de datos, etc.
            # Supongamos que la reserva se realiza con éxito:
            flash('Reserva confirmada con éxito.')
            return redirect(url_for('home'))

    return render_template('home.html', form=form)


@app.route('/check_availability', methods=['GET'])
def check_availability_route():
    num_people = int(request.args.get('num_people'))
    date = request.args.get('date')
    location = request.args.get('location')
    available_times = check_availability(num_people, date, location)
    return jsonify({'available_times': available_times})