from datetime import datetime, timedelta, date, time
from restaurant_config import OPENING_TIMES, INDOOR_CONFIGS, OUTDOOR_CONFIGS, CLOSED_DAYS, DEFAULT_RULES, EXCEPTION_RULES
from bookings import create_app, db
from bookings.models import TableAvailability, TableConfig
import json


def is_closed(target_date):
    """Verifica si el restaurante está cerrado en la fecha dada."""
    for period in CLOSED_DAYS:
        if period['start_date'] <= target_date <= period['end_date']:
            return True
    return False


def generate_time_slots(start_time, end_time):
    """Genera intervalos de tiempo de 15 minutos entre dos horas, manejando horarios que cruzan medianoche."""
    time_slots = []

    # Convertir `start_time` y `end_time` en datetime para realizar cálculos
    current_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)

    # Ajustar si el periodo cruza la medianoche
    if end_time <= start_time:
        end_datetime += timedelta(days=1)

    # Generar intervalos de 15 minutos hasta alcanzar `end_datetime`
    while current_datetime < end_datetime:
        time_slots.append(current_datetime.time().strftime('%H:%M'))
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
    time_slots = generate_time_slots(start_time, end_time)
    config_index = 0  # Aquí puedes seleccionar la configuración correcta

    indoor_config = INDOOR_CONFIGS[config_index]
    outdoor_config = OUTDOOR_CONFIGS[config_index]

    indoor_tables = generate_table_ids(indoor_config, 'indoor')
    outdoor_tables = generate_table_ids(outdoor_config, 'outdoor')

    for table_id in indoor_tables + outdoor_tables:
        for slot in time_slots:
            availability_record = TableAvailability(
                date=date_obj,
                table_id=table_id,
                time_slot=slot,
                is_available=True
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


def check_availability(num_people, date_obj, location):
    app = create_app()
    with app.app_context():
        ensure_availability_records(date_obj)
        reservation_rules = get_reservation_rules(date_obj)

        valid_table_types = get_valid_table_types(num_people, reservation_rules)
        available_timeslots_query = query_available_timeslots(date_obj, location, valid_table_types)

        table_slots = organize_time_slots_by_table(available_timeslots_query)
        print(table_slots)
        available_start_times = find_valid_start_times(table_slots)

        return available_start_times


def get_valid_table_types(num_people, reservation_rules):
    """Obtiene los tipos de mesa válidos que pueden aceptar la cantidad de personas."""
    return [
        table_type for table_type, rule in reservation_rules.items()
        if rule['min_accept'] <= num_people <= rule['max_accept']
    ]


def query_available_timeslots(date_obj, location, valid_table_types):
    """Consulta la base de datos para obtener los timeslots disponibles según la ubicación y tipos de mesa."""
    if location == 'outdoor':
        return TableAvailability.query.filter(
            TableAvailability.date == date_obj,
            TableAvailability.is_available == True,
            db.func.substring(TableAvailability.table_id, 1, 2).in_(valid_table_types),
            TableAvailability.table_id.endswith('_O')
        ).all()
    else:
        return TableAvailability.query.filter(
            TableAvailability.date == date_obj,
            TableAvailability.is_available == True,
            db.func.substring(TableAvailability.table_id, 1, 2).in_(valid_table_types),
            ~TableAvailability.table_id.endswith('_O')
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

    available_start_times.sort(key=lambda x: datetime.strptime(x['start_time'], '%H:%M'))
    print(available_start_times)
    return available_start_times


def is_valid_start_time(time_slots):
    """Verifica si los time_slots son consecutivos en intervalos de 15 minutos."""
    time_format = '%H:%M'
    start_time = datetime.strptime(time_slots[0], time_format)
    end_time = datetime.strptime(time_slots[5], time_format)
    if end_time < start_time:
        end_time += timedelta(days=1)
    return end_time - start_time == timedelta(minutes=75)


def ensure_availability_records(date_obj):
    app = create_app()
    with app.app_context():
        existing_records = TableAvailability.query.filter_by(date=date_obj).first()
        if not existing_records:
            create_availability_records(date_obj)

