from pymongo.server_api import ServerApi
from pymongo import MongoClient
import os

MONGODB_URI = os.environ['MONGODB_URI']
print(MONGODB_URI)


# Conexión a la base de datos
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))# Ajusta según la configuración de tu MongoDB
db = client.get_database("Arbonaida")
bookings_db = db.get_collection("Bookings")
availability_db = db.get_collection("Availability")

def get_reservation_data(date):
    # Lógica para obtener datos de la base de datos según la fecha
    # Realiza la consulta a la base de datos MongoDB usando la fecha proporcionada
    # Retorna los datos correspondientes

    # Ejemplo de consulta básica (ajusta según tu estructura de datos):
    result = collection.find_one({"date": date})
    return result
