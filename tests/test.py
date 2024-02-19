from datetime import datetime, timedelta, time

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
DINNER_WKND_OUTDOOR = (time(20, 0), time(0, 0))

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
            time_config = calculate_interval_count(DINNER_WK)
        elif is_outdoor == False:
            time_config = calculate_interval_count(DINNER_WKND)
        else:
            time_config = calculate_interval_count(DINNER_WKND_OUTDOOR)

    else:

        if day_of_week < 5:  # Monday to Thursday
            time_config = calculate_interval_count(LUNCH_WK)
        elif day_of_week == 4:  # Friday
            time_config = calculate_interval_count(LUNCH_FRIDAY)
        else:  # Saturday and Sunday
            time_config = calculate_interval_count(LUNCH_SAT_SUN)

    # Create table configurations based on the provided capacity and count
    for capacity, count in config.items():
        tables[capacity] = {}
        for i in range(count):
            table_key = f"{chr(65 + i)}"
            intervals = time_config
            tables[capacity][table_key] = [True] * intervals  # Use the calculated intervals
    return tables


print(create_tables(TABLES_CONFIG['outdoor']['standard_outdoor'], datetime.now(), is_outdoor=True, is_dinner=False))