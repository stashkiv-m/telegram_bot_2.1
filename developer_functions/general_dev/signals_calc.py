import os
import time
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from developer_functions.general_dev.massage_and_img_send import send_chart_and_metrics_to_all_users
from developer_functions.general_dev.chart import generate_chart
from stock.get_stock_data import get_stock_metrics


def get_price_dependent_metrics(symbol):
    """
    Отримує фундаментальні метрики для символу.
    """
    stock = yf.Ticker(symbol)
    try:
        info = stock.info
        metrics = {
            'Trailing P/E': info.get('trailingPE'),
            'Forward P/E': info.get('forwardPE'),
            'P/B Ratio': info.get('priceToBook'),
            'Dividend Yield (%)': info.get('dividendYield') * 100 if info.get('dividendYield') else None,
            'Gross Margin (%)': info.get('grossMargins') * 100 if info.get('grossMargins') else None,
            'Operating Margin (%)': info.get('operatingMargins') * 100 if info.get('operatingMargins') else None,
            'Profit Margin (%)': info.get('profitMargins') * 100 if info.get('profitMargins') else None,
            'ROA (%)': info.get('returnOnAssets') * 100 if info.get('returnOnAssets') else None,
            'ROE (%)': info.get('returnOnEquity') * 100 if info.get('returnOnEquity') else None,
        }
        return metrics
    except Exception as e:
        print(f"Error fetching metrics for {symbol}: {e}")
        return {}


def fetch_ohlcv(symbol, asset_type, timeframe='1d'):
    """
    Завантажує історичні дані для символу, пропускаючи тікери з помилкою.
    """
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=205)).strftime('%Y-%m-%d')

        if asset_type == 'crypto':
            df = yf.download(f'{symbol}-USD', start=start_date, end=end_date, interval=timeframe, progress=False)
        elif asset_type == 'forex':
            df = yf.download(f'{symbol}=X', start=start_date, end=end_date, interval=timeframe, progress=False)
        else:
            df = yf.download(symbol, start=start_date, end=end_date, interval=timeframe, progress=False)

        if df.empty:
            print(f"No data available for {symbol}")
            return None

        df.reset_index(inplace=True)
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        return df

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def calculate_ma_signals(df, short_window, long_window):
    """
    Розраховує сигнали MA.
    """
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()
    df['MA Signal'] = np.where(
        (df['short_ma'] > df['long_ma']) & (df['short_ma'].shift(1) <= df['long_ma'].shift(1)), 'Buy',
        np.where(
            (df['short_ma'] < df['long_ma']) & (df['short_ma'].shift(1) >= df['long_ma'].shift(1)), 'Sell', 'Neutral'
        )
    )
    return df


def calculate_macd_signals(df, short_period, long_period, signal_period):
    """
    Розраховує сигнали MACD.
    """
    df['macd'] = df['close'].ewm(span=short_period, adjust=False).mean() - df['close'].ewm(span=long_period, adjust=False).mean()
    df['macd_signal_line'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
    df['MACD Signal'] = np.where(
        (df['macd'] > df['macd_signal_line']) & (df['macd'].shift(1) <= df['macd_signal_line'].shift(1)), 'Buy',
        np.where(
            (df['macd'] < df['macd_signal_line']) & (df['macd'].shift(1) >= df['macd_signal_line'].shift(1)), 'Sell',
            'Neutral'
        )
    )
    return df


def add_sector_industry_and_last_7_closes(df, symbol):
    """
    Додає сектор, галузь та ціни закриття за останні 7 торгових днів.
    """
    stock = yf.Ticker(symbol)
    try:
        info = stock.info
        df['Sector'] = info.get('sector', 'N/A')
        df['Industry'] = info.get('industry', 'N/A')

        hist_data = stock.history(period="1mo")
        last_7_trading_days = hist_data['Close'].tail(7).tolist()

        for i in range(1, 8):
            df[f'close_day_{i}'] = last_7_trading_days[-i] if len(last_7_trading_days) >= i else 'N/A'

    except Exception as e:
        print(f"Error adding sector/industry or closes for {symbol}: {e}")
    return df


def signal_calc_function_from_file(file_path, asset_type, output_file=None):
    """
    Обробляє файл активів, розраховує сигнали та зберігає результати.
    """

    def should_print_buy(metrics):
        return all([
            metrics.get('Gross Margin (%)', 0) and metrics['Gross Margin (%)'] > 0,
            metrics.get('Profit Margin (%)', 0) and metrics['Profit Margin (%)'] > 0,
            metrics.get('Operating Margin (%)', 0) and metrics['Operating Margin (%)'] > 0,
            metrics.get('ROA (%)', 0) and metrics['ROA (%)'] > 0,
            metrics.get('ROE (%)', 0) and metrics['ROE (%)'] > 0
        ])

    asset_df = pd.read_csv(file_path)
    all_signals = []

    for _, row in asset_df.iterrows():
        symbol = row['Symbol']

        # 🔎 Фільтр: надсилати сигнали лише якщо MACD Profit > 20%
        macd_profit = float(row.get('MACD Profit (%)', 0))
        if macd_profit <= 20:
            continue

        short_ma_window = int(row['Short MA Window'])
        long_ma_window = int(row['Long MA Window'])
        macd_short_period = int(row['MACD Short Period'])
        macd_long_period = int(row['MACD Long Period'])
        macd_signal_period = int(row['MACD Signal Period'])

        print(f"Processing {symbol}...")
        df = fetch_ohlcv(symbol, asset_type)
        if df is None:
            continue

        df = calculate_ma_signals(df, short_ma_window, long_ma_window)
        df = calculate_macd_signals(df, macd_short_period, macd_long_period, macd_signal_period)

        last_signal = df.tail(1).copy()

        if asset_type == 'stock':
            metrics = get_price_dependent_metrics(symbol)
            last_signal = add_sector_industry_and_last_7_closes(last_signal, symbol)
            for col, value in metrics.items():
                last_signal[col] = value

            if (last_signal['MA Signal'].iloc[0] == 'Buy' or last_signal['MACD Signal'].iloc[0] == 'Buy') and should_print_buy(metrics):
                print(f"📈 BUY SIGNAL for {symbol}")
                chart_path = generate_chart(symbol, ignore_state_check=True)
                signal_type = "📈 *BUY SIGNAL*\n\n"
                metrics_text = signal_type + get_stock_metrics(yf.Ticker(symbol), symbol)
                print(metrics_text)
                send_chart_and_metrics_to_all_users(chart_path, metrics_text)

            elif last_signal['MA Signal'].iloc[0] == 'Sell' or last_signal['MACD Signal'].iloc[0] == 'Sell':
                print(f"📉 SELL SIGNAL for {symbol}")
                chart_path = generate_chart(symbol, ignore_state_check=True)
                signal_type = "📉 *SELL SIGNAL*\n\n"
                metrics_text = signal_type + get_stock_metrics(yf.Ticker(symbol), symbol)
                print(metrics_text)
                send_chart_and_metrics_to_all_users(chart_path, metrics_text)

            for col in ['MA Profit (%)', 'MA Take Profit (%)', 'MA Stop Loss (%)',
                        'MACD Profit (%)', 'MACD Take Profit (%)', 'MACD Stop Loss (%)',
                        'Market Cap', 'PE Ratio', 'PS Ratio', 'P/B Ratio', 'ROE (%)', 'ROA (%)',
                        'Gross Margin (%)', 'Operating Margin (%)', 'EBIT Margin (%)',
                        'EBITDA Margin (%)', 'Net Margin (%)', 'Current Ratio', 'Quick Ratio',
                        'Debt to Assets', 'Debt to Equity', 'Long Term Debt to Assets',
                        'Book Value Per Share']:
                last_signal[col] = row.get(col, None)
        else:
            for col in ['MA Profit (%)', 'MA Take Profit (%)', 'MA Stop Loss (%)',
                        'MACD Profit (%)', 'MACD Take Profit (%)', 'MACD Stop Loss (%)']:
                last_signal[col] = row.get(col, None)

        last_signal['Symbol'] = symbol
        all_signals.append(last_signal)
        time.sleep(1)

    if all_signals:
        combined_signals = pd.concat(all_signals, ignore_index=True)
        combined_signals.to_csv(output_file, index=False)
        print(f"Signals saved to {output_file}")
    else:
        print("No signals found.")

    return all_signals


def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    asset_type = 'stock'  # або 'crypto' / 'forex' для інших активів

    file_map = {
        'crypto': ('crypto_backtest_optimized.csv', 'crypto_signal.csv'),
        'stock': ('stock_backtest_optimized.csv', 'stock_signal.csv'),
        'forex': ('forex_backtest_optimized.csv', 'forex_signal.csv'),
    }

    input_file, output_file = file_map[asset_type]
    file_path = os.path.join(BASE_DIR, '..', asset_type + '_dev', input_file)
    output_path = os.path.join(BASE_DIR, '..', asset_type + '_dev', output_file)

    signal_calc_function_from_file(file_path, asset_type, output_file=output_path)


if __name__ == "__main__":
    main()
