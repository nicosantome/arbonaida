from datetime import datetime, time

# Aquí están las distintas configuraciones de mesas y los horarios

# Tiempos
# 1 intervalo = 15 minutos
LUNCH_TIME_CONFIG = 14 # Son 14 intervalos desde las 13 hasta las 16:30
DINNER_TIME_CONFIG = 16 # Son 16 intervalos desde las 20 hasta las 00:00

DINNER_TIME_CONFIG_OUTDOOR = 12 # La terraza cierra antes?

RESERVA_STANDARD = 6 # Son 6 intervalos - El tiempo de reserva default es 1hr 30mins
RESERVA_REDUCIDA = 4 # Son 4 intervalos - Es 1hr

# Espacios
TABLES_CONFIG = {
    'indoor': {'standard_indoor':{
                '2p': 6,
                '4p': 3,
                '5p': 1
            }},
    'outdoor': {'standard_outdoor':{
                '3p': 3
    }}
}

#Bookings availability windows
LUNCH_WK = (time(13, 0), time(16, 0))
LUNCH_FRIDAY = (time(13, 0), time(16, 30))
LUNCH_SAT_SUN = (time(13, 0), time(17, 00))
DINNER_WK = (time(20, 0), time(0, 0))
DINNER_WKND = (time(20, 0), time(0, 0))
DINNER_WKND_OUTDOOR = (time(20, 0), time(23, 0))




# # Definition of restaurant opening and closing hours for each day of the week
# RESTAURANT_SCHEDULE = {
#     'Monday': None,  # Closed on Monday
#     'Tuesday': {'commercial': {'indoor': [(OPENING_LUNCH, CLOSING_LUNCH_WK), (OPENING_DINNER, CLOSING_DINNER_WK)],
#                                 'outdoor': [(OPENING_LUNCH, CLOSING_LUNCH_WK), (OPENING_DINNER, CLOSING_DINNER_WK)]},
#                 'kitchen': {'indoor': [(OPENING_LUNCH, time(16, 0)), (time(19, 0), time(23, 30))],
#                             'outdoor': [(OPENING_LUNCH, time(23, 59))]}
#                },
#     'Wednesday': {'commercial': {'indoor': [(time(13, 0), time(16, 30)), (time(19, 0), time(23, 30))],
#                                   'outdoor': [(time(13, 0), time(23, 59))]},
#                   'kitchen': {'indoor': [(time(13, 0), time(16, 0)), (time(19, 0), time(23, 30))],
#                               'outdoor': [(time(13, 0), time(23, 59))]}
#                  },
#     'Thursday': {'commercial': {'indoor': [(time(13, 0), time(16, 30)), (time(19, 0), time(23, 30))],
#                                  'outdoor': [(time(13, 0), time(23, 59))]},
#                  'kitchen': {'indoor': [(time(13, 0), time(16, 0)), (time(19, 0), time(23, 30))],
#                              'outdoor': [(time(13, 0), time(23, 59))]}
#                 },
#     'Friday': {'commercial': {'indoor': [(time(13, 0), time(23, 59)), (time(0, 0), time(1, 0))],  # Cierre a la 1:00 AM del sábado
#                                'outdoor': [(time(13, 0), time(23, 59))]},
#                'kitchen': {'indoor': [(time(13, 0), time(16, 0)), (time(20, 0), time(23, 30))],
#                            'outdoor': [(time(13, 0), time(23, 59))]}
#               },
#     'Saturday': {'commercial': {'indoor': [(time(13, 0), time(23, 59)), (time(0, 0), time(1, 0))],  # Cierre a la 1:00 AM del domingo
#                                  'outdoor': [(time(13, 0), time(23, 59))]},
#                  'kitchen': {'indoor': [(time(13, 0), time(16, 0)), (time(20, 0), time(23, 30))],
#                              'outdoor': [(time(13, 0), time(23, 59))]}
#                 },
#     'Sunday': {'commercial': {'indoor': [(time(13, 0), time(17, 0))],
#                                'outdoor': [(time(13, 0), time(23, 59))]},
#                'kitchen': {'indoor': [(time(13, 0), time(16, 0))],
#                            'outdoor': [(time(13, 0), time(23, 59))]}
#               }
# }
