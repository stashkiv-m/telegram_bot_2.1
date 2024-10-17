import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Визначення універсального шляху до JSON-файлу з обліковими даними
base_dir = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(base_dir, '', 'general_data_base', 'telegram-bot-user-list-79452f202a61.json')

# Встановлення з'єднання з Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)

client = gspread.authorize(creds)

# Отримання доступу до таблиці за її ID
sheet = client.open_by_key('1nZv5QBo_excPo402Ul-a278hyB2-rQbYfqlCcHu-524')
worksheet = sheet.get_worksheet(0)  # Отримання першого аркуша таблиці

# Тестове зчитування даних з таблиці
print(worksheet.get_all_records())

def add_user_activity(user_id, username):
    # Додає або оновлює запис користувача в таблиці з часом виклику команди
    from datetime import datetime

    # Отримує поточний час у форматі дати та часу
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Додає новий рядок до таблиці
    worksheet.append_row([user_id, username, current_time])
    print(f"User {username} (ID: {user_id}) activity recorded at {current_time}.")
