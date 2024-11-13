from datetime import datetime, timedelta
from restaurant_config import OPENING_TIMES, INDOOR_CONFIGS, OUTDOOR_CONFIGS, CLOSED_DAYS, DEFAULT_RULES, EXCEPTION_RULES, TIEMPO_DE_RESERVA
from bookings import create_app, db
from bookings.models import TableAvailability, TableConfig, Customer, Booking
from bookings.mail import send_email

import json

from sqlalchemy.exc import IntegrityError


def is_closed(target_date):
    """Verifica si el restaurante está cerrado en la fecha dada."""
    for period in CLOSED_DAYS:
        if period['start_date'] <= target_date <= period['end_date']:
            return True
    return False


def generate_time_slots(start_time, end_time=None, num_intervals=6):
    """
    Genera intervalos de tiempo de 15 minutos entre dos horas o una cantidad específica de intervalos a partir de un solo `start_time`.

    - Si se proporciona solo `start_time`, genera `num_intervals` intervalos de 15 minutos desde `start_time`.
    - Si se proporcionan ambos `start_time` y `end_time`, genera intervalos de 15 minutos entre esas horas.
    """
    time_slots = []
    current_datetime = datetime.combine(datetime.today(), start_time)

    # Si se proporciona end_time, genera hasta end_time
    if end_time:
        end_datetime = datetime.combine(datetime.today(), end_time)

        # Ajustar si el periodo cruza la medianoche
        if end_time <= start_time:
            end_datetime += timedelta(days=1)

        while current_datetime < end_datetime:
            time_slots.append(current_datetime.time())  # Guardar como objeto time
            current_datetime += timedelta(minutes=15)

    # Si no se proporciona end_time, genera `num_intervals` intervalos de 15 minutos desde `start_time`
    else:
        for _ in range(num_intervals):
            time_slots.append(current_datetime.time())  # Guardar como objeto time
            current_datetime += timedelta(minutes=15)

    return time_slots


def create_availability_records(date_obj):
    if is_closed(date_obj):
        return

    weekday = date_obj.strftime('%A')
    if weekday in OPENING_TIMES:
        lunch_start, lunch_end, dinner_start, dinner_end = OPENING_TIMES[weekday]
        if lunch_start and lunch_end:
            process_shift(date_obj, 'lunch', lunch_start, lunch_end)
        if dinner_start and dinner_end:
            process_shift(date_obj, 'dinner', dinner_start, dinner_end)

        db.session.commit()


def process_shift(date_obj, shift, start_time, end_time):
    """Función auxiliar para procesar un turno específico (almuerzo o cena)."""
    # Creamos franjas horarias de 15 minutos para el período dado
    time_slots = generate_time_slots(start_time, end_time)  # Ahora devuelve objetos `datetime.time`
    config_index = 0  # Aquí puedes seleccionar la configuración correcta

    indoor_config = INDOOR_CONFIGS[config_index]
    outdoor_config = OUTDOOR_CONFIGS[config_index]

    # Generamos las tablas de acuerdo con el turno y ubicación
    indoor_tables = generate_table_ids(indoor_config, 'indoor')
    outdoor_tables = generate_table_ids(outdoor_config, 'outdoor')

    # Procesamos cada mesa y cada franja horaria
    for table_id in indoor_tables + outdoor_tables:
        for slot in time_slots:
            availability_record = TableAvailability(
                date=date_obj,
                table_id=table_id,
                time_slot=slot,
                is_available=True,
            )
            db.session.add(availability_record)

    # Registro de la configuración utilizada para la fecha y turno
    indoor_config_record = TableConfig(
        date=date_obj,
        shift=shift,
        location='indoor',
        config_index=config_index,
        config=json.dumps(indoor_config)
    )
    db.session.add(indoor_config_record)

    outdoor_config_record = TableConfig(
        date=date_obj,
        shift=shift,
        location='outdoor',
        config_index=config_index,
        config=json.dumps(outdoor_config)
    )
    db.session.add(outdoor_config_record)



def generate_table_ids(config, location):
    table_ids = []
    for table_type, count in config.items():
        for i in range(count):
            suffix = chr(65 + i)
            table_id = f"{table_type}{suffix}"
            if location == 'outdoor':
                table_id = f"{table_id}_O"
            table_ids.append(table_id)
    return table_ids


def get_reservation_rules(date_obj):
    if date_obj in EXCEPTION_RULES:
        return EXCEPTION_RULES[date_obj]
    return DEFAULT_RULES


def check_availability(booking_data, booking_id=None):
    """Función principal para verificar la disponibilidad de mesas."""

    app = create_app()
    with app.app_context():
        ensure_availability_records(booking_data['date'])
        reservation_rules = get_reservation_rules(booking_data['date'])

        valid_table_types = get_valid_table_types(booking_data['num_people'], reservation_rules)
        available_timeslots_query = query_available_timeslots(booking_data['date'], booking_data['location'], valid_table_types, booking_id)

        table_slots = organize_time_slots_by_table(available_timeslots_query)
        available_start_times = find_valid_start_times(table_slots)
        if booking_data.get('timeslot'):
            # Filtrar los horarios disponibles que coincidan con el 'timeslot' solicitado
            matched_times = [
                time for time in available_start_times
                if time['start_time'] == booking_data['timeslot']
            ]
            return matched_times
        print(available_start_times)
        return available_start_times


def get_valid_table_types(num_people, reservation_rules):
    """Obtiene los tipos de mesa válidos que pueden aceptar la cantidad de personas."""
    return [
        table_type for table_type, rule in reservation_rules.items()
        if rule['min_accept'] <= num_people <= rule['max_accept']
    ]


def query_available_timeslots(date_obj, location, valid_table_types, booking_id):
    """Consulta la base de datos para obtener los timeslots disponibles según la ubicación y tipos de mesa."""
    if location == 'outdoor':
        if booking_id is None:
            # Cuando no hay booking_id, buscamos únicamente los disponibles
            return TableAvailability.query.filter(
                TableAvailability.date == date_obj,
                TableAvailability.is_available == True,
                db.func.substring(TableAvailability.table_id, 1, 2).in_(valid_table_types),
                TableAvailability.table_id.endswith('_O')
            ).all()
        else:
            # Cuando hay booking_id, buscamos disponibles + ocupados por el mismo booking_id
            return TableAvailability.query.filter(
                TableAvailability.date == date_obj,
                db.func.substring(TableAvailability.table_id, 1, 2).in_(valid_table_types),
                TableAvailability.table_id.endswith('_O')
            ).filter(
                db.or_(
                    TableAvailability.is_available == True,
                    db.and_(
                        TableAvailability.is_available == False,
                        TableAvailability.booking_id == booking_id
                    )
                )
            ).all()
    else:
        if booking_id is None:
            # Cuando no hay booking_id, buscamos únicamente los disponibles
            return TableAvailability.query.filter(
                TableAvailability.date == date_obj,
                TableAvailability.is_available == True,
                db.func.substring(TableAvailability.table_id, 1, 2).in_(valid_table_types),
                ~TableAvailability.table_id.endswith('_O')
            ).all()
        else:
            # Cuando hay booking_id, buscamos disponibles + ocupados por el mismo booking_id
            return TableAvailability.query.filter(
                TableAvailability.date == date_obj,
                db.func.substring(TableAvailability.table_id, 1, 2).in_(valid_table_types),
                ~TableAvailability.table_id.endswith('_O')
            ).filter(
                db.or_(
                    TableAvailability.is_available == True,
                    db.and_(
                        TableAvailability.is_available == False,
                        TableAvailability.booking_id == booking_id
                    )
                )
            ).all()


def organize_time_slots_by_table(available_timeslots_query):
    """Organiza los timeslots disponibles por ID de mesa."""
    table_slots = {}
    for table in available_timeslots_query:
        if table.table_id not in table_slots:
            table_slots[table.table_id] = []
        table_slots[table.table_id].append(table.time_slot)
    return table_slots


def find_valid_start_times(table_slots):
    """Encuentra los start times válidos para las mesas disponibles."""
    available_start_times = []
    start_times_checked = set()

    for table_id, slots in table_slots.items():
        for i in range(len(slots) - 5):  # Iterar hasta la penúltima secuencia de 6 intervalos
            consecutive_slots = slots[i:i + 6]
            start_time = consecutive_slots[0]

            if is_valid_start_time(consecutive_slots) and start_time not in start_times_checked:
                available_start_times.append({
                    "start_time": start_time,
                    "table_id": table_id
                })
                start_times_checked.add(start_time)

    available_start_times.sort(key=lambda x: x['start_time'])  # Ya no se necesita convertir a str
    return available_start_times


def is_valid_start_time(time_slots):
    """Verifica si los time_slots son consecutivos en intervalos de 15 minutos."""
    start_time = datetime.combine(datetime.today(), time_slots[0])
    end_time = datetime.combine(datetime.today(), time_slots[5])

    # Ajuste si cruza medianoche
    if end_time < start_time:
        end_time += timedelta(days=1)

    return end_time - start_time == timedelta(minutes=75)


def ensure_availability_records(date_obj):
    app = create_app()
    with app.app_context():
        existing_records = TableAvailability.query.filter_by(date=date_obj).first()
        if not existing_records:
            create_availability_records(date_obj)


def make_booking(booking_data, customer_data):
    """Handles the end-to-end table booking process."""

    # Check availability
    available_times = check_availability(booking_data, booking_id=None)
    if not available_times:
        return False, "No hay mesas disponibles para el horario solicitado."

    selected_table_id = available_times[0]['table_id']
    selected_start_time = booking_data['timeslot']

    # Retrieve or create customer
    customer = get_or_create_customer(customer_data)
    if not customer:
        return False, "Error al registrar el cliente."

    # Create booking record
    booking_id = create_booking_record(booking_data, customer.id, selected_table_id, selected_start_time)
    if not booking_id:
        return False, "Error al crear la reserva."

    # Update availability
    update_availability_slots(booking_data['date'], selected_table_id, selected_start_time, booking_id, action="set")

    # Send confirmation email
    send_email(customer_data['email'], customer_data['name'], booking_data['date'], booking_data['timeslot'])

    return True, "Reserva realizada con éxito."


def get_or_create_customer(customer_data):
    """Retrieves an existing customer or creates a new one."""
    customer = Customer.query.filter_by(email=customer_data['email']).first()
    if not customer:
        customer = Customer(
            name=customer_data['name'],
            phone=customer_data['phone'],
            email=customer_data['email']
        )
        try:
            db.session.add(customer)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
    return customer


def create_booking_record(booking_data, customer_id, table_id, start_time):
    """Creates a booking record for a customer at the specified table and time."""
    booking = Booking(
        date=booking_data['date'],
        table_id=table_id,
        start_time=start_time,
        num_people=booking_data['num_people'],
        location=booking_data['location'],
        customer_id=customer_id
    )
    try:
        db.session.add(booking)
        db.session.commit()
        return booking.id  # Devolver el ID del booking creado
    except IntegrityError:
        db.session.rollback()
        return None


def update_availability_slots(date_obj, table_id, start_time, booking_id, action="set"):
    """
    Updates the availability of timeslots based on the action.

    Args:
        date_obj (date): The date of the reservation.
        table_id (int): The table ID.
        start_time (time): The starting time of the reservation.
        booking_id (int): The ID of the booking.
        action (str): Either 'set' to mark timeslots as unavailable or 'remove' to mark them as available.
    """
    # Calculamos los 6 slots consecutivos que deben ser actualizados
    slots_to_update = [
        (datetime.combine(datetime.today(), start_time) + timedelta(minutes=15 * i)).time()
        for i in range(6)
    ]

    # Configurar parámetros según la acción
    if action == "set":
        update_data = {"is_available": False, "booking_id": booking_id}
    elif action == "remove":
        update_data = {"is_available": True, "booking_id": None}
    else:
        raise ValueError("Invalid action. Use 'set' or 'remove'.")

    # Actualizamos los slots seleccionados
    TableAvailability.query.filter(
        TableAvailability.date == date_obj,
        TableAvailability.table_id == table_id,
        TableAvailability.time_slot.in_(slots_to_update)
    ).update(update_data, synchronize_session='fetch')

    # Confirmamos los cambios en la base de datos
    db.session.commit()

def get_future_bookings():
    """Obtiene todas las reservas futuras de la base de datos con estado activo."""
    current_date = datetime.now().date()
    bookings = Booking.query.join(Customer).filter(
        Booking.date >= current_date,
        Booking.status == True
    ).order_by(Booking.date.asc()).all()

    booking_data = []
    for booking in bookings:
        booking_data.append({
            'id': booking.id,
            'date': booking.date,
            'time': booking.start_time,  # Asegúrate de que el atributo es correcto
            'customer_name': booking.customer.name,  # Relación con Customer
            'num_people': booking.num_people,
            'location': booking.location
        })
    print(booking_data)

    return booking_data


def set_status_false(booking_id):
    booking = Booking.query.get(booking_id)
    if booking:
        booking.status = False  # Cambiar el estado de la reserva a cancelado
        db.session.commit()
    else:
        return "Reserva no encontrada", 404

