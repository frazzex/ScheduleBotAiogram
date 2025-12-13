"""
Скрипт для заполнения базы данных расписанием из существующих данных
"""
import asyncio
from datetime import datetime
from database import init_db, close_db
from models import Subject, Lesson


async def fill_schedule():
    """Заполнение базы данных расписанием"""
    await init_db()
    
    # Словарь для маппинга названий предметов
    subjects_data = {
        "Основы российской государственности": "Основы российской государственности",
        "Математический анализ": "Математический анализ",
        "Иностранный язык": "Иностранный язык",
        "Архитектура вычислительных систем": "Архитектура вычислительных систем",
        "Циклические виды спорта (по выбору)": "Циклические виды спорта (по выбору)",
        "Языки программирования": "Языки программирования",
        "История России": "История России",
        "Информатика": "Информатика",
        "Алгебра и геометрия": "Алгебра и геометрия",
        "Введение в профессиональную деятельность": "Введение в профессиональную деятельность"
    }
    
    # Создаем предметы
    subjects = {}
    for name in subjects_data.values():
        subject, created = await Subject.get_or_create(name=name)
        subjects[name] = subject
    
    # Маппинг дней недели
    days_map = {
        "Понедельник": 0,
        "Вторник": 1,
        "Среда": 2,
        "Четверг": 3,
        "Пятница": 4,
        "Суббота": 5,
        "Воскресенье": 6
    }
    
    # Расписание для четной недели
    even_lessons = [
        # Понедельник
        {"day": "Понедельник", "time": "8:00-9:35", "subject": "Основы российской государственности", 
         "type": "пр", "teacher": "ст. пр. Нестеров Д.В.", "classroom": "2219", "week": "even"},
        {"day": "Понедельник", "time": "9:45-11:20", "subject": "Математический анализ", 
         "type": "л", "teacher": "доц. Жалнина А.А.", "classroom": "2115", "week": "even"},
        {"day": "Понедельник", "time": "11:45-13:20", "subject": "Иностранный язык", 
         "type": "пр", "teacher": "доц. Сергейчик Т.С.", "classroom": "5203", "week": "even", "subgroup": 1},
        {"day": "Понедельник", "time": "11:45-13:20", "subject": "Архитектура вычислительных систем", 
         "type": "лаб", "teacher": "асс. Лось М.А.", "classroom": "2131а", "week": "even", "subgroup": 2},
        {"day": "Понедельник", "time": "13:30-15:05", "subject": "Циклические виды спорта (по выбору)", 
         "type": "пр", "teacher": "ст. пр. Тюкалова С.А.", "classroom": "лыжная база", "week": "even"},
        
        # Вторник
        {"day": "Вторник", "time": "9:45-11:20", "subject": "Языки программирования", 
         "type": "лаб", "teacher": "асс. Дунанов И.О.", "classroom": "21306", "week": "even", "subgroup": 1},
        {"day": "Вторник", "time": "11:45-13:20", "subject": "История России", 
         "type": "пр", "teacher": "асс. Сирюкин И.В.", "classroom": "5221", "week": "even"},
        {"day": "Вторник", "time": "13:30-15:05", "subject": "Основы российской государственности", 
         "type": "л", "teacher": "доц. Пьянов А.Е.", "classroom": "4бл", "week": "even"},
        {"day": "Вторник", "time": "15:30-17:05", "subject": "Информатика", 
         "type": "л", "teacher": "зав. каф. Степанов Ю.А.", "classroom": "2226", "week": "even"},
        
        # Среда
        {"day": "Среда", "time": "9:45-11:20", "subject": "Математический анализ", 
         "type": "пр", "teacher": "асс. Ануфриев Д.А.", "classroom": "5121", "week": "even"},
        {"day": "Среда", "time": "11:45-13:20", "subject": "Циклические виды спорта (по выбору)", 
         "type": "пр", "teacher": "ст. пр. Тюкалова С.А.", "classroom": "лыжная база", "week": "even"},
        {"day": "Среда", "time": "13:30-15:05", "subject": "История России", 
         "type": "л", "teacher": "ст. пр. Ганенок В.Ю.", "classroom": "2бл", "week": "even"},
        {"day": "Среда", "time": "15:30-17:05", "subject": "Алгебра и геометрия", 
         "type": "пр", "teacher": "проф. Медведев А.В.", "classroom": "5106", "week": "even"},
        
        # Четверг
        {"day": "Четверг", "time": "9:45-11:20", "subject": "Информатика", 
         "type": "лаб", "teacher": "асс. Лаврова В.И.", "classroom": "21306", "week": "even"},
        {"day": "Четверг", "time": "11:45-13:20", "subject": "Языки программирования", 
         "type": "л", "teacher": "доц. Бондарева Л.В.", "classroom": "2226", "week": "even"},
        {"day": "Четверг", "time": "13:30-15:05", "subject": "Иностранный язык", 
         "type": "пр", "teacher": "доц. Сергейчик Т.С.", "classroom": "5109", "week": "even", "subgroup": 1},
        {"day": "Четверг", "time": "13:30-15:05", "subject": "Информатика", 
         "type": "лаб", "teacher": "асс. Лаврова В.И.", "classroom": "21306", "week": "even", "subgroup": 2},
        {"day": "Четверг", "time": "15:30-17:05", "subject": "Иностранный язык", 
         "type": "пр", "teacher": "доц. Сергейчик Т.С.", "classroom": "5109", "week": "even", "subgroup": 2},
        {"day": "Четверг", "time": "17:15-18:50", "subject": "Языки программирования", 
         "type": "лаб", "teacher": "асс. Дунанов И.О.", "classroom": "2130б", "week": "even", "subgroup": 2},
        
        # Пятница
        {"day": "Пятница", "time": "11:45-13:20", "subject": "Алгебра и геометрия", 
         "type": "л", "teacher": "проф. Медведев А.В.", "classroom": "2114", "week": "even"},
        {"day": "Пятница", "time": "13:30-15:05", "subject": "Архитектура вычислительных систем", 
         "type": "л", "teacher": "доц. Чеботарев А.Л.", "classroom": "3304", "week": "even"},
        {"day": "Пятница", "time": "15:30-17:05", "subject": "Введение в профессиональную деятельность", 
         "type": "лаб", "teacher": "асс. Пасютин А.С.", "classroom": "2131в", "week": "even", "subgroup": 1},
        {"day": "Пятница", "time": "17:15-18:50", "subject": "Введение в профессиональную деятельность", 
         "type": "лаб", "teacher": "асс. Пасютин А.С.", "classroom": "2131в", "week": "even", "subgroup": 1},
    ]
    
    # Расписание для нечетной недели
    odd_lessons = [
        # Понедельник
        {"day": "Понедельник", "time": "8:00-9:35", "subject": "Основы российской государственности", 
         "type": "пр", "teacher": "ст. пр. Нестеров Д.В.", "classroom": "2219", "week": "odd"},
        {"day": "Понедельник", "time": "9:45-11:20", "subject": "Математический анализ", 
         "type": "л", "teacher": "доц. Жалнина А.А.", "classroom": "2115", "week": "odd"},
        {"day": "Понедельник", "time": "11:45-13:20", "subject": "Архитектура вычислительных систем", 
         "type": "лаб", "teacher": "асс. Лось М.А.", "classroom": "2131в", "week": "odd"},
        {"day": "Понедельник", "time": "11:45-13:20", "subject": "Иностранный язык", 
         "type": "пр", "teacher": "доц. Сергейчик Т.С.", "classroom": "5203", "week": "odd"},
        {"day": "Понедельник", "time": "13:30-15:05", "subject": "Циклические виды спорта (по выбору)", 
         "type": "пр", "teacher": "ст. пр. Тюкалова С.А.", "classroom": "лыжная база", "week": "odd"},
        
        # Вторник
        {"day": "Вторник", "time": "9:45-11:20", "subject": "Языки программирования", 
         "type": "лаб", "teacher": "асс. Дунанов И.О.", "classroom": "21306", "week": "odd", "subgroup": 1},
        {"day": "Вторник", "time": "11:45-13:20", "subject": "История России", 
         "type": "пр", "teacher": "асс. Сирюкин И.В.", "classroom": "5221", "week": "odd"},
        {"day": "Вторник", "time": "13:30-15:05", "subject": "Введение в профессиональную деятельность", 
         "type": "л", "teacher": "доц. Бондарева Л.В.", "classroom": "2219", "week": "odd"},
        {"day": "Вторник", "time": "15:30-17:05", "subject": "Информатика", 
         "type": "л", "teacher": "зав. каф. Степанов Ю.А.", "classroom": "2226", "week": "odd"},
        
        # Среда
        {"day": "Среда", "time": "9:45-11:20", "subject": "Математический анализ", 
         "type": "пр", "teacher": "асс. Ануфриев Д.А.", "classroom": "5121", "week": "odd"},
        {"day": "Среда", "time": "11:45-13:20", "subject": "Циклические виды спорта (по выбору)", 
         "type": "пр", "teacher": "ст. пр. Тюкалова С.А.", "classroom": "лыжная база", "week": "odd"},
        {"day": "Среда", "time": "13:30-15:05", "subject": "История России", 
         "type": "л", "teacher": "ст. пр. Ганенок В.Ю.", "classroom": "2бл", "week": "odd"},
        {"day": "Среда", "time": "15:30-17:05", "subject": "Алгебра и геометрия", 
         "type": "пр", "teacher": "проф. Медведев А.В.", "classroom": "5106", "week": "odd"},
        
        # Четверг
        {"day": "Четверг", "time": "9:45-11:20", "subject": "Информатика", 
         "type": "лаб", "teacher": "асс. Лаврова В.И.", "classroom": "21306", "week": "odd"},
        {"day": "Четверг", "time": "11:45-13:20", "subject": "Языки программирования", 
         "type": "л", "teacher": "доц. Бондарева Л.В.", "classroom": "2226", "week": "odd"},
        {"day": "Четверг", "time": "13:30-15:05", "subject": "Иностранный язык", 
         "type": "пр", "teacher": "доц. Сергейчик Т.С.", "classroom": "5109", "week": "odd", "subgroup": 1},
        {"day": "Четверг", "time": "13:30-15:05", "subject": "Информатика", 
         "type": "лаб", "teacher": "асс. Лаврова В.И.", "classroom": "21306", "week": "odd", "subgroup": 2},
        {"day": "Четверг", "time": "15:30-17:05", "subject": "Иностранный язык", 
         "type": "пр", "teacher": "доц. Сергейчик Т.С.", "classroom": "5109", "week": "odd", "subgroup": 2},
        {"day": "Четверг", "time": "17:15-18:50", "subject": "Языки программирования", 
         "type": "лаб", "teacher": "асс. Дунанов И.О.", "classroom": "2130б", "week": "odd", "subgroup": 2},
        
        # Пятница
        {"day": "Пятница", "time": "11:45-13:20", "subject": "Алгебра и геометрия", 
         "type": "л", "teacher": "проф. Медведев А.В.", "classroom": "2114", "week": "odd"},
        {"day": "Пятница", "time": "13:30-15:05", "subject": "Архитектура вычислительных систем", 
         "type": "л", "teacher": "доц. Чеботарев А.Л.", "classroom": "3304", "week": "odd"},
        {"day": "Пятница", "time": "15:30-17:05", "subject": "Введение в профессиональную деятельность", 
         "type": "лаб", "teacher": "асс. Пасютин А.С.", "classroom": "2131в", "week": "odd", "subgroup": 2},
        {"day": "Пятница", "time": "17:15-18:50", "subject": "Введение в профессиональную деятельность", 
         "type": "лаб", "teacher": "асс. Пасютин А.С.", "classroom": "2131в", "week": "odd", "subgroup": 2},
    ]
    
    all_lessons = even_lessons + odd_lessons
    
    # Очищаем существующие пары
    await Lesson.all().delete()
    
    def normalize_time(time_str: str) -> str:
        """Нормализует время в формат HH:MM с ведущим нулем"""
        if not time_str:
            return ""
        parts = time_str.strip().split(':')
        if len(parts) == 2:
            hour = parts[0].zfill(2)  # Добавляем ведущий ноль, если нужно
            minute = parts[1].zfill(2)
            return f"{hour}:{minute}"
        return time_str
    
    # Создаем пары
    for lesson_data in all_lessons:
        time_parts = lesson_data["time"].split("-")
        start_time = normalize_time(time_parts[0].strip())
        end_time = normalize_time(time_parts[1].strip() if len(time_parts) > 1 else "")
        
        await Lesson.create(
            subject=subjects[lesson_data["subject"]],
            day_of_week=days_map[lesson_data["day"]],
            start_time=start_time,
            end_time=end_time,
            lesson_type=lesson_data["type"],
            teacher=lesson_data.get("teacher"),
            classroom=lesson_data.get("classroom"),
            week_type=lesson_data.get("week"),
            subgroup=lesson_data.get("subgroup")
        )
    
    print(f"Создано {len(all_lessons)} пар в базе данных")
    
    await close_db()


if __name__ == "__main__":
    asyncio.run(fill_schedule())

