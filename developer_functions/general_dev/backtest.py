import os
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

# Сьогоднішня дата
today = datetime.date.today()
one_year_ago = today - datetime.timedelta(days=365)


# Функція для отримання історичних даних через yfinance
def fetch_ohlcv(symbol, asset_type):
    try:
        # Якщо актив — це криптовалюта, додаємо суфікс -USD
        if asset_type == 'crypto':
            df = yf.download(f'{symbol}-USD', start=one_year_ago, interval='1d')
        # Якщо актив — це форекс, додаємо суфікс USD=X
        elif asset_type == 'forex':
            df = yf.download(f'{symbol}=X', start=one_year_ago, interval='1d')
        else:
            df = yf.download(symbol, start=one_year_ago, interval='1d')

        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        df.reset_index(inplace=True)
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


# Стратегія перетину ковзних середніх
def moving_average_crossover_strategy(df, short_window, long_window):
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()

    # Створення сигналів
    df['signal'] = 0
    df.loc[short_window:, 'signal'] = np.where(df['short_ma'][short_window:] > df['long_ma'][short_window:], 1, 0)
    df['position'] = df['signal'].diff()

    return df


# Функція для бектесту стратегії з підбором найкращих параметрів ковзних середніх
def optimize_moving_average(df):
    best_profit = -np.inf
    best_short_window = None
    best_long_window = None
    best_df = None

    # Перебираємо комбінації коротких і довгих вікон
    for short_window in range(10, 101, 10):
        for long_window in range(short_window + 10, 201, 10):
            temp_df = moving_average_crossover_strategy(df.copy(), short_window, long_window)
            profit, profit_percentage, _ = backtest_strategy(temp_df)

            if profit_percentage > best_profit:
                best_profit = profit_percentage
                best_short_window = short_window
                best_long_window = long_window
                best_df = temp_df

    return best_df, best_short_window, best_long_window, best_profit


# Функція для бектестування стратегії
def backtest_strategy(df):
    initial_balance = 10000
    balance = initial_balance
    position = 0  # 1 - довга позиція, 0 - без позиції

    for i in range(1, len(df)):
        if df['position'].iloc[i] == 1:  # Купуємо
            position = balance / df['close'].iloc[i]  # Купуємо за весь баланс
            balance = 0
        elif df['position'].iloc[i] == -1:  # Продаємо
            balance = position * df['close'].iloc[i]  # Продаємо і отримуємо новий баланс
            position = 0

    # Кінцевий баланс: закриваємо позицію за останньою ціною, якщо є відкрита позиція
    if position != 0:
        final_balance = balance + position * df['close'].iloc[-1]
    else:
        final_balance = balance

    profit = final_balance - initial_balance  # Прибуток або збиток
    profit_percentage = (profit / initial_balance) * 100  # Прибуток у відсотках
    return profit, profit_percentage, final_balance


# Функція для розрахунку Take Profit і Stop Loss
def calculate_take_profit_and_stop_loss(df):
    signals = df[df['position'] != 0].reset_index()

    take_profits = []
    stop_losses = []

    for i in range(len(signals) - 1):
        signal = signals.iloc[i]
        next_signal = signals.iloc[i + 1]

        period_df = df.loc[signal['index']:next_signal['index']]

        take_profit = 0
        stop_loss = 0

        if signal['position'] == 1:  # BUY
            if not period_df.empty:
                max_price = period_df['high'].max()
                take_profit = (max_price - signal['close']) / signal['close'] * 100
                min_price = period_df['low'].min()
                stop_loss = (min_price - signal['close']) / signal['close'] * 100

        elif signal['position'] == -1:  # SELL
            if not period_df.empty:
                min_price = period_df['low'].min()
                take_profit = (signal['close'] - min_price) / signal['close'] * 100
                max_price = period_df['high'].max()
                stop_loss = (signal['close'] - max_price) / signal['close'] * 100

        take_profits.append(take_profit)
        stop_losses.append(stop_loss)

    avg_take_profit = np.mean(take_profits) if take_profits else 0
    avg_stop_loss = np.mean(stop_losses) if stop_losses else 0

    return avg_take_profit, avg_stop_loss


# Основна функція для бектесту
def run_backtest_from_file(file_path, asset_type='crypto'):
    asset_df = pd.read_csv(file_path)
    tickers = asset_df['Ticker'].tolist()

    all_results = []

    for ticker in tickers:
        print(f"\nFetching data for {ticker} ({asset_type})...")
        df = fetch_ohlcv(ticker, asset_type)

        if df is None or df.empty:
            print(f"Skipping {ticker} due to insufficient data.")
            continue

        # Оптимізація стратегії
        df, short_window, long_window, profit_percentage = optimize_moving_average(df)

        # Розрахунок Take Profit і Stop Loss
        avg_take_profit, avg_stop_loss = calculate_take_profit_and_stop_loss(df)

        # Додаємо результати у форматі рядка для кожного активу
        result = {
            'Symbol': f"{ticker}",
            'Short MA Window': short_window,
            'Long MA Window': long_window,
            'Profit (%)': profit_percentage,
            'Take Profit (%)': avg_take_profit,
            'Stop Loss (%)': avg_stop_loss
        }
        all_results.append(result)

        print(
            f"Results for {ticker}: Profit (%) = {profit_percentage:.2f}, Short MA = {short_window}, Long MA = {long_window}, Take Profit = {avg_take_profit:.2f}%, Stop Loss = {avg_stop_loss:.2f}%")

    # Визначаємо, в яку папку зберігати результати
    folder_path = os.path.join(os.getcwd(), 'developer_functions', f'{asset_type}_dev')
    file_name = f'{asset_type}_backtest_optimized.csv'

    # Перевірка наявності папки
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Шлях для збереження результатів
    file_path = os.path.join(folder_path, file_name)
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(file_path, index=False)
    print(f"\nResults saved to {file_path}")


# Головна функція для запуску бектесту
def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    file_path_crypto = os.path.join(base_dir, '..', 'crypto_dev', 'crypto_list.csv')
    file_path_stock = os.path.join(base_dir, '..', 'stock_dev', 'stock_list.csv')
    file_path_forex = os.path.join(base_dir, '..', 'forex_dev', 'forex_list.csv')

    # Вибір, який бектест запускати: криптовалюта, акції або форекс
    asset_type = input("Введіть тип активу (crypto/stock/forex): ").strip().lower()

    if asset_type == 'crypto':
        run_backtest_from_file(file_path_crypto, asset_type='crypto')
    elif asset_type == 'stock':
        run_backtest_from_file(file_path_stock, asset_type='stock')
    elif asset_type == 'forex':
        run_backtest_from_file(file_path_forex, asset_type='forex')
    else:
        print("Невірний тип активу. Виберіть 'crypto', 'stock' або 'forex'.")



if __name__ == "__main__":
    main()
