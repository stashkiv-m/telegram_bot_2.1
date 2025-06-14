import os

import pandas as pd
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from developer_functions.general_dev.massage_and_img_send import send_message_to_all_users, send_image_to_all_users
from developer_functions.general_dev.signals_calc import signal_calc_function_from_file
from general.daily_information import send_img_with_text
from language_state import language_state


import os
import pandas as pd

def all_signals_calc_run():
    BASE_DIR = os.getcwd()

    file_path_stock = os.path.join(BASE_DIR, 'developer_functions', 'stock_dev', 'stock_backtest_optimized.csv')
    output_file_stock = os.path.join(BASE_DIR, 'developer_functions', 'stock_dev', 'stock_signal.csv')

    # Генеруємо файл із сигналами
    signal_calc_function_from_file(file_path_stock, 'stock', output_file=output_file_stock)

    # Зчитуємо результат построково і одразу виводимо сигнали
    stock_data = pd.read_csv(output_file_stock)

    total_buy = 0
    total_sell = 0

    for _, row in stock_data.iterrows():
        ticker = row.get('Ticker', 'UNKNOWN')
        ma_signal = row.get('MA Signal', '')
        macd_signal = row.get('MACD Signal', '')

        if ma_signal in ['Buy', 'Sell']:
            print(f"[MA] {ticker}: {ma_signal}")
            total_buy += ma_signal == 'Buy'
            total_sell += ma_signal == 'Sell'

        if macd_signal in ['Buy', 'Sell']:
            print(f"[MACD] {ticker}: {macd_signal}")
            total_buy += macd_signal == 'Buy'
            total_sell += macd_signal == 'Sell'

    # Після всіх сигналів — загальне повідомлення
    summary_msg = f"New signals are in!\nBUY: {total_buy}\nSELL: {total_sell}"

    if total_buy > total_sell:
        send_img_with_text(summary_msg, 'bull.jpg', 'market_type', 50)
    else:
        send_img_with_text(summary_msg, 'bear.jpg', 'market_type', 50)



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