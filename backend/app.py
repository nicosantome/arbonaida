from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

@app.route('/', methods=['GET'])
def new_booking():
    return render_template('new_booking.html')

@app.route('/create_booking', methods=['POST'])
def create_booking():
    if request.method == 'POST':
        # Obtener los datos del formulario
        people = request.form['people']
        date = request.form['date']
        time = request.form['time']
        location = request.form['location']

        # Aquí puedes procesar los datos, guardar en la base de datos, etc.
        # Por ahora, simplemente imprimo los datos en la consola
        print(f'Booking Details: People={people}, Date={date}, Time={time}, Location={location}')

        # Redirigir a una página de éxito o a donde sea necesario
        return redirect('/success')

@app.route('/success')
def success():
    return "Booking Successful!"

if __name__ == '__main__':
    app.run(debug=True)
