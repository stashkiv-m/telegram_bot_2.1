import random

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Bot
import os
import json

from language_state import language_state

Telegram_token = '7721716265:AAEuzhZyZM_pT0FQHsbx-FziENEg-cNT5do'


def send_message_to_all_users(message: str):
    # Використовуйте лише один з варіантів:
    # 1. Для сервера:
    # credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    # credentials_data = json.loads(credentials_json)

    # 2. Для локального запуску:
    local_credentials_path = 'C:/Users/Mykhailo/PycharmProjects/telegram_bot_2.1/general/general_data_base/telegram-bot-user-list-79452f202a61.json'
    with open(local_credentials_path, 'r') as file:
        credentials_data = json.load(file)

    # Налаштування Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_data, scope)
    client = gspread.authorize(creds)

    # Отримання доступу до таблиці за її ID
    sheet = client.open_by_key('1nZv5QBo_excPo402Ul-a278hyB2-rQbYfqlCcHu-524')
    worksheet = sheet.get_worksheet(0)  # Отримання першого аркуша таблиці

    # Ініціалізація бота з вашим токеном
    bot = Bot(token='7749471664:AAEp85bkb0szrSBDso9bxU2FSy8JU0RVSEY')  # замініть на ваш токен

    # Зберігаємо унікальні User ID
    unique_user_ids = set()

    # Читаємо дані користувачів з Google Таблиці
    users_data = worksheet.get_all_records()
    for row in users_data:
        user_id = row.get('ID')
        if user_id and user_id not in unique_user_ids:
            # Додаємо user_id до множини унікальних ID
            unique_user_ids.add(user_id)

            # Відправляємо повідомлення користувачу
            try:
                bot.send_message(chat_id=user_id, text=message)
                print(f"Повідомлення надіслано користувачу {user_id}")
            except Exception as e:
                print(f"Не вдалося надіслати повідомлення користувачу {user_id}. Помилка: {e}")


def send_image_to_all_users():

    # Використовуйте лише один з варіантів:
    # 1. Для сервера:
    # credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    # credentials_data = json.loads(credentials_json)

    # 2. Для локального запуску:
    local_credentials_path = 'C:/Users/Mykhailo/PycharmProjects/telegram_bot_2.1/general/general_data_base/telegram-bot-user-list-79452f202a61.json'
    with open(local_credentials_path, 'r') as file:
        credentials_data = json.load(file)

    # Налаштування Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_data, scope)
    client = gspread.authorize(creds)

    # Отримання доступу до таблиці за її ID
    sheet = client.open_by_key('1nZv5QBo_excPo402Ul-a278hyB2-rQbYfqlCcHu-524')
    worksheet = sheet.get_worksheet(0)  # Отримання першого аркуша таблиці

    # Ініціалізація бота з вашим токеном
    bot = Bot(token='7749471664:AAEp85bkb0szrSBDso9bxU2FSy8JU0RVSEY')  # замініть на ваш токен

    # Зберігаємо унікальні User ID
    unique_user_ids = set()

    # Читаємо дані користувачів з Google Таблиці
    users_data = worksheet.get_all_records()
    for row in users_data:
        user_id = row.get('ID')
        if user_id and user_id not in unique_user_ids:
            # Додаємо user_id до множини унікальних ID
            unique_user_ids.add(user_id)

            # Вибираємо рандомне зображення з папки
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            img_folder = os.path.join(base_dir, 'img', 'exchange_img')
            print(f"Папка зображень: {img_folder}")  # Додано для відлагодження

            try:
                images = [f for f in os.listdir(img_folder) if os.path.isfile(os.path.join(img_folder, f))]
                if images:
                    random_image = random.choice(images)
                    image_path = os.path.join(img_folder, random_image)

                    # Відправляємо зображення користувачу
                    with open(image_path, 'rb') as photo:
                        bot.send_photo(chat_id=user_id, photo=photo)
                    print(f"Зображення {random_image} надіслано користувачу {user_id}")
                else:
                    print(f"У папці {img_folder} немає зображень.")
            except FileNotFoundError:
                print(f"Папка з зображеннями не знайдена за шляхом: {img_folder}")
            except Exception as e:
                print(f"Не вдалося надіслати зображення користувачу {user_id}. Помилка: {e}")

