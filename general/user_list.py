import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

from language_state import language_state

# Перевірка режиму запуску (сервер або локально)
if os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
    # Використовується на сервері
    credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    credentials_data = json.loads(credentials_json)
else:
    # Локальний запуск
    local_credentials_path = 'C:/Users/Mykhailo/PycharmProjects/telegram_bot_2.1/general/general_data_base/telegram-bot-user-list-79452f202a61.json'
    with open(local_credentials_path, 'r') as file:
        credentials_data = json.load(file)

# Налаштування Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_data, scope)
client = gspread.authorize(creds)

# Ідентифікатори таблиць
spreadsheet_id_access = '1y8q73J6wiwNhQLkWyzBBRTOwh0yy5TdGglIpNNOCgEo'  # замініть на ID таблиці з контролем доступу
spreadsheet_id_activity = '1nZv5QBo_excPo402Ul-a278hyB2-rQbYfqlCcHu-524'  # замініть на ID таблиці для запису активності

# Отримання аркушів з таблиць
access_sheet = client.open_by_key(spreadsheet_id_access)
access_worksheet = access_sheet.get_worksheet(0)  # Аркуш для контролю доступу

activity_sheet = client.open_by_key(spreadsheet_id_activity)
activity_worksheet = activity_sheet.get_worksheet(0)  # Аркуш для запису активності


# Функція для перевірки доступу користувача
def check_user_access(user_id):
    # Зчитування даних з таблиці доступу
    access_data = access_worksheet.get_all_records()

    # Перевірка, чи є користувач в таблиці доступу
    for row in access_data:
        if str(row['User ID']) == str(user_id) and row['Access Granted'] == 'TRUE':
            return True  # Доступ дозволено

    # Якщо користувача немає в таблиці, доступ заборонено
    return False


# Функція для запису активності користувача
def add_user_activity(user_id, username):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    activity_worksheet.append_row([user_id, username, current_time])
    print(f"User {username} (ID: {user_id}) activity recorded at {current_time}.")

# Функція для надсилання повідомлення з реквізитами для оплати
def send_payment_message(user_id):
    # Тут вставте ваш код для відправки повідомлення користувачу через Telegram API або інший сервіс
    print(f"User ID: {user_id} - Повідомлення з реквізитами для оплати надіслано.")


# Логіка обробки доступу користувача
def handle_user_access(user_id, username):
    if check_user_access(user_id):
        print("Доступ дозволено. Користувач може використовувати бота.")
        # Запис активності користувача
    else:
        print("Доступ заборонено. Надсилаємо повідомлення з реквізитами для оплати.")
        # Надсилання повідомлення з реквізитами для оплати
        send_payment_message(user_id)


def user_activity_and_access(update, context):
    # Отримуємо мову користувача
    language = language_state().rstrip('\n')
    # Отримуємо ID користувача та його ім'я
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    if language == 'Ukrainian':
        payment_details = (
            "Вибачте, але ваш доступ обмежено. Щоб отримати повний доступ до бота, будь ласка, оформіть підписку "
            "за 25 доларів на місяць за наступними реквізитами:\n\n"
            "Ваш внесок допоможе в розробці нових функцій. Після здійснення оплати, надішліть підтвердження"
            " для активації доступу.\n\n"
            "Реквізити для оплати:\n"
            "PayPal: business.stashkiv@gmail.com\n"
            "USDT (Network ETH ERC20) : \n\n"
    )
        eth = '0x281ce314d2f3762ccb591a987ad9a793bf0be2a7'
    else:
        payment_details = (
            "Sorry, but your access is restricted. To gain full access to the bot, please subscribe for $25 per "
            "month using the following payment details:\n\n"
            "Your contribution will support the development of new bot features. After completing the payment,"
            " please send a screenshot of the transaction for access activation.\n\n"
            "Payment details:\n"
            "PayPal: business.stashkiv@gmail.com\n"
            "USDT (Network ETH ERC20) : \n\n"
        )
        eth = '0x281ce314d2f3762ccb591a987ad9a793bf0be2a7'

    # Перевірка доступу
    if check_user_access(user_id):
        add_user_activity(user_id, username)
        return True
    else:
        context.bot.send_message(chat_id=user_id, text=payment_details)
        context.bot.send_message(chat_id=user_id, text=eth)
        return False


