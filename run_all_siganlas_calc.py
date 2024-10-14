import os
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from developer_functions.general_dev.massage_send import send_message_to_all_users
from developer_functions.general_dev.signals_calc import process_assets_from_file


def signals_auto_update():

    # Визначаємо базову директорію проєкту (поточна робоча директорія)
    BASE_DIR = os.getcwd()  # Поточна робоча директорія на сервері

    # Формуємо шляхи до файлів відносно базової директорії
    file_path_crypto = os.path.join(BASE_DIR, 'developer_functions', 'crypto_dev', 'crypto_backtest_optimized.csv')
    output_file_crypto = os.path.join(BASE_DIR, 'developer_functions', 'crypto_dev', 'crypto_signal.csv')

    file_path_stock = os.path.join(BASE_DIR, 'developer_functions', 'stock_dev', 'stock_backtest_optimized.csv')
    output_file_stock = os.path.join(BASE_DIR, 'developer_functions', 'stock_dev', 'stock_signal.csv')
    #
    file_path_forex = os.path.join(BASE_DIR, 'developer_functions', 'forex_dev', 'forex_backtest_optimized.csv')
    output_file_forex = os.path.join(BASE_DIR, 'developer_functions', 'forex_dev', 'forex_signal.csv')

    process_assets_from_file(file_path_crypto, 'crypto', output_file=output_file_crypto)
    process_assets_from_file(file_path_stock, 'stock', output_file=output_file_stock)
    process_assets_from_file(file_path_forex, 'forex', output_file=output_file_forex)

    send_message_to_all_users("Signals have been updated. Check out new trading ideas!")


def schedule_signal_updates(hour: int = 23, minute: int = 30):
    # Використовуємо часову зону Eastern Time (US/Eastern)
    timezone = pytz.timezone('America/Chicago')

    # Створюємо планувальник
    scheduler = BackgroundScheduler(timezone=timezone)

    # Додаємо завдання для запуску функції signals_auto_update в конкретний час
    scheduler.add_job(signals_auto_update, 'cron', hour=hour, minute=minute)

    # Запускаємо планувальник
    scheduler.start()
    print(f"Планувальник запущено. Сигнали будуть оновлюватися щодня о {hour:02d}:{minute:02d}.")



