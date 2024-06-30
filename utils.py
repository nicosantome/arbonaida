from datetime import datetime, timedelta, date, time
from restaurant_config import OPENING_TIMES, INDOOR_CONFIGS, OUTDOOR_CONFIGS, CLOSED_DAYS, DEFAULT_RULES, EXCEPTION_RULES
from bookings import create_app, db
from bookings.models import TableAvailability, TableConfig
import json


def is_closed(date):
    for period in CLOSED_DAYS:
        start_date = datetime.strptime(period['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(period['end_date'], '%Y-%m-%d').date()
        if start_date <= date <= end_date:
            return True
    return False


def create_time_slots(period):
    time_slots = []
    start_str, end_str = period.split('-')
    start_time = datetime.strptime(start_str, '%H:%M').time()
    end_time = datetime.strptime(end_str, '%H:%M').time()

    current_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)

    # Si end_time es menor o igual que start_time, entonces end_time es al día siguiente
    if end_time <= start_time:
        end_datetime += timedelta(days=1)

    while current_datetime < end_datetime:
        time_slots.append(current_datetime.time().strftime('%H:%M'))
        current_datetime += timedelta(minutes=15)

    return time_slots


def create_availability_records(date):
    if is_closed(date):
        return

    weekday = date.strftime('%A')

    if weekday in OPENING_TIMES:
        for shift, period in OPENING_TIMES[weekday].items():

            if period:
                time_slots = create_time_slots(period)
                config_index = 0  # Aquí puedes seleccionar la configuración correcta

                indoor_config = INDOOR_CONFIGS[config_index]
                outdoor_config = OUTDOOR_CONFIGS[config_index]

                indoor_tables = generate_table_ids(indoor_config, 'indoor')
                outdoor_tables = generate_table_ids(outdoor_config, 'outdoor')

                for table_id in indoor_tables + outdoor_tables:
                    for slot in time_slots:
                        availability_record = TableAvailability(
                            date=date,
                            table_id=table_id,
                            time_slot=slot,
                            is_available=True
                        )
                        db.session.add(availability_record)

                # Record the used configuration for the date and shift
                indoor_config_record = TableConfig(
                    date=date,
                    shift=shift,
                    location='indoor',
                    config_index=config_index,
                    config=json.dumps(indoor_config)
                )
                db.session.add(indoor_config_record)

                outdoor_config_record = TableConfig(
                    date=date,
                    shift=shift,
                    location='outdoor',
                    config_index=config_index,
                    config=json.dumps(outdoor_config)
                )
                db.session.add(outdoor_config_record)

        db.session.commit()


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


def get_reservation_rules(date_str):
    if date_str in EXCEPTION_RULES:
        return EXCEPTION_RULES[date_str]
    return DEFAULT_RULES


def check_availability(num_people, date_str, location):
    app = create_app()
    with app.app_context():
        # Convertir la fecha de string a objeto date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Asegurarse de que los registros de disponibilidad existen
        ensure_availability_records(date_obj)

        # Obtener las reglas de reserva para la fecha
        reservation_rules = get_reservation_rules(date_str)
        print("Reservation rules: ", reservation_rules)

        # Determinar los tipos de mesa que pueden aceptar la cantidad de personas
        valid_table_types = [table_type for table_type, rule in reservation_rules.items() if
                             rule['min_accept'] <= num_people <= rule['max_accept']]
        print("valid_table_types: ", valid_table_types)

        # Filtrar las mesas adecuadas por tipo de mesa y ubicación directamente en la consulta a la base de datos
        if location == 'outdoor':
            available_timeslots_query = TableAvailability.query.filter(
                TableAvailability.date == date_obj,
                TableAvailability.is_available == True,
                db.func.substring(TableAvailability.table_id, 1, 2).in_(valid_table_types),
                TableAvailability.table_id.endswith('_O')
            ).all()
        else:
            available_timeslots_query = TableAvailability.query.filter(
                TableAvailability.date == date_obj,
                TableAvailability.is_available == True,
                db.func.substring(TableAvailability.table_id, 1, 2).in_(valid_table_types),
                ~TableAvailability.table_id.endswith('_O')
            ).all()

        # Organizar las mesas por table_id y time_slot
        table_slots = {}
        for table in available_timeslots_query:
            if table.table_id not in table_slots:
                table_slots[table.table_id] = []
            table_slots[table.table_id].append(table.time_slot)

        # Función para verificar si los time_slots son consecutivos en intervalos de 15 minutos
        def is_valid_start_time(time_slots):
            time_format = '%H:%M'
            start_time = datetime.strptime(time_slots[0], time_format)
            end_time = datetime.strptime(time_slots[5], time_format)
            if end_time < start_time:
                end_time += timedelta(days=1)
            return end_time - start_time == timedelta(minutes=75)

        # Buscar start times válidos
        available_start_times = []
        start_times_checked = set()

        for table_id, slots in table_slots.items():
            for i in range(len(slots) - 5):  # Iterar hasta la penúltima secuencia de 6 intervalos
                consecutive_slots = slots[i:i + 6]
                start_time = consecutive_slots[0]

                # Verificar si los slots consecutivos son válidos
                if is_valid_start_time(consecutive_slots) and start_time not in start_times_checked:
                    available_start_times.append({
                        "start_time": start_time,
                        "table_id": table_id
                    })
                    start_times_checked.add(start_time)

        # Ordenar por start_time
        available_start_times.sort(key=lambda x: datetime.strptime(x['start_time'], '%H:%M'))

        return available_start_times


def ensure_availability_records(date):
    app = create_app()
    with app.app_context():
        existing_records = TableAvailability.query.filter_by(date=date).first()
        if not existing_records:
            create_availability_records(date)


# if __name__ == '__main__':
#     app = create_app()
#     with app.app_context():
#         db.create_all()  # Crea las tablas en la base de datos
#         example_date = date(2024, 6, 25)
#         create_availability_records(example_date)
# 22 - 23 - 25

if __name__ == '__main__':
    date_str = '2024-06-25'
    num_people = 2
    location = 'indoor'
    check_availability(num_people, date_str, location)



# if __name__ == '__main__':
#     create_time_slots('11:00-16:00')