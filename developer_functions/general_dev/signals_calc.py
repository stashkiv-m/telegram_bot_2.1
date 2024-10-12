import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# Функція для отримання історичних даних за 205 днів
def fetch_ohlcv(symbol, asset_type, timeframe='1d'):
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')  # Сьогоднішня дата
        start_date = (datetime.now() - timedelta(days=205)).strftime('%Y-%m-%d')  # Останні 205 днів

        if asset_type == 'crypto':
            df = yf.download(f'{symbol}-USD', start=start_date, end=end_date, interval=timeframe)
        elif asset_type == 'forex':
            df = yf.download(f'{symbol}=X', start=start_date, end=end_date, interval=timeframe)
        else:  # Для акцій
            df = yf.download(symbol, start=start_date, end=end_date, interval=timeframe)

        if df.empty:
            raise ValueError(f"No data available for {symbol}")

        df.reset_index(inplace=True)
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


# Функція для розрахунку сигналів на купівлю/продаж на основі ковзних середніх
def calculate_signals(df, short_window, long_window):
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()

    # Explicitly setting the column dtype to 'object' to hold strings like 'Buy' or 'Sell'
    df['signal'] = np.nan
    df['signal'] = df['signal'].astype('object')  # Set dtype to object to store string values

    for i in range(1, len(df)):
        # Buy signal
        if df['short_ma'].iloc[i - 1] < df['long_ma'].iloc[i - 1] and df['short_ma'].iloc[i] > df['long_ma'].iloc[i]:
            df.loc[i, 'signal'] = 'Buy'
        # Sell signal
        elif df['short_ma'].iloc[i - 1] > df['long_ma'].iloc[i - 1] and df['short_ma'].iloc[i] < df['long_ma'].iloc[i]:
            df.loc[i, 'signal'] = 'Sell'

    last_5_days = datetime.now() - timedelta(days=5)
    signals_df = df.dropna(subset=['signal'])
    signals_df = signals_df[signals_df['timestamp'] >= last_5_days].copy()

    return signals_df


# Функція для обробки списку активів з файлу та збереження сигналів за останні 5 днів
def process_assets_from_file(file_path, asset_type, output_file=None):
    asset_df = pd.read_csv(file_path)
    all_signals = []

    for _, row in asset_df.iterrows():
        symbol = row['Symbol']
        short_window = int(row['Short MA Window'])
        long_window = int(row['Long MA Window'])

        # Завантаження даних
        df = fetch_ohlcv(symbol, asset_type)

        if df is None:
            continue

        # Обчислення сигналів
        signals_df = calculate_signals(df, short_window, long_window)

        if not signals_df.empty:
            # Додаємо додаткові колонки з початкового файлу до сигналів
            for col in ['Profit (%)', 'Take Profit (%)', 'Stop Loss (%)', 'Short MA Window', 'Long MA Window']:
                signals_df[col] = row[col]

            signals_df['Symbol'] = symbol
            all_signals.append(signals_df)

    # Об'єднуємо всі результати в один DataFrame та зберігаємо
    if all_signals:
        combined_signals = pd.concat(all_signals, ignore_index=True)
        combined_signals.to_csv(output_file, index=False)
        print(f"All signals combined and saved to {output_file}")
    else:
        print("No signals found for the last 5 days.")

    return combined_signals if all_signals else None


# Головна функція для запуску процесу
def main():
    # Визначаємо базову директорію проєкту (директорія, де знаходиться цей скрипт)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    asset_type = input("Введіть тип активу (crypto/stock/forex): ").strip().lower()

    if asset_type == 'crypto':
        file_path = os.path.join(BASE_DIR, '..', 'crypto_dev', 'crypto_backtest_optimized.csv')
        output_file = os.path.join(BASE_DIR, '..', 'crypto_dev', 'crypto_signal.csv')
    elif asset_type == 'stock':
        file_path = os.path.join(BASE_DIR, '..', 'stock_dev', 'stock_backtest_optimized.csv')
        output_file = os.path.join(BASE_DIR, '..', 'stock_dev', 'stock_signal.csv')
    elif asset_type == 'forex':
        file_path = os.path.join(BASE_DIR, '..', 'forex_dev', 'forex_backtest_optimized.csv')
        output_file = os.path.join(BASE_DIR, '..', 'forex_dev', 'forex_signal.csv')
    else:
        print("Невірний тип активу. Виберіть 'crypto', 'stock', або 'forex'.")
        return

    process_assets_from_file(file_path, asset_type, output_file=output_file)


if __name__ == "__main__":
    main()
