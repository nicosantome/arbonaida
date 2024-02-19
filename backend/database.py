from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

MONGODB_URI = "mongodb+srv://nicosantome:VVgkgCBDyX77fqKF@cluster0.snvatrh.mongodb.net/?retryWrites=true&w=majority"
SERVER_API = ServerApi('1')


class Database:
    def __init__(self, uri, database_name):
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client.get_database(database_name)

# Instanciar la base de datos
database = Database(MONGODB_URI, "Arbonaida")

# Clase para manejar la colección de reservas
class BookingsDB:
    def __init__(self):
        self.collection = database.db.get_collection("Bookings")

    def save(self, booking_data):
        return self.collection.insert_one(booking_data)

    def get(self, booking_id):
        return self.collection.find_one({"_id": booking_id})

    def delete(self, booking_id):
        return self.collection.delete_one({"_id": booking_id})

# Clase para manejar la colección de disponibilidad
class AvailabilityDB:
    def __init__(self):
        self.collection = database.db.get_collection("Availability")

    def save(self, availability_data):
        return self.collection.insert_one(availability_data)

    def get(self, date):
        return self.collection.find_one({'date': date})

    def delete(self, date):
        return self.collection.delete_one({'date': date})


class ClientsDB:
    def __init__(self):
        self.collection = database.db.get_collection("Clients")

    def save(self, client_data):
        return self.collection.insert_one(client_data)

    def get(self, client_id):
        return self.collection.find_one({'_id': client_id})

    def delete(self, client_id):
        return self.collection.delete_one({'_id': client_id})