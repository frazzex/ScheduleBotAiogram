from datetime import date



def is_even_week_from_september(target_date: date | None = None) -> bool:
    if target_date is None:
        target_date = date.today()

    year = target_date.year
    september_start = date(year, 9, 1)

    if target_date < september_start:
        september_start = date(year - 1, 9, 1)

    days_since_september = (target_date - september_start).days
    week_number = days_since_september // 7 + 1
    return week_number % 2 == 0


def time_to_minutes(time_str: str) -> int:
    time_parts = time_str.split(':')
    return int(time_parts[0]) * 60 + int(time_parts[1])
