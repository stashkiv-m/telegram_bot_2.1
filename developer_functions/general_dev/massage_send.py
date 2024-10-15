import csv
import os
from telegram import Bot


def send_message_to_all_users(message: str):
    # Визначаємо базову директорію (директорія, де розташований цей скрипт)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Формуємо шлях до файлу з користувачами відносно базової директорії
    file_path = os.path.join(BASE_DIR, '..', '..', 'general', 'general_data_base', 'users_data.csv')

    # Перевіряємо, чи існує файл
    if not os.path.exists(file_path):
        print(f"Файл з даними користувачів не знайдено за шляхом: {file_path}")
        return

    # Ініціалізація бота з вашим токеном
    bot = Bot(token='7749471664:AAEp85bkb0szrSBDso9bxU2FSy8JU0RVSEY')

    # Зберігаємо унікальні User ID
    unique_user_ids = set()

    # Читаємо дані користувачів з CSV файлу
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            user_id = row.get('User ID')
            if user_id and user_id not in unique_user_ids:
                # Додаємо user_id до множини унікальних ID
                unique_user_ids.add(user_id)

                # Відправляємо повідомлення користувачу
                try:
                    bot.send_message(chat_id=user_id, text=message)
                    print(f"Повідомлення надіслано користувачу {user_id}")
                except Exception as e:
                    print(f"Не вдалося надіслати повідомлення користувачу {user_id}. Помилка: {e}")


# Виклик функції для відправки повідомлення всім унікальним користувачам

# send_message_to_users("Це тестове повідомлення для всіх користувачів!")
