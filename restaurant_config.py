# Días de apertura
OPENING_DAYS = ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Horarios de apertura
OPENING_TIMES = {
    'Tuesday': {'lunch': '13:00-16:00', 'dinner': '19:00-00:00'},
    'Wednesday': {'lunch': '13:00-16:00', 'dinner': '19:00-00:00'},
    'Thursday': {'lunch': '13:00-16:00', 'dinner': '19:00-00:00'},
    'Friday': {'lunch': '13:00-16:00', 'dinner': '19:00-01:00'},
    'Saturday': {'lunch': '13:00-16:00', 'dinner': '19:00-01:00'},
    'Sunday': {'lunch': '13:00-17:00', 'dinner': None}
}

# Días de cerrado
CLOSED_DAYS = [
    {'start_date': '2024-08-01', 'end_date': '2024-08-31'},  # Ejemplo de período de vacaciones
    {'start_date': '2024-09-10', 'end_date': '2024-09-10'},  # Ejemplo de día suelto
]

# Configuraciones de mesas estándar y alternativas para indoor y outdoor
INDOOR_CONFIGS = [{
    '2p': 6,
    '4p': 3,
    '5p': 1
}, {
    '2p': 5,
    '4p': 2,
    '5p': 1,
    '6p': 1
}]

OUTDOOR_CONFIGS = [
    {'3p': 3},
    {'3p': 1, '6p': 1}
]


DEFAULT_RULES = {
    '2p': {'min_accept': 1, 'max_accept': 2},
    '3p': {'min_accept': 2, 'max_accept': 3},
    '4p': {'min_accept': 2, 'max_accept': 4},
    '5p': {'min_accept': 3, 'max_accept': 5}
}

# Excepciones de reglas de reserva para fechas específicas
EXCEPTION_RULES = {
    '2024-05-15': {
        '2p': {'min_accept': 2, 'max_accept': 2},
        '4p': {'min_accept': 4, 'max_accept': 4},
        '5p': {'min_accept': 5, 'max_accept': 5}
    }
}