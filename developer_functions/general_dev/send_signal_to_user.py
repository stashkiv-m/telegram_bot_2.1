import os
import pandas as pd
from telegram import Update
from telegram.ext import CallbackContext
from state_update_menu import menu_state
from datetime import datetime, timedelta

def process_signals(update: Update, context: CallbackContext) -> None:
    # Отримання поточного стану з функції menu_state
    state = menu_state().rstrip('\n')  # Видаляємо символ нового рядка
    print(f"Поточний стан: {state}")

    # Визначаємо базову директорію проекту
    BASE_DIR = os.getcwd()  # Отримуємо поточну робочу директорію
    print(f"Поточна робоча директорія: {BASE_DIR}")

    # Визначаємо шлях до файлу в залежності від стану
    if state == 'stock_signal':
        file_path = os.path.join(BASE_DIR, 'developer_functions', 'stock_dev', 'stock_signal.csv')
    elif state == 'crypto_signals':
        file_path = os.path.join(BASE_DIR, 'developer_functions', 'crypto_dev', 'crypto_signal.csv')
    elif state == 'forex_signal':
        file_path = os.path.join(BASE_DIR, 'developer_functions', 'forex_dev', 'forex_signal.csv')
    else:
        update.message.reply_text("Невірний стан! Виберіть 'stock_signals' або 'crypto_signals'.")
        print("Невірний стан! Введіть 'stock_signals' або 'crypto_signals'.")
        return

    # Виводимо шлях до файлу для перевірки
    print(f"Шлях до файлу: {file_path}")

    # Перевірка наявності файлу
    if not os.path.exists(file_path):
        update.message.reply_text(f"Файл {file_path} не існує!")
        print(f"Файл {file_path} не існує!")
        return

    # Завантаження CSV файлу в DataFrame
    df = pd.read_csv(file_path)

    # Фільтрація і обробка даних
    if state == 'forex_signal':
        # Для форекс сигналів фільтруємо рядки з Return більше 1%
        df_filtered = df[df['Profit (%)'] > 1].copy()
    else:
        # Для інших сигналів залишаємо фільтр більше 20%
        df_filtered = df[df['Profit (%)'] > 20].copy()

    # Конвертуємо стовпець timestamp у формат дати
    df_filtered['timestamp'] = pd.to_datetime(df_filtered['timestamp'])

    # Фільтруємо сигнали за останні 2 дні
    two_days_ago = datetime.now() - timedelta(days=2)
    df_filtered = df_filtered[df_filtered['timestamp'] >= two_days_ago]

    # Подальша обробка
    df_filtered['Symbol'] = df_filtered['Symbol'].str.upper()
    df_filtered.loc[:, ['Take Profit (%)', 'Stop Loss (%)']] = df_filtered[['Take Profit (%)', 'Stop Loss (%)']].round(2)
    df_filtered['Signal Date'] = df_filtered['timestamp'].dt.strftime('%m/%d/%y')
    df_filtered.rename(columns={'Take Profit (%)': 'TP', 'Stop Loss (%)': 'SL'}, inplace=True)
    df_filtered.dropna(subset=['TP', 'SL'], inplace=True)
    df_filtered.drop_duplicates(inplace=True)

    # Збереження результатів у текстовий файл
    output_file_txt = os.path.join(os.path.dirname(file_path), f"{state}_signals.txt")
    df_filtered[['Symbol', 'TP', 'SL', 'signal', 'Signal Date']].to_csv(output_file_txt, index=False, sep='\t')

    print(f"Сигнали за останні 2 дні збережено в {output_file_txt}")

    # Надсилаємо файл користувачу
    with open(output_file_txt, 'rb') as file:
        context.bot.send_document(chat_id=update.effective_chat.id, document=file, filename=os.path.basename(output_file_txt))

    print(f"Файл {output_file_txt} надіслано користувачу.")
