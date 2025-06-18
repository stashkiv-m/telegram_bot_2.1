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

text_3 = [
    "🇺🇦 Привіт! Це Міша — я створив цього бота! 😊\n\n"
    "Дякую, що зацікавилися темою інвестицій і приділили увагу цьому проєкту.\n"
    "Ви — одні з перших користувачів, і бот для вас буде безкоштовним **назавжди**! ❤️",

    "🤖 Бот працює **автономно** — сигнали розраховуються автоматично за допомогою алгоритму, який я створив, надихаючись книгами 📚 Джека Швагера (*«Технічний аналіз»*) та Бенджаміна Грехема (*«Розумний інвестор»*).",

    "📈 Я поступово додаю нові функції. Планую інтегрувати **AI-аналіз**, додати підтримку **криптовалют** та **форексу**.",

    "📝 Також я працюю над функцією **Watchlist** — ви зможете зберігати акції, які вам сподобались, відстежувати їхню ціну та новини по кожній компанії.",

    "📲 Сповіщення про сигнали надходять щодня **о 15:00 за Центральним часом (🇺🇸)** — це **23:00 за Києвом (🇺🇦)**.",

    "🤝 Якщо вам подобається бот — **поділіться ним із друзями**. Це дуже допоможе проєкту!"
]

text_2 = (
    "Привіт!:\n"
    "📊 Ми щойно додали автоматичний аналіз фундаментальних показників компаній!\n"
    "Тепер бот не лише показує цифри, а й пояснює:\n"
    "- чи компанія прибуткова,\n"
    "- наскільки в неї високі маржі,\n"
    "- чи не має вона надмірного боргу,\n"
    "- чи акція виглядає недооціненою тощо.\n\n"
    "🤝 Поділіться ботом з друзями — нехай і вони отримають безкоштовний доступ до цих розумних підказок!\n\n"
    "📲 Приєднуйтесь до нашої групи: https://t.me/trade_navigator_channel\n"
    "Не тримайте інсайди лише для себе — це шанс для кожного! 💸"
)
text_2_en = (
    "🔥 If you've already joined — congratulations! You now have full free access to all bot features — forever ✅\n"
    "Even when the bot becomes paid — you won’t be affected 💼\n\n"
    "📊 We've just added automatic analysis of fundamental company metrics!\n"
    "The bot now not only shows numbers, but also explains:\n"
    "- whether the company is profitable,\n"
    "- how strong its margins are,\n"
    "- if it carries too much debt,\n"
    "- and whether the stock looks undervalued.\n\n"
    "🤝 Share the bot with your friends — let them also enjoy free lifetime access to these smart insights!\n\n"
    "📲 Join our group: https://t.me/trade_navigator_channel\n"
    "Don't keep the insights to yourself — give others a chance too! 💸"
)
