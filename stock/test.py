import yfinance as yf
import pandas as pd

def get_financial_statement(ticker_symbol, statement_type):
    # Отримуємо об'єкт Ticker для вибраного символу
    ticker = yf.Ticker(ticker_symbol)

    # Залежно від типу звіту, повертаємо відповідний DataFrame
    if statement_type == 'balance':
        return ticker.balance_sheet
    elif statement_type == 'income':
        return ticker.financials
    elif statement_type == 'cashflow':
        return ticker.cashflow
    else:
        raise ValueError("Invalid statement type. Choose 'balance', 'income', or 'cashflow'.")

def save_to_excel(dataframe, filename):
    # Зберігаємо DataFrame у файл Excel
    dataframe.to_excel(filename, index=True)
    print(f"Дані збережено у файл: {filename}")

# Приклад використання
ticker_symbol = input("Введіть символ акції (наприклад, AAPL): ").strip().upper()
statement_type = input("Введіть тип звіту ('balance', 'income', 'cashflow'): ").strip().lower()

try:
    statement = get_financial_statement(ticker_symbol, statement_type)
    filename = f"{ticker_symbol}_{statement_type}_statement.xlsx"
    save_to_excel(statement, filename)
except ValueError as e:
    print(e)
