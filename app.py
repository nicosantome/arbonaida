from flask import Flask, render_template, jsonify, request
from database import get_reservation_data

app = Flask(__name__)

@app.route('/')
def hello_world():
  return render_template('home.html')

@app.route('/getReservationData')
def fetch_db_doc():
  if request.method == 'POST':
      data = request.get_json()
      date = data.get('date')

      # Llama a la función de base de datos para obtener los datos de la reserva
      reservation_data = get_reservation_data(date)

      # Devuelve los datos obtenidos como respuesta en formato JSON
      return jsonify(reservation_data)
  
if __name__ == '__main__':
  app.run(host= '0.0.0.0', debug=True)