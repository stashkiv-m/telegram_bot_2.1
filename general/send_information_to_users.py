import investpy
import pandas as pd


# Функція для отримання важливих економічних подій
def get_important_economic_events(country='United States', from_date=None, to_date=None):
    """
    Отримує економічний календар для вказаної країни та періоду,
    фільтруючи події за високою важливістю.

    Параметри:
        country (str): Країна для фільтрації подій.
        from_date (str): Початкова дата у форматі 'дд/мм/рррр'.
        to_date (str): Кінцева дата у форматі 'дд/мм/рррр'.

    Повертає:
        pd.DataFrame: Таблиця з важливими подіями.
    """
    try:
        # Отримуємо економічний календар за вказаний період і країну
        calendar = investpy.news.economic_calendar(
            countries=[country],
            from_date=from_date,
            to_date=to_date
        )

        # Фільтруємо події за високою важливістю
        important_events = calendar[calendar['importance'] == 'high']

        # Перевірка, чи є результати
        if important_events.empty:
            print("Немає важливих подій для вказаного періоду.")
            return None

        # Налаштування відображення всіх колонок і рядків для кращого вигляду
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)

        return important_events

    except Exception as e:
        print(f"Error: {e}")
        return None


# Використання функції для отримання важливих подій
important_events = get_important_economic_events(from_date='27/10/2024', to_date='03/11/2024')

# Перевірка і вивід результатів
if important_events is not None:
    print(important_events)
else:
    print("Подій не знайдено або виникла помилка.")


