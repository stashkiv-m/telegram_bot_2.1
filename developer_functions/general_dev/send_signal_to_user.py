import os
import pandas as pd
from telegram import Update
from telegram.ext import CallbackContext
from state_update_menu import menu_state


def safe_float_conversion(value):
    try:
        return float(value) if value else None
    except ValueError:
        return None


def clean_percentage(value):
    if isinstance(value, float):
        return value
    if isinstance(value, str) and value.endswith('%'):
        return float(value.strip('%'))
    try:
        return float(value)
    except ValueError:
        return None


def signal_list_for_user(update: Update, context: CallbackContext):
    # Встановлюємо базову директорію
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Отримуємо стан меню
    state = menu_state().rstrip('\n')
    print(state)

    # Визначаємо вхідні та вихідні файли на основі стану меню
    if state == 'crypto_signals':
        file_path = os.path.join(BASE_DIR, '..', 'crypto_dev', 'crypto_signal_test.csv')
        output_file = os.path.join(BASE_DIR, '..', 'crypto_dev', 'crypto_siganls.txt')
    elif state == 'stock_signal':
        file_path = os.path.join(BASE_DIR, '..', 'stock_dev', 'stock_signal_test.csv')
        output_file = os.path.join(BASE_DIR, '..', 'stock_dev', 'stock_signals.txt')
    elif state == 'forex_signal':
        file_path = os.path.join(BASE_DIR, '..', 'forex_dev', 'forex_signal_test.csv')
        output_file = os.path.join(BASE_DIR, '..', 'forex_dev', 'forex_signals.txt')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Невідомий тип активу.")
        return

    # Відкриваємо CSV файл для читання
    df = pd.read_csv(file_path)

    # Визначаємо пороги для фундаментальних метрик
    min_roe = 8
    min_roa = 4
    min_debt_to_equity = 1.5
    min_div_yield = 3.0

    macd_rows = []
    ma_rows = []

    # Скорочені назви стратегій
    strategy_abbr = {
        "High Growth": "HG",
        "Conservative": "Cons",
        "Dividend Accumulator": "DivAcc",
        "Stable Growth": "StblGr",
        "Dividend Growth": "DivGr",
        "Profitability Leader": "PrftLd",
        "Unknown": "Unk"
    }

    # Опис стратегій
    strategy_descriptions = {
        "HG": "High Growth: High ROE and ROA with high Debt to Equity.",
        "Cons": "Conservative: Low ROE and ROA with low Debt to Equity.",
        "DivAcc": "Dividend Accumulator: High Dividend Yield, ROE, and ROA.",
        "StblGr": "Stable Growth: Moderate ROE and ROA with manageable Debt to Equity.",
        "DivGr": "Dividend Growth: High Dividend Yield and consistent dividend growth.",
        "PrftLd": "Profitability Leader: Very high Gross and Operating Margins.",
        "Unk": "Unknown: No specific strategy classification available."
    }

    for _, row in df.iterrows():
        # Отримуємо сигнали та дані про прибуток
        macd_signal = row.get('MACD Signal')
        ma_signal = row.get('MA Signal')
        take_profit_macd = safe_float_conversion(row.get('MACD Take Profit (%)'))
        stop_loss_macd = safe_float_conversion(row.get('MACD Stop Loss (%)'))
        profit_macd = safe_float_conversion(row.get('MACD Profit (%)'))
        take_profit_ma = safe_float_conversion(row.get('MA Take Profit (%)'))
        stop_loss_ma = safe_float_conversion(row.get('MA Stop Loss (%)'))
        profit_ma = safe_float_conversion(row.get('MA Profit (%)'))

        # Фільтруємо лише рядки з сигналами BUY або SELL
        if macd_signal not in ['Buy', 'Sell'] and ma_signal not in ['Buy', 'Sell']:
            continue

        strategy = "Unknown"

        # Якщо актив — це акція, додаємо фундаментальні метрики та класифікуємо стратегію
        if state == 'stock_signal':
            roe = safe_float_conversion(row.get('ROE (%)'))
            roa = safe_float_conversion(row.get('ROA (%)'))
            debt_to_equity = safe_float_conversion(row.get('Debt to Equity'))
            dividend_yield = clean_percentage(row.get('Dividend Yield (%)'))
            gross_margin = safe_float_conversion(row.get('Gross Margin (%)'))
            operating_margin = safe_float_conversion(row.get('Operating Margin (%)'))

            # High Growth
            if roe is not None and roe > min_roe and roa is not None and roa > min_roa and debt_to_equity is not None and debt_to_equity > min_debt_to_equity:
                strategy = "High Growth"
            # Conservative
            elif roe is not None and roe < min_roe and roa is not None and roa < min_roa and debt_to_equity is not None and debt_to_equity < min_debt_to_equity:
                strategy = "Conservative"
            # Dividend Accumulator
            elif dividend_yield is not None and dividend_yield > min_div_yield:
                strategy = "Dividend Accumulator"
            # Stable Growth
            elif roe is not None and 5 <= roe <= 8 and roa is not None and 3 <= roa <= 5 and debt_to_equity is not None and debt_to_equity <= 1.5:
                strategy = "Stable Growth"
            # Dividend Growth
            elif dividend_yield is not None and dividend_yield > min_div_yield and row.get('Dividend Growth', '') == 'Yes':
                strategy = "Dividend Growth"
            # Profitability Leader
            elif gross_margin is not None and gross_margin > 50 and operating_margin is not None and operating_margin > 20:
                strategy = "Profitability Leader"

        # Скорочена назва стратегії
        strategy_short = strategy_abbr.get(strategy, "Unk")

        # Додаємо рядки для MACD та MA
        if macd_signal in ['Buy', 'Sell']:
            macd_row = {
                'Symb': row['Symbol'],
                'MACD': macd_signal,
                'TProfit': f"{take_profit_macd:.2f}"[:6] if take_profit_macd is not None else '',
                'SLoss': f"{stop_loss_macd:.2f}"[:6] if stop_loss_macd is not None else '',
                'Profit%': f"{profit_macd:.2f}"[:6] if profit_macd is not None else ''
            }
            if state == 'stock_signal':  # Додаємо колонку "Strat" тільки для акцій
                macd_row['Strat'] = strategy_short
            macd_rows.append(macd_row)

        if ma_signal in ['Buy', 'Sell']:
            ma_row = {
                'Symb': row['Symbol'],
                'MA': ma_signal,
                'TProfit': f"{take_profit_ma:.2f}"[:6] if take_profit_ma is not None else '',
                'SLoss': f"{stop_loss_ma:.2f}"[:6] if stop_loss_ma is not None else '',
                'Profit%': f"{profit_ma:.2f}"[:6] if profit_ma is not None else ''
            }
            if state == 'stock_signal':  # Додаємо колонку "Strat" тільки для акцій
                ma_row['Strat'] = strategy_short
            ma_rows.append(ma_row)

    # Конвертуємо списки у DataFrame
    macd_df = pd.DataFrame(macd_rows)
    ma_df = pd.DataFrame(ma_rows)

    # Форматований вивід для текстового файлу
    def format_table(df, title):
        table_str = f"\n=== {title} ===\n"
        if df.empty:
            return table_str + "No data available.\n"
        headers = " | ".join(df.columns)
        separator = "|".join(['-' * len(col) for col in df.columns])
        rows = "\n".join(" | ".join(str(val).ljust(6)[:6] for val in row) for row in df.values)
        table_str += f"| {headers} |\n|{separator}|\n{rows}\n"
        return table_str

    # Зберігаємо об'єднаний DataFrame у текстовий файл з описами стратегій (тільки для акцій)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(format_table(macd_df, "MACD Signals"))
        file.write(format_table(ma_df, "MA Signals"))

        # Додаємо описи стратегій тільки для акцій
        if state == 'stock_signal':
            file.write("\n\n=== Strategy Descriptions ===\n")
            for strategy_code, description in strategy_descriptions.items():
                file.write(f"{strategy_code}: {description}\n")

    # Відправляємо файл користувачу
    with open(output_file, 'rb') as document:
        context.bot.send_document(chat_id=update.effective_chat.id, document=document)

    return macd_df, ma_df
