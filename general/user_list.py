import csv
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


def log_user_data(user_id, username, first_name, last_name):
    # Шлях до файлу
    file_path = os.path.join(os.getcwd(), 'general', 'general_data_base', 'users_data.csv')

    # Перевіряємо, чи існує файл, і створюємо його з заголовками, якщо він не існує
    file_exists = os.path.isfile(file_path)

    # Отримуємо поточний час
    interaction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Відкриваємо файл для запису
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Якщо файл новий, додаємо заголовки
        if not file_exists:
            writer.writerow(['User ID', 'Username', 'First Name', 'Last Name', 'Interaction Time'])

        # Записуємо дані користувача
        writer.writerow([user_id, username, first_name, last_name, interaction_time])


def handle_user_interaction(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name

    # Логування даних користувача
    log_user_data(user_id, username, first_name, last_name)

    # Відповідь користувачу (опціонально)
    update.message.reply_text(f"Welcome! {first_name if last_name else ''} Glad to see you here! ")

