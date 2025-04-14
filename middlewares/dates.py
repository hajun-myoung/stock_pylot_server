from datetime import datetime, timedelta


def get_weekdays_between(start_date: str, end_date: str):
    """
    Get all weekdays between two dates.
    :param start_date: Start date in 'YYYY-MM-DD' format.
    :param end_date: End date in 'YYYY-MM-DD' format.
    :return: List of weekdays in 'YYYY-MM-DD' format.
    """
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    weekdays = []

    # print("GET WEEKDAYS BETWEEN")
    # print(start, end)

    for n in range(int((end - start).days) + 1):
        day = start + timedelta(n)
        if day.weekday() < 5:  # Monday to Friday are considered weekdays
            weekdays.append(day.strftime("%Y%m%d"))

    return weekdays
