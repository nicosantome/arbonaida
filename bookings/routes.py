from flask import current_app as app, render_template, request, jsonify
from utils import check_availability

# Define tus rutas aquí
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/check_availability', methods=['GET'])
def check_availability_route():
    num_people = int(request.args.get('num_people'))
    date = request.args.get('date')
    location = request.args.get('location')
    available_times = check_availability(num_people, date, location)
    return jsonify({'available_times': available_times})