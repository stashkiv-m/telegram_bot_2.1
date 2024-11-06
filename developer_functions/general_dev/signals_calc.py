import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def get_price_dependent_metrics(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    current_price = info.get('regularMarketPrice')

    metrics = {
        'Trailing P/E': info.get('trailingPE'),
        'Forward P/E': info.get('forwardPE'),
        'P/B Ratio': info.get('priceToBook'),
        'Dividend Yield (%)': info.get('dividendYield') * 100 if info.get('dividendYield') else None,
    }
    return metrics

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
    df['macd'] = df['close'].ewm(span=short_period, adjust=False).mean() - df['close'].ewm(span=long_period,
                                                                                           adjust=False).mean()
    df['macd_signal_line'] = df['macd'].ewm(span=signal_period, adjust=False).mean()

    df['MACD Signal'] = np.nan
    df['MACD Signal'] = df['MACD Signal'].astype('object')  # Set dtype to object to store string values

    for i in range(1, len(df)):
        if df['macd'].iloc[i - 1] < df['macd_signal_line'].iloc[i - 1] and df['macd'].iloc[i] > \
                df['macd_signal_line'].iloc[i]:
            df.loc[i, 'MACD Signal'] = 'Buy'
        elif df['macd'].iloc[i - 1] > df['macd_signal_line'].iloc[i - 1] and df['macd'].iloc[i] < \
                df['macd_signal_line'].iloc[i]:
            df.loc[i, 'MACD Signal'] = 'Sell'

    return df


# Функція для об'єднання сигналів MA та MACD
def merge_signals(df):
    df['MA Signal'] = df['MA Signal'].fillna('Neutral')
    df['MACD Signal'] = df['MACD Signal'].fillna('Neutral')
    return df


# Функція для отримання сектору, галузі та цін закриття за останні 5 торгових днів
# Функція для отримання сектору, галузі та цін закриття за останні 7 торгових днів
def add_sector_industry_and_last_7_closes(df, symbol):
    stock = yf.Ticker(symbol)
    info = stock.info

    # Додавання сектору та галузі
    df['Sector'] = info.get('sector', 'N/A')
    df['Industry'] = info.get('industry', 'N/A')

    # Отримання цін закриття за останні 7 торгових днів (без вихідних)
    hist_data = stock.history(period="1mo")  # Отримання даних за останній місяць
    last_7_trading_days = hist_data['Close'].tail(7)  # Останні 7 торгових днів

    for i in range(1, 8):
        column_name = f'close_day_{i}'
        if len(last_7_trading_days) >= i:
            df[column_name] = last_7_trading_days.iloc[-i]
        else:
            df[column_name] = 'N/A'

    return df


# Функція для обробки списку активів з файлу та збереження сигналів
def signal_calc_function_from_file(file_path, asset_type, output_file=None):
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
            # Додавання фундаментальних метрик тільки для акцій
            if asset_type == 'stock':
                price_dependent_metrics = get_price_dependent_metrics(symbol)
                for col, value in price_dependent_metrics.items():
                    last_signal[col] = value

                # Додавання сектору, галузі та цін закриття за останні 5 днів
                last_signal = add_sector_industry_and_last_7_closes(last_signal, symbol)

                for col in ['MA Profit (%)', 'MA Take Profit (%)', 'MA Stop Loss (%)',
                            'MACD Profit (%)', 'MACD Take Profit (%)', 'MACD Stop Loss (%)',
                            'Market Cap', 'PE Ratio', 'PS Ratio', 'P/B Ratio', 'ROE (%)', 'ROA (%)',
                            'Gross Margin (%)', 'Operating Margin (%)', 'EBIT Margin (%)',
                            'EBITDA Margin (%)', 'Net Margin (%)', 'Current Ratio', 'Quick Ratio',
                            'Debt to Assets', 'Debt to Equity', 'Long Term Debt to Assets', 'Book Value Per Share']:
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
        file_path = os.path.join(BASE_DIR, '..', 'crypto_dev', 'crypto_backtest_optimized.csv')
        output_file = os.path.join(BASE_DIR, '..', 'crypto_dev', 'crypto_signal.csv')
    elif asset_type == 'stock':
        file_path = os.path.join(BASE_DIR, '..', 'stock_dev', 'stock_backtest_optimized.csv')
        output_file = os.path.join(BASE_DIR, '..', 'stock_dev', 'stock_signal.csv')
    elif asset_type == 'forex':
        file_path = os.path.join(BASE_DIR, '..', 'forex_dev', 'forex_backtest_optimized.csv')
        output_file = os.path.join(BASE_DIR, '..', 'forex_dev', 'forex_signal_test.csv')
    else:
        print("Невірний тип активу. Виберіть 'crypto', 'stock', або 'forex'.")
        return

    signal_calc_function_from_file(file_path, asset_type, output_file=output_file)


# Виклик головної функції
if __name__ == "__main__":
    main()

