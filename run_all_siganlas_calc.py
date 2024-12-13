import os

import pandas as pd
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from developer_functions.general_dev.massage_and_img_send import send_message_to_all_users, send_image_to_all_users
from developer_functions.general_dev.signals_calc import signal_calc_function_from_file
from general.daily_information import send_img_with_text
from language_state import language_state


def all_signals_calc_run():
    # language = language_state().rstrip('\n')
    BASE_DIR = os.getcwd()  # Поточна робоча директорія на сервері

    # Шлях до файлів
    file_path_stock = os.path.join(BASE_DIR, 'developer_functions', 'stock_dev', 'stock_backtest_optimized.csv')
    output_file_stock = os.path.join(BASE_DIR, 'developer_functions', 'stock_dev', 'stock_signal.csv')

    # Виконання функції обробки сигналів
    signal_calc_function_from_file(file_path_stock, 'stock', output_file=output_file_stock)

    # Підрахунок значень "Buy" та "Sell" у колонках MA Signal та MACD Signal
    stock_data = pd.read_csv(output_file_stock)

    # Підрахунок кількості "Buy" і "Sell" в обох колонках
    buy_count_ma = stock_data['MA Signal'].value_counts().get('Buy', 0)
    sell_count_ma = stock_data['MA Signal'].value_counts().get('Sell', 0)
    buy_count_macd = stock_data['MACD Signal'].value_counts().get('Buy', 0)
    sell_count_macd = stock_data['MACD Signal'].value_counts().get('Sell', 0)

    # Загальна кількість "Buy" і "Sell"
    total_buy = buy_count_ma + buy_count_macd
    total_sell = sell_count_ma + sell_count_macd

    # Перевірка умови та результат
    if total_buy > total_sell:
        send_img_with_text(
            f"New signals are in! "
            f"BUY: {total_buy} "
            f"SELL: {total_sell} ",
            'bull.jpg', 'market_type',50
            )
    else:
        send_img_with_text(
            f"New signals are in! "
            f"BUY: {total_buy} "
            f"SELL: {total_sell} ",
            'bear.jpg', 'market_type',50
        )


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
