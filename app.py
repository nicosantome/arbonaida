from flask import Flask, render_template, jsonify, request
from database import get_reservation_data

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/getReservationData', methods=['POST'])
def fetch():
    # Get data from the request body
    data = request.json
    # Reformat the date before passing it to the get_reservation_data function 'yyyy-mm-dd' to 'dd-mm-yyyy'
    db_format_date = '-'.join(data.split('-')[::-1])

    # Call the get_reservation_data function with the reformatted date
    get_reservation_data(db_format_date)

    # Example test response
    response_data = {"status": "success", "message": "Data retrieved successfully"}

    # Return the data as a JSON response
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
