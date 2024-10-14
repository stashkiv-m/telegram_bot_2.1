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


# Функція для розрахунку сигналів на основі ковзних середніх
def calculate_ma_signals(df, short_window, long_window):
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()

    df['MA Signal'] = np.nan
    df['MA Signal'] = df['MA Signal'].astype('object')  # Set dtype to object to store string values

    for i in range(1, len(df)):
        if df['short_ma'].iloc[i - 1] < df['long_ma'].iloc[i - 1] and df['short_ma'].iloc[i] > df['long_ma'].iloc[i]:
            df.loc[i, 'MA Signal'] = 'Buy'
        elif df['short_ma'].iloc[i - 1] > df['long_ma'].iloc[i - 1] and df['short_ma'].iloc[i] < df['long_ma'].iloc[i]:
            df.loc[i, 'MA Signal'] = 'Sell'

    return df


# Функція для розрахунку MACD сигналів
def calculate_macd_signals(df, short_period, long_period, signal_period):
    df['macd'] = df['close'].ewm(span=short_period, adjust=False).mean() - df['close'].ewm(span=long_period, adjust=False).mean()
    df['macd_signal_line'] = df['macd'].ewm(span=signal_period, adjust=False).mean()

    df['MACD Signal'] = np.nan
    df['MACD Signal'] = df['MACD Signal'].astype('object')  # Set dtype to object to store string values

    for i in range(1, len(df)):
        if df['macd'].iloc[i - 1] < df['macd_signal_line'].iloc[i - 1] and df['macd'].iloc[i] > df['macd_signal_line'].iloc[i]:
            df.loc[i, 'MACD Signal'] = 'Buy'
        elif df['macd'].iloc[i - 1] > df['macd_signal_line'].iloc[i - 1] and df['macd'].iloc[i] < df['macd_signal_line'].iloc[i]:
            df.loc[i, 'MACD Signal'] = 'Sell'

    return df


# Функція для об'єднання сигналів MA та MACD
def merge_signals(df):
    df['MA Signal'] = df['MA Signal'].fillna('Neutral')
    df['MACD Signal'] = df['MACD Signal'].fillna('Neutral')
    return df


# Функція для обробки списку активів з файлу та збереження сигналів
# Функція для обробки списку активів з файлу та збереження сигналів
def process_assets_from_file(file_path, asset_type, output_file=None):
    asset_df = pd.read_csv(file_path)
    all_signals = []

    for _, row in asset_df.iterrows():
        symbol = row['Symbol']
        short_ma_window = int(row['Short MA Window'])
        long_ma_window = int(row['Long MA Window'])
        macd_short_period = int(row['MACD Short Period'])
        macd_long_period = int(row['MACD Long Period'])
        macd_signal_period = int(row['MACD Signal Period'])

        df = fetch_ohlcv(symbol, asset_type)
        if df is None:
            continue

        # Обчислення сигналів MA
        df_with_ma = calculate_ma_signals(df, short_ma_window, long_ma_window)

        # Обчислення сигналів MACD
        df_with_macd = calculate_macd_signals(df_with_ma, macd_short_period, macd_long_period, macd_signal_period)

        # Об'єднання сигналів
        combined_signals_df = merge_signals(df_with_macd)

        # Збереження лише останнього сигналу
        last_signal = combined_signals_df.dropna(subset=['MA Signal', 'MACD Signal']).tail(1)

        if not last_signal.empty:
            # Додавання фундаментальних метрик лише для акцій
            if asset_type == 'stock':
                for col in ['MA Profit (%)', 'MA Take Profit (%)', 'MA Stop Loss (%)',
                            'MACD Profit (%)', 'MACD Take Profit (%)', 'MACD Stop Loss (%)',
                            'Market Cap', 'Enterprise Value', 'Trailing P/E', 'Forward P/E',
                            'P/B Ratio', 'ROE (%)', 'ROA (%)', 'Debt to Equity', 'Current Ratio',
                            'Dividend Yield (%)', 'Payout Ratio', 'Gross Margin', 'Operating Margin', 'Profit Margin']:
                    last_signal[col] = row[col]
            else:
                # Додавання тільки технічних метрик для форексу та криптовалют
                for col in ['MA Profit (%)', 'MA Take Profit (%)', 'MA Stop Loss (%)',
                            'MACD Profit (%)', 'MACD Take Profit (%)', 'MACD Stop Loss (%)']:
                    last_signal[col] = row[col]

            last_signal['Symbol'] = symbol
            all_signals.append(last_signal)

    if all_signals:
        combined_signals = pd.concat(all_signals, ignore_index=True)
        combined_signals.to_csv(output_file, index=False)
        print(f"Latest signals combined and saved to {output_file}")
    else:
        print("No signals found.")

    return combined_signals if all_signals else None



# Головна функція для запуску процесу
def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    asset_type = input("Введіть тип активу (crypto/stock/forex): ").strip().lower()

    if asset_type == 'crypto':
        file_path = os.path.join(BASE_DIR, '..', 'crypto_dev', 'crypto_backtest_optimized_test.csv')
        output_file = os.path.join(BASE_DIR, '..', 'crypto_dev', 'crypto_signal_test.csv')
    elif asset_type == 'stock':
        file_path = os.path.join(BASE_DIR, '..', 'stock_dev', 'stock_backtest_optimized_test.csv')
        output_file = os.path.join(BASE_DIR, '..', 'stock_dev', 'stock_signal_test.csv')
    elif asset_type == 'forex':
        file_path = os.path.join(BASE_DIR, '..', 'forex_dev', 'forex_backtest_optimized.csv')
        output_file = os.path.join(BASE_DIR, '..', 'forex_dev', 'forex_signal_test.csv')
    else:
        print("Невірний тип активу. Виберіть 'crypto', 'stock', або 'forex'.")
        return

    process_assets_from_file(file_path, asset_type, output_file=output_file)


# Виклик головної функції
if __name__ == "__main__":
    main()
