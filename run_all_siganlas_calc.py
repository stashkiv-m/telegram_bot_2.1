import os
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from developer_functions.general_dev.massage_and_img_send import send_message_to_all_users, send_image_to_all_users
from developer_functions.general_dev.signals_calc import process_assets_from_file
from language_state import language_state


def signals_auto_update():

    language = language_state().rstrip('\n')

    # Визначаємо базову директорію проєкту (поточна робоча директорія)
    BASE_DIR = os.getcwd()  # Поточна робоча директорія на сервері

    # Формуємо шляхи до файлів відносно базової директорії
    # file_path_crypto = os.path.join(BASE_DIR, 'developer_functions', 'crypto_dev', 'crypto_backtest_optimized.csv')
    # output_file_crypto = os.path.join(BASE_DIR, 'developer_functions', 'crypto_dev', 'crypto_signal.csv')
    #
    file_path_stock = os.path.join(BASE_DIR, 'developer_functions', 'stock_dev', 'stock_backtest_optimized.csv')
    output_file_stock = os.path.join(BASE_DIR, 'developer_functions', 'stock_dev', 'stock_signal.csv')
    #
    # file_path_forex = os.path.join(BASE_DIR, 'developer_functions', 'forex_dev', 'forex_backtest_optimized.csv')
    # output_file_forex = os.path.join(BASE_DIR, 'developer_functions', 'forex_dev', 'forex_signal.csv')

    # process_assets_from_file(file_path_crypto, 'crypto', output_file=output_file_crypto)
    process_assets_from_file(file_path_stock, 'stock', output_file=output_file_stock)
    # process_assets_from_file(file_path_forex, 'forex', output_file=output_file_forex)

    send_image_to_all_users()
    if language == "Ukrainian":
        send_message_to_all_users("Нові сигнали вже доступні! Ознайомтеся з оновленим списком!")
    elif language == 'English':
        send_message_to_all_users("New signals are in! View the updated list of signals!")


def schedule_signal_updates(hour: int = 22, minute: int = 5):
    # Використовуємо часову зону Eastern Time (US/Eastern)
    timezone = pytz.timezone('America/Chicago')

    # Створюємо планувальник
    scheduler = BackgroundScheduler(timezone=timezone)

    # Додаємо завдання для запуску функції signals_auto_update в конкретний час
    scheduler.add_job(signals_auto_update, 'cron', hour=hour, minute=minute)

    # Запускаємо планувальник
    scheduler.start()
    print(f"Планувальник запущено. Сигнали будуть оновлюватися щодня о {hour:02d}:{minute:02d}.")



