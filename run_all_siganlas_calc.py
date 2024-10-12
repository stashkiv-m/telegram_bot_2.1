import os
import time
from developer_functions.general_dev.signals_calc import process_assets_from_file
import schedule


def signals_auto_update():

    # Визначаємо базову директорію проєкту (поточна робоча директорія)
    BASE_DIR = os.getcwd()  # Поточна робоча директорія на сервері

    # Формуємо шляхи до файлів відносно базової директорії
    file_path_crypto = os.path.join(BASE_DIR, 'developer_functions', 'crypto_dev', 'crypto_backtest_optimized.csv')
    output_file_crypto = os.path.join(BASE_DIR, 'developer_functions', 'crypto_dev', 'crypto_signal.csv')

    file_path_stock = os.path.join(BASE_DIR, 'developer_functions', 'stock_dev', 'stock_backtest_optimized.csv')
    output_file_stock = os.path.join(BASE_DIR, 'developer_functions', 'stock_dev', 'stock_signal.csv')

    file_path_forex = os.path.join(BASE_DIR, 'developer_functions', 'forex_dev', 'forex_backtest_optimized.csv')
    output_file_forex = os.path.join(BASE_DIR, 'developer_functions', 'forex_dev', 'forex_signal.csv')

    process_assets_from_file(file_path_crypto, 'crypto', output_file=output_file_crypto)
    process_assets_from_file(file_path_stock, 'stock', output_file=output_file_stock)
    process_assets_from_file(file_path_forex, 'forex', output_file=output_file_forex)


# Запускає функцію кожну 1 хвилину
schedule.every(1).minutes.do(signals_auto_update)

# Цикл для виконання запланованих завдань
while True:
    schedule.run_pending()
    time.sleep(1)
