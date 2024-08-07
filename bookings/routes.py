from flask import current_app as app, render_template, request, jsonify, flash, redirect, url_for
from utils import check_availability
from .forms import ReservationForm


@app.route('/', methods=['GET', 'POST'])
def home():
    form = ReservationForm()

    if request.method == 'POST':
        print('This prints')
        print('Form data:', request.form)

        if form.validate_on_submit():
            print('This doesnt print')
            num_people = form.num_people.data
            date = form.date.data.strftime('%Y-%m-%d')
            location = form.location.data
            timeslot = form.timeslot.data
            name = form.name.data
            phone = form.phone.data
            email = form.email.data

            # Aquí puedes procesar la reserva, guardar en la base de datos, etc.
            # Supongamos que la reserva se realiza con éxito:
            flash('Reserva confirmada con éxito.')
            print('Received confirm')
            return redirect(url_for('home'))
        else:
            print('Validation errors:', form.errors)

    return render_template('home.html', form=form)


@app.route('/check_availability', methods=['GET'])
def check_availability_route():
    num_people = int(request.args.get('num_people'))
    date = request.args.get('date')
    location = request.args.get('location')
    available_times = check_availability(num_people, date, location)
    return jsonify({'available_times': available_times})