import requests
import re
from datetime import datetime, timedelta, time


from config import (
    TABLES_CONFIG,
    LUNCH_WK, LUNCH_FRIDAY, LUNCH_SAT_SUN,
    DINNER_WK, DINNER_WKND, DINNER_WKND_OUTDOOR
)


def convert_time(time_str):
    return time(int(time_str[:2]), int(time_str[2:]))


# def calculate_placeholder():
#     now = datetime.now()
#     day_of_week = now.strftime('%A')
#
#     if day_of_week == 'Monday':
#         placeholder_date = (now + timedelta(days=1)).strftime('%Y-%m-%d')
#         placeholder_time = '13:00'
#     else:
#         schedule = RESTAURANT_SCHEDULE[day_of_week]
#         current_time = now.time()
#
#         if current_time < schedule['commercial'][0]:
#             placeholder_date = now.strftime('%Y-%m-%d')
#             placeholder_time = schedule['commercial'][0].strftime('%H:%M')
#         elif current_time < schedule['commercial'][1]:
#             placeholder_date = now.strftime('%Y-%m-%d')
#             placeholder_time = schedule['commercial'][1].strftime('%H:%M')
#         else:
#             placeholder_date = (now + timedelta(days=1)).strftime('%Y-%m-%d')
#             placeholder_time = schedule['commercial'][0].strftime('%H:%M')
#
#     return placeholder_date, placeholder_time

def calculate_interval_count(interval):
    """Calculate the number of 15 minutes intervals in given time range
        Parameters:
        - time_range (tuple): A tuple containing two time objects representing the start and end times.
        Returns:
        - int: The number of 15 minutes intervals in given range.
        """
    start_time, end_time = interval

    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute

    if end_minutes < start_minutes:
        end_minutes += 24 * 60

    duration_minutes = end_minutes - start_minutes
    intervals = duration_minutes // 15

    return intervals


def create_tables(config, date, is_dinner=False, is_outdoor=False):
    """Create table configurations based on the given configuration and date.

    Parameters:
    - config (dict): A dictionary containing table capacities and counts.
    - date (datetime): The date for which the table configurations are created.
    - is_dinner (bool): A flag indicating if the tables are for dinner service.
    - is_outdoor (bool): A flag indicating if the tables are outdoor tables.

    Returns:
    - dict: A dictionary representing the table configurations based on the provided parameters.
    """
    tables = {}
    day_of_week = date.weekday()
    # Determine the time configuration based on the service type and the day of the week
    if is_dinner:
        if day_of_week < 5:
            intervals = calculate_interval_count(DINNER_WK)
        elif is_outdoor == False:
            intervals = calculate_interval_count(DINNER_WKND)
        else:
            intervals = calculate_interval_count(DINNER_WKND_OUTDOOR)

    else:

        if day_of_week < 5:  # Monday to Thursday
            intervals = calculate_interval_count(LUNCH_WK)
        elif day_of_week == 4:  # Friday
            intervals = calculate_interval_count(LUNCH_FRIDAY)
        else:  # Saturday and Sunday
            intervals = calculate_interval_count(LUNCH_SAT_SUN)

    # Create table configurations based on the provided capacity and count
    for capacity, count in config.items():
        tables[capacity] = {}
        for i in range(count):
            table_key = f"{chr(65 + i)}"
            tables[capacity][table_key] = [True] * intervals  # Use the calculated intervals
    return tables


def create_availability_record(date):
    """ Create an availability record for a given date based on the opening times and table configuration.
       Parameters:
       - date (datetime): The date for which the availability record is to be created.
       Returns:
       - dict: An availability record object for the given date. """

    day_of_week = date.weekday()
    is_sunday = day_of_week == 6

    record = {
        'date': date.strftime("%d-%m-%Y"),

        'lunch': {
            'indoor': {
                'config': TABLES_CONFIG['indoor']['standard_indoor'],
                'tables': create_tables(TABLES_CONFIG['indoor']['standard_indoor'], date)

            },
            'outdoor': {
                'config': TABLES_CONFIG['outdoor']['standard_outdoor'],
                'tables': create_tables(TABLES_CONFIG['outdoor']['standard_outdoor'], date, is_outdoor=True)
            }
        }

    }

    if not is_sunday:
        record['dinner'] = {
            'indoor': {
                'config': TABLES_CONFIG['indoor']['standard_indoor'],
                'tables': create_tables(TABLES_CONFIG['indoor']['standard_indoor'], date, is_dinner=True)
            },
            'outdoor': {
                'config': TABLES_CONFIG['outdoor']['standard_outdoor'],
                'tables': create_tables(TABLES_CONFIG['outdoor']['standard_outdoor'], date, is_dinner=True)
            }
        }

    return record



# def format_opening_text(opening_text):
#     table_html = '<table class="WgFkxc"><tbody>'
#
#     for entry in opening_text:
#         match = re.search(r'(\w+):\s*(.*)', entry)
#         if match:
#             day = match.group(1)
#             schedule = match.group(2)
#             table_html += f'<tr><td class="SKNSIb">{day}</td><td>{schedule}</td></tr>'
#
#     table_html += '</tbody></table>'
#     return table_html



# opening = fetch_opening_hours()
# opening_text = opening['weekday_text']
# formatted_opening = format_opening_text(opening_text)


# def is_commerce_open(date, time):
#     opening_hours = opening['periods']
#     input_datetime = datetime.strptime(date, '%Y-%m-%d')
#     input_day_of_week = (input_datetime.weekday() + 1) % 7
#     input_time = datetime.strptime(time, '%H:%M').time()
#
#     for entry in opening_hours:
#         open_day = entry['open']['day']
#         close_day = entry['close']['day']
#         open_time = datetime.strptime(entry['open']['time'], '%H%M').time()
#         close_time = datetime.strptime(entry['close']['time'], '%H%M').time()
#
#         if open_day == close_day == input_day_of_week:
#             if open_time <= input_time < close_time:
#                 return True
#         elif open_day == input_day_of_week and close_day == (input_day_of_week + 1) % 7:
#             if open_time <= input_time:
#                 return True
#         elif close_day == input_day_of_week and open_day == (input_day_of_week - 1) % 7:
#             if input_time < close_time:
#                 return True
#
#     return False
