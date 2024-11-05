import os
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from developer_functions.general_dev.massage_and_img_send import send_message_to_all_users, send_image_to_all_users
from developer_functions.general_dev.signals_calc import process_assets_from_file
from general.daily_information import send_img_with_text
from language_state import language_state


def all_signals_calc_run():

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

    if language == "Ukrainian":
        send_img_with_text("Нові сигнали вже доступні! Ознайомтеся з оновленим списком!")
    elif language == 'English':
        send_img_with_text("New signals are in! View the updated list of signals!")


def schedule_func_call(func, hour: int = 22, minute: int = 35):
    # Використовуємо часову зону Eastern Time (US/Eastern)
    timezone = pytz.timezone('America/Chicago')

    # Створюємо планувальник
    scheduler = BackgroundScheduler(timezone=timezone)
    # Додаємо завдання для запуску функції щодня у вказаний час
    scheduler.add_job(func, 'cron', hour=hour, minute=minute)
    # Додаємо завдання для запуску функції у конкретний час з понеділка по п'ятницю
    # scheduler.add_job(func, 'cron', hour=hour, minute=minute, day_of_week='mon-fri')

    # Запускаємо планувальник
    scheduler.start()
    print(f"Планувальник запущено. Оновлення о {hour:02d}:{minute:02d}, з понеділка по п'ятницю.")


all_signals_calc_run()