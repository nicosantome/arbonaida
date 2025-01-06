from datetime import datetime, timedelta
from celery.utils.time import maybe_make_aware
from restaurant_config import OPENING_TIMES, INDOOR_CONFIGS, OUTDOOR_CONFIGS, CLOSED_DAYS, DEFAULT_RULES, \
    EXCEPTION_RULES, TIEMPO_DE_RESERVA, MOVILES_PERSONAL, TIEMPO_RECORDATORIO
from bookings import create_app, db
from bookings.models import TableAvailability, TableConfig, Customer, Booking
from bookings.mail import send_email
from bookings.whatsapp import send_whatsapp_message, create_new_booking_template
from bookings.tasks import enviar_recordatorio, printo
from pytz import timezone
import json

from sqlalchemy.exc import IntegrityError


def is_closed(target_date):
    """Check if the restaurant is closed on the given date."""
    for period in CLOSED_DAYS:
        if period['start_date'] <= target_date <= period['end_date']:
            return True
    return False


def generate_time_slots(start_time, end_time=None, num_intervals=6):
    """
    Generate 15-minute time intervals between two times or a specific number of intervals from a single start_time.

    - If only start_time is provided, generates num_intervals of 15-minute intervals from start_time.
    - If both start_time and end_time are provided, generates 15-minute intervals between those times.
    """
    time_slots = []
    current_datetime = datetime.combine(datetime.today(), start_time)

    # If end_time is provided, generate until end_time
    if end_time:
        end_datetime = datetime.combine(datetime.today(), end_time)

        # Adjust if the period crosses midnight
        if end_time <= start_time:
            end_datetime += timedelta(days=1)

        while current_datetime < end_datetime:
            time_slots.append(current_datetime.time())  # Store as time object
            current_datetime += timedelta(minutes=15)

    # If end_time is not provided, generate num_intervals of 15-minute intervals from start_time
    else:
        for _ in range(num_intervals):
            time_slots.append(current_datetime.time())  # Store as time object
            current_datetime += timedelta(minutes=15)

    return time_slots


def create_availability_records(date_obj):
    """Create availability records for a given date if the restaurant is open."""
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
    """Helper function to process a specific shift (lunch or dinner)."""
    # Create 15-minute time slots for the given period
    time_slots = generate_time_slots(start_time, end_time)  # Now returns datetime.time objects
    config_index = 0  # Here you can select the correct configuration

    indoor_config = INDOOR_CONFIGS[config_index]
    outdoor_config = OUTDOOR_CONFIGS[config_index]

    # Generate tables according to shift and location
    indoor_tables = generate_table_ids(indoor_config, 'indoor')
    outdoor_tables = generate_table_ids(outdoor_config, 'outdoor')

    # Process each table and each time slot
    for table_id in indoor_tables + outdoor_tables:
        for slot in time_slots:
            availability_record = TableAvailability(
                date=date_obj,
                table_id=table_id,
                time_slot=slot,
                is_available=True,
            )
            db.session.add(availability_record)

    # Record the configuration used for the date and shift
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
    """Generate table IDs based on the configuration and location."""
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
    """Get reservation rules for a specific date, falling back to default rules if not specified."""
    if date_obj in EXCEPTION_RULES:
        return EXCEPTION_RULES[date_obj]
    return DEFAULT_RULES


def check_availability(booking_data, booking_id=None):
    """Main function to check table availability."""

    app = create_app()
    with app.app_context():
        ensure_availability_records(booking_data['date'])
        reservation_rules = get_reservation_rules(booking_data['date'])

        valid_table_types = get_valid_table_types(booking_data['num_people'], reservation_rules)
        available_timeslots_query = query_available_timeslots(booking_data['date'], booking_data['location'], valid_table_types, booking_id)

        table_slots = organize_time_slots_by_table(available_timeslots_query)
        available_start_times = find_valid_start_times(table_slots)
        if booking_data.get('timeslot'):
            # Filter available times that match the requested timeslot
            matched_times = [
                time for time in available_start_times
                if time['start_time'] == booking_data['timeslot']
            ]
            return matched_times
        print(available_start_times)
        return available_start_times


def get_valid_table_types(num_people, reservation_rules):
    """Get valid table types that can accommodate the given number of people."""
    return [
        table_type for table_type, rule in reservation_rules.items()
        if rule['min_accept'] <= num_people <= rule['max_accept']
    ]


def query_available_timeslots(date_obj, location, valid_table_types, booking_id):
    """Query the database for available timeslots based on location and table types."""
    if location == 'outdoor':
        if booking_id is None:
            # When there's no booking_id, we only look for available slots
            return TableAvailability.query.filter(
                TableAvailability.date == date_obj,
                TableAvailability.is_available == True,
                db.func.substring(TableAvailability.table_id, 1, 2).in_(valid_table_types),
                TableAvailability.table_id.endswith('_O')
            ).all()
        else:
            # When there's a booking_id, we look for available slots + those occupied by the same booking_id
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
            # When there's no booking_id, we only look for available slots
            return TableAvailability.query.filter(
                TableAvailability.date == date_obj,
                TableAvailability.is_available == True,
                db.func.substring(TableAvailability.table_id, 1, 2).in_(valid_table_types),
                ~TableAvailability.table_id.endswith('_O')
            ).all()
        else:
            # When there's a booking_id, we look for available slots + those occupied by the same booking_id
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
    """Organize available time slots by table ID."""
    table_slots = {}
    for table in available_timeslots_query:
        if table.table_id not in table_slots:
            table_slots[table.table_id] = []
        table_slots[table.table_id].append(table.time_slot)
    return table_slots


def find_valid_start_times(table_slots):
    """Find valid start times for available tables."""
    available_start_times = []
    start_times_checked = set()

    for table_id, slots in table_slots.items():
        for i in range(len(slots) - 5):  # Iterate up to the penultimate sequence of 6 intervals
            consecutive_slots = slots[i:i + 6]
            start_time = consecutive_slots[0]

            if is_valid_start_time(consecutive_slots) and start_time not in start_times_checked:
                available_start_times.append({
                    "start_time": start_time,
                    "table_id": table_id
                })
                start_times_checked.add(start_time)

    available_start_times.sort(key=lambda x: x['start_time'])  # No need to convert to str anymore
    return available_start_times


def is_valid_start_time(time_slots):
    """Check if the time slots are consecutive in 15-minute intervals."""
    start_time = datetime.combine(datetime.today(), time_slots[0])
    end_time = datetime.combine(datetime.today(), time_slots[5])

    # Adjust if crossing midnight
    if end_time < start_time:
        end_time += timedelta(days=1)

    return end_time - start_time == timedelta(minutes=75)


def ensure_availability_records(date_obj):
    """Ensure availability records exist for the given date."""
    app = create_app()
    with app.app_context():
        existing_records = TableAvailability.query.filter_by(date=date_obj).first()
        if not existing_records:
            create_availability_records(date_obj)


def make_booking(booking_data, customer_data):
    """Main function to create a booking."""
    # Check availability
    available_times = check_availability(booking_data, booking_id=None)
    if not available_times:
        return False, "No tables available for the requested time."

    selected_table_id = available_times[0]['table_id']
    selected_start_time = booking_data['timeslot']

    # Retrieve or create customer
    customer = get_or_create_customer(customer_data)
    if not customer:
        return False, "Error registering the customer."

    # Create booking record
    booking_id = create_booking_record(booking_data, customer.id, selected_table_id, selected_start_time)
    if not booking_id:
        return False, "Error creating the reservation."

    # Update availability
    update_availability_slots(booking_data['date'], selected_table_id, selected_start_time, booking_id, action="set")

    # Send confirmation email (commented out)
    # send_email(customer_data['email'], customer_data['name'], booking_data['date'], booking_data['timeslot'])

    # Send new booking WhatsApp message
    new_bkg_template = create_new_booking_template(booking_data, customer_data['name'])
    send_whatsapp_message(new_bkg_template)

    # Schedule reminder (commented out)
    booking = Booking.query.get(booking_id)  # Get the created booking
    print('booking_data:', booking_data)
    # programar_recordatorio(booking_data, booking)
    print(booking_id)
    # In the part that calls the task:
    # result = enviar_recordatorio.apply_async(args=[booking_id], countdown=10)
    # if result:
    #     print(f"Task scheduled: {result.id}")
    # else:
    #     print("Error scheduling the task.")

    return True, "Reservation made successfully."


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
        return booking.id
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
    # Calculate the 6 consecutive slots that need to be updated
    slots_to_update = [
        (datetime.combine(datetime.today(), start_time) + timedelta(minutes=15 * i)).time()
        for i in range(6)
    ]

    # Configure parameters based on the action
    if action == "set":
        update_data = {"is_available": False, "booking_id": booking_id}
    elif action == "remove":
        update_data = {"is_available": True, "booking_id": None}
    else:
        raise ValueError("Invalid action. Use 'set' or 'remove'.")

    # Update the selected slots
    TableAvailability.query.filter(
        TableAvailability.date == date_obj,
        TableAvailability.table_id == table_id,
        TableAvailability.time_slot.in_(slots_to_update)
    ).update(update_data, synchronize_session='fetch')

    # Commit changes to the database
    db.session.commit()


def get_future_bookings():
    """Retrieves all future active bookings from the database."""
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
            'time': booking.start_time,  # Ensure this attribute is correct
            'customer_name': booking.customer.name,  # Relationship with Customer
            'num_people': booking.num_people,
            'location': booking.location
        })
    print(booking_data)
    return booking_data


def set_status_false(booking_id):
    """Sets the status of a booking to False (cancelled)."""
    booking = Booking.query.get(booking_id)
    if booking:
        booking.status = False  # Change the booking status to cancelled
        db.session.commit()
    else:
        return "Booking not found", 404


def tiempo_recordatorio(booking_data):
    """
    Calculates the reminder send time based on the booking time
    adjusted to the "Europe/Madrid" timezone.
    """
    # Combine the date and time of the booking and adjust the timezone
    reserva_datetime = datetime.combine(
        booking_data['date'], booking_data['timeslot']
    )
    # Adjust the timezone to Europe/Madrid
    reserva_datetime = timezone("Europe/Madrid").localize(reserva_datetime)

    # Subtract the reminder time
    return reserva_datetime - timedelta(hours=TIEMPO_RECORDATORIO)


# def programar_recordatorio(booking_data, booking):
#     """
#     Schedules a booking reminder for the customer in the local timezone.
#     """
#     # Calculate the reminder time
#     recordatorio_datetime = tiempo_recordatorio(booking_data)
#     print(f"ETA for the reminder: {recordatorio_datetime}")
#
#     # Get the current time in the same timezone
#     now = datetime.now(timezone("Europe/Madrid"))
#
#
#     # Ensure the reminder is in the future
#     if recordatorio_datetime > now:
#         task = enviar_recordatorio.apply_async(
#             (booking_data), eta=recordatorio_datetime
#         )
#         booking.task_id = task.id  # Save the task_id in the booking
#         db.session.commit()
#         print(f"Task scheduled with ID: {task.id}")
#     else:
#         print("Cannot schedule the reminder because the time has already passed.")