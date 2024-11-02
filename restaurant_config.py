from datetime import date, time
# Días de apertura
OPENING_DAYS = ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Horarios de apertura
OPENING_TIMES = {
    'Tuesday': (time(13, 0), time(16, 0), time(19, 0), time(0, 0)),  # (lunch_start, lunch_end, dinner_start, dinner_end)
    'Wednesday': (time(13, 0), time(16, 0), time(19, 0), time(0, 0)),
    'Thursday': (time(13, 0), time(16, 0), time(19, 0), time(0, 0)),
    'Friday': (time(13, 0), time(16, 0), time(19, 0), time(1, 0)),
    'Saturday': (time(13, 0), time(16, 0), time(19, 0), time(1, 0)),
    'Sunday': (time(13, 0), time(17, 0), None, None)  # No hay cena
}

# Días de cerrado
CLOSED_DAYS = [
    {'start_date': date(2024, 8, 1), 'end_date': date(2024, 8, 31)},  # Ejemplo de período de vacaciones
    {'start_date': date(2024, 9, 10), 'end_date': date(2024, 9, 10)}  # Ejemplo de día suelto
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
    '5p': {'min_accept': 3, 'max_accept': 5},
    '6p': {'min_accept': 4, 'max_accept': 6}
}

# Excepciones de reglas de reserva para fechas específicas
EXCEPTION_RULES = {
    date(2024, 5, 15): {
        '2p': {'min_accept': 2, 'max_accept': 2},
        '4p': {'min_accept': 4, 'max_accept': 4},
        '5p': {'min_accept': 5, 'max_accept': 5}
    }
}