import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Замість JSON-файлу використовуємо словник з обліковими даними
google_cred = {
  "type": "service_account",
  "project_id": "telegram-bot-user-list",
  "private_key_id": "04ed64b2edff631617aac9f098eccd92338e090d",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCc4VDCIOTxzB5U\nlfDS0/5k/Q1fB5cyfleveXJsxheF0dItbWbWkBqSqmGMg1TQ04Lr19PiUpXHe1Ty\niHg7DUwKu5vqIDnjSTsumlFQJzVTrzv0NcZQRoPjIs10xBpCSP2+ZwIatpd1CvUc\neUJu87v3JkBInjgllSc0+SSe+BRbc5FC6kdQn0R26u29QtyKhTIg5gR2irqAnKER\nKeVAv3KdLdCLwoPMlNa9nbA72rtM49z2mWwpZKsTlfBpeT/T43qfBB7cRMaIUf6N\nxmjcQwk/CPq3Hw3WxxJpXr83WPiXuSrkKGkBSjNGyLAE4JWil0f6BPbX2VAxtT8r\nIerESJDnAgMBAAECggEAApvf0yMrkenU8fXT2QdPFzByZQL5b+qYXE6vZP0FR6fl\nWMHq3TpTds13oDoLsF96fih+SH4Jw1lbCzk5O/eAG/cvAexmvT572xJHgPX/j24K\n3CHhVd18vQ/Yb6QjOYVe0uQKlB4UseqoMvx8+/Ar18kk7VR+7CM2DQma1k0j+pe6\n/2dSjD/JGkTgzGsNR9T272oEw/kZ1kHIlLi9u7PKcV8xN8tDfwbYQAYXuYu8XWWI\nrjanXVoM6jApUEmXJgjm8NM/77MjP2RUQqHT68r6ILcu4QbqfgvAo8lKMf2Dyxe/\nzLB7Jt0ZMV3IvnN6OetF5ck5zgXvxdhIafZEHKgoYQKBgQDWXdFwRgnzPhV8HiVM\nHpqwCEvGb1Oyu8vTQJaJpzNC2C6BHPP4czCA0qsD52+xRGFAjs0LQPg1HZh/3cqT\nrovkMqru4s0UnaybfzgclpUAUhaOZQiBi9IJARdO5rHhDjR3BofW1Hc0c5n6GCxe\nQ8BCi1PnOoPA0eXFh45HAdH+YwKBgQC7WU8Aa4/dDDV/mTM2rGgSszf7+o/tLGHV\nHl/LTcYfpivdG1KwRLxCxBA8CvITWc5qatYHpeIgJ2iqwX6y/69dRI9gw/ElY9Lx\njQgnn9LaZTdrdP57l9mY1KCblC54q7NglHaUFTazhPAUE4zIjLbeWSmL8FPCmby3\nj7erl344rQKBgQCE3+yFinR6eR46LDl0QHgj61CE9NbNsEh8bsmhE6nbokLZN0gm\n1cfX4j2tEtUR7U/XA20nr6Lq0aiIgcMi3YvK7Hk10BHM2Jt4W1g9qD090KQ4qXmn\nSzLq7+kxuB/EX9i3eq3SxSoKsilcc4V0/Mv8s35Tktq+N50UXp0beI5g/wKBgHeO\n6+Kpwdpf8zglrVAjwBrG8mBEq1rA6wIVay6TyG7kHbPxvtgsVTQKaQ3YMln1AsxY\nt5OT4fWBEMN/zfovP1s26ITpJlglFzX9OYoH7Yhf9XkG5Ww8IKnubzw52Vo6wLNO\nq0mfLBRuLsOxIjPN0NmebuwWB231rEA8YAsKF4vVAoGADLZn52HGFCZOJeztLFik\nRt95mMU9t1y9QIOD1rZruf/BvHJ/9fIwms9pifUqJq9u166kWm2MruBEooeUOw1I\nbWSBDwLvwIzEANZjKrHmXJoGZGzuh8+b3wAyL3AaPNZGZaeA9DvVxE8gOKbtRIA1\np0nEj9BYw2B0SUrlVIEKyqg=\n-----END PRIVATE KEY-----\n",
  "client_email": "telegram-bot-user-list@telegram-bot-user-list.iam.gserviceaccount.com",
  "client_id": "105555608665692748291",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/telegram-bot-user-list%40telegram-bot-user-list.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Встановлення з'єднання з Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_cred, scope)

client = gspread.authorize(creds)

# Отримання доступу до таблиці за її ID
sheet = client.open_by_key('1nZv5QBo_excPo402Ul-a278hyB2-rQbYfqlCcHu-524')  # Заміни YOUR_SPREADSHEET_ID на ID таблиці
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
