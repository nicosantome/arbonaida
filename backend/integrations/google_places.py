import requests

GOOGLE_MAPS_API_KEY = 'AIzaSyDNRnNigwF0tKH8Ts8HgeA62wRC3O-Ru6M'
ARBONAIDA_ID = 'ChIJYbRen3koQg0RnD4R2EuPahk'

def fetch_opening_hours():
    arbonaida_params = {'place_id': ARBONAIDA_ID, 'key': GOOGLE_MAPS_API_KEY}
    arbonaida_data = requests.get('https://maps.googleapis.com/maps/api/place/details/json', params=arbonaida_params)
    opening_hours = arbonaida_data.json()['result']['opening_hours']

    return opening_hours