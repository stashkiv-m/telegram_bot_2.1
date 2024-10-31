import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Bot
import os
import json
import random

# Ініціалізація глобальних змінних
bot = None
worksheet = None

def initialize_bot_and_sheet():

    global bot, worksheet

    # Налаштування для роботи на сервері або локально
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
        # Варіант для сервера
        credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        credentials_data = json.loads(credentials_json)
    else:
        # Варіант для локального запуску
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

    # Ініціалізація бота з токеном
    bot_token = '7749471664:AAEp85bkb0szrSBDso9bxU2FSy8JU0RVSEY'
    bot = Bot(token=bot_token)

# Викликаємо функцію ініціалізації на початку
initialize_bot_and_sheet()

def send_message_to_all_users(message: str):
    unique_user_ids = set()
    users_data = worksheet.get_all_records()
    for row in users_data:
        user_id = row.get('ID')
        if user_id and user_id not in unique_user_ids:
            unique_user_ids.add(user_id)
            try:
                bot.send_message(chat_id=user_id, text=message)
                print(f"Повідомлення надіслано користувачу {user_id}")
            except Exception as e:
                print(f"Не вдалося надіслати повідомлення користувачу {user_id}. Помилка: {e}")

def send_image_to_all_users():
    unique_user_ids = set()
    users_data = worksheet.get_all_records()
    for row in users_data:
        user_id = row.get('ID')
        if user_id and user_id not in unique_user_ids:
            unique_user_ids.add(user_id)

            # Вибираємо рандомне зображення з папки
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            img_folder = os.path.join(base_dir, 'img', 'exchange_img')
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

def send_file_to_all_users(file_path: str):
    unique_user_ids = set()
    users_data = worksheet.get_all_records()
    for row in users_data:
        user_id = row.get('ID')
        if user_id and user_id not in unique_user_ids:
            unique_user_ids.add(user_id)
            try:
                with open(file_path, 'rb') as file:
                    bot.send_document(chat_id=user_id, document=file)
                print(f"Файл надіслано користувачу {user_id}")
            except Exception as e:
                print(f"Не вдалося надіслати файл користувачу {user_id}. Помилка: {e}")
