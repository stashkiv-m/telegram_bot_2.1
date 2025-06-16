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


def send_image_to_all_users(image_path=None):
    unique_user_ids = set()
    users_data = worksheet.get_all_records()
    for row in users_data:
        user_id = row.get('ID')
        if user_id and user_id not in unique_user_ids:
            unique_user_ids.add(user_id)

            # Використовуємо передане зображення або обираємо рандомне, якщо шлях не вказано
            if image_path:
                final_image_path = image_path
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                img_folder = os.path.join(base_dir, 'img', 'exchange_img')
                images = [f for f in os.listdir(img_folder) if os.path.isfile(os.path.join(img_folder, f))]
                if images:
                    random_image = random.choice(images)
                    final_image_path = os.path.join(img_folder, random_image)
                else:
                    print(f"У папці {img_folder} немає зображень.")
                    continue

            # Відправляємо зображення користувачу
            try:
                with open(final_image_path, 'rb') as photo:
                    bot.send_photo(chat_id=user_id, photo=photo)
                print(f"Зображення {final_image_path} надіслано користувачу {user_id}")
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


def send_chart_and_metrics_to_all_users(image_path: str, metrics_text: str):
    """
    Надсилає зображення з графіком та текст з метриками всім користувачам.
    """
    unique_user_ids = set()
    users_data = worksheet.get_all_records()
    for row in users_data:
        user_id = row.get('ID')
        if user_id and user_id not in unique_user_ids:
            unique_user_ids.add(user_id)
            try:
                with open(image_path, 'rb') as photo:
                    bot.send_photo(chat_id=user_id, photo=photo, caption=metrics_text[:1024], parse_mode='Markdown')
                    if len(metrics_text) > 1024:
                        bot.send_message(chat_id=user_id, text=metrics_text[1024:], parse_mode='Markdown')
                print(f"Графік + метрики надіслано користувачу {user_id}")
            except Exception as e:
                print(f"Не вдалося надіслати повідомлення користувачу {user_id}. Помилка: {e}")

text = (
    "Привіт, мої дорогі користувачі! Це Міша.\n\n"
    "Я хочу подякувати вам за мотивацію, яку ви мені даєте. Навіть якщо ви давно не заходили або не були активними — я дуже ціную, що ви зацікавились ідеєю бота.\n\n"
    "Я ціную кожен ваш клік ❤️\n\n"
    "Я щойно оновив бота: тепер сигнали надходитимуть автоматично — вам не потрібно робити абсолютно нічого.\n\n"
    "Я врахував усі ваші побажання і продовжуватиму працювати, навіть якщо тут залишиться тільки один користувач.\n\n"
    "Буду дуже вдячний, якщо ви поділитесь ботом зі знайомими. Він абсолютно безкоштовний і таким залишиться.\n\n"
    "Моя ціль — зібрати думки та відгуки про ідею. Це важливіше за гроші.\n\n"
    "Щоб приєднатись — просто натисніть *Старт* і надішліть будь-яке фото з галереї 📸\n\n"
    "З повагою,\n"
    "Міша Сташків\n\n"
    "———\n\n"
    "Hello my dear users! This is Misha.\n\n"
    "I want to thank you for the motivation you give me. Even if you haven’t visited for a while or haven’t been active — I deeply appreciate your interest in the bot idea.\n\n"
    "Every single click means a lot to me ❤️\n\n"
    "I’ve just updated the bot: now signals will be sent automatically — you won’t have to do anything at all.\n\n"
    "I’ve considered your suggestions and will keep working, even if only one user remains here.\n\n"
    "I’d be truly grateful if you share this bot with your friends. It’s completely free — and it always will be.\n\n"
    "My goal is to gather feedback and thoughts about the idea. That’s worth more than money to me.\n\n"
    "To join — just press *Start* and send any random photo from your gallery 📸\n\n"
    "Sincerely,\n"
    "Misha Stashkiv"
)

