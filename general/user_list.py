import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

# Отримання доступу до таблиці за її ID
sheet = client.open_by_key('1nZv5QBo_excPo402Ul-a278hyB2-rQbYfqlCcHu-524')
worksheet = sheet.get_worksheet(0)  # Отримання першого аркуша таблиці

# Тестове зчитування даних з таблиці
print(worksheet.get_all_records())

def add_user_activity(user_id, username):
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.append_row([user_id, username, current_time])
    print(f"User {username} (ID: {user_id}) activity recorded at {current_time}.")
