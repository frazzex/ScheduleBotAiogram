from datetime import datetime

def is_even_week_from_september() -> bool:
    today = datetime.now().date()
    september_start = datetime(today.year, 9, 1).date()
    if today < september_start:
        september_start = datetime(today.year - 1, 9, 1).date()
    days_since_september = (today - september_start).days

    week_number = days_since_september // 7 + 1

    return week_number % 2 == 0


def time_to_minutes(time_str: str) -> int:
    """Преобразует время в формате 'HH:MM' в минуты с начала дня"""
    try:
        parts = time_str.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return 0
    except (ValueError, AttributeError):
        return 0