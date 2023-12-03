from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


MONGODB_URI = "mongodb+srv://nicosantome:VVgkgCBDyX77fqKF@cluster0.snvatrh.mongodb.net/?retryWrites=true&w=majority"

# os.environ['MONGODB_URI']
# print(MONGODB_URI)


# Conexión a la base de datos
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
db = client.get_database("Arbonaida")
bookings_db = db.get_collection("Bookings")
availability_db = db.get_collection("Availability")

def get_reservation_data(date):
  cursor = availability_db.find({'date': date})
  for document in cursor:
      print(document)
  

