import os
from datetime import datetime, timedelta
import investpy
from developer_functions.general_dev.massage_and_img_send import send_file_to_all_users, send_message_to_all_users

# Базова директорія для збереження файлів
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def send_important_economic_events(country='United States'):
    try:
        today = datetime.today()
        future_date = (today + timedelta(days=3)).strftime('%d/%m/%Y')
        today_str = today.strftime('%d/%m/%Y')

        calendar = investpy.news.economic_calendar(
            countries=[country],
            from_date=today_str,
            to_date=future_date
        )

        # Видаляємо колонку 'actual' для оптимізації
        important_events = calendar[calendar['importance'] == 'high']
        important_events = important_events[['date', 'time', 'event', 'forecast', 'previous']]

        def format_date(date_str):
            # Форматуємо дату у форматі 'день/місяць'
            event_date = datetime.strptime(date_str, '%d/%m/%Y')
            return event_date.strftime('%d/%m')

        important_events['date'] = important_events['date'].apply(format_date)

        if not important_events.empty:
            # Замість таблиці, виводимо інформацію простим текстом
            event_lines = []
            for _, row in important_events.iterrows():
                event_text = row['event'][:20]  # Обрізаємо текст події до 20 символів
                forecast_text = f"Fcst: {row['forecast']}" if row['forecast'] else "Fcst: N/A"
                previous_text = f"Prev: {row['previous']}" if row['previous'] else "Prev: N/A"

                # Форматуємо кожен рядок без розділення колонок
                line = f"{row['date']} {row['time']} - {event_text} {forecast_text} {previous_text}"
                event_lines.append(line)

            # Додаємо заголовок для інформативності
            formatted_text = f"Economic Events for {today_str}\n\n" + "\n".join(event_lines)

            # Додаємо інформацію про часовий пояс
            formatted_text += "\n\n* All times are in Eastern Standard Time (EST)"

            # Формуємо шлях до файлу з поточною датою
            formatted_massage = (
                f"Important Economic Events for {today_str}\n\n"
                "Please check the details below to stay informed about key economic events.\n\n"
            )
            send_message_to_all_users(formatted_massage)
            file_name = f"Important economic_events_{today.strftime('%Y-%m-%d')}.txt"
            file_path = os.path.join(BASE_DIR, 'developer_functions', 'stock_dev', file_name)
            print("Скоригований file_path:", file_path)  # Перевірка шляху

            # Записуємо текст у файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_text)

            send_file_to_all_users(file_path)
            print("Файл успішно відправлено користувачам.")
        else:
            print("Немає важливих подій для вказаного періоду.")

    except Exception as e:
        print(f"Error: {e}")


