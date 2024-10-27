import os
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

# Сьогоднішня дата
today = datetime.date.today()
one_year_ago = today - datetime.timedelta(days=165)


def fetch_fundamental_data(symbol, report_type='Quarterly'):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        # Вибір даних на основі типу звіту
        balance_sheet = stock.quarterly_balance_sheet if report_type == 'Quarterly' else stock.balance_sheet
        financials = stock.quarterly_financials if report_type == 'Quarterly' else stock.financials
        cashflow = stock.quarterly_cashflow if report_type == 'Quarterly' else stock.cashflow

        # Збір основних даних з інформації про акцію
        market_cap = info.get('marketCap')
        shares_outstanding = info.get('sharesOutstanding')
        cash = balance_sheet.loc['Cash'].iloc[0] if 'Cash' in balance_sheet.index else 0
        net_income = financials.loc['Net Income'].iloc[0] if 'Net Income' in financials.index else None
        total_equity = balance_sheet.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in balance_sheet.index else None
        total_assets = balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in balance_sheet.index else None
        long_term_debt = balance_sheet.loc['Long Term Debt'].iloc[0] if 'Long Term Debt' in balance_sheet.index else 0
        current_debt = balance_sheet.loc['Current Debt'].iloc[0] if 'Current Debt' in balance_sheet.index else 0
        total_debt = long_term_debt + current_debt
        current_assets = balance_sheet.loc['Current Assets'].iloc[0] if 'Current Assets' in balance_sheet.index else None
        current_liabilities = balance_sheet.loc['Current Liabilities'].iloc[0] if 'Current Liabilities' in balance_sheet.index else None
        revenue = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials.index else None
        operating_income = financials.loc['Operating Income'].iloc[0] if 'Operating Income' in financials.index else None
        gross_profit = financials.loc['Gross Profit'].iloc[0] if 'Gross Profit' in financials.index else None
        ebitda = financials.loc['EBITDA'].iloc[0] if 'EBITDA' in financials.index else None
        cash_from_operations = cashflow.loc['Total Cash From Operating Activities'].iloc[0] if 'Total Cash From Operating Activities' in cashflow.index else None
        inventory = balance_sheet.loc['Inventory'].iloc[0] if 'Inventory' in balance_sheet.index else None

        # Розрахунок показників
        pe_ratio = market_cap / net_income if market_cap and net_income else None
        ps_ratio = market_cap / revenue if market_cap and revenue else None
        price_to_cash_flow = market_cap / cash_from_operations if market_cap and cash_from_operations else None
        pb_ratio = market_cap / total_equity if market_cap and total_equity else None
        roe = (net_income / total_equity) * 100 if net_income and total_equity else None
        roa = (net_income / total_assets) * 100 if net_income and total_assets else None
        gross_margin = (gross_profit / revenue) * 100 if gross_profit and revenue else None
        operating_margin = (operating_income / revenue) * 100 if operating_income and revenue else None
        ebit_margin = (operating_income / revenue) * 100 if operating_income and revenue else None
        ebitda_margin = (ebitda / revenue) * 100 if ebitda and revenue else None
        net_margin = (net_income / revenue) * 100 if net_income and revenue else None
        current_ratio = current_assets / current_liabilities if current_assets and current_liabilities else None
        quick_ratio = (current_assets - inventory) / current_liabilities if inventory and current_liabilities else None
        debt_to_assets = total_debt / total_assets if total_debt and total_assets else None
        debt_to_equity = total_debt / total_equity if total_debt and total_equity else None
        long_term_debt_to_assets = long_term_debt / total_assets if long_term_debt and total_assets else None
        book_value_per_share = total_equity / shares_outstanding if total_equity and shares_outstanding else None

        # Створення структури даних
        data = {
            'Market Cap': market_cap,
            'PE Ratio': pe_ratio,
            'PS Ratio': ps_ratio,
            'P/B Ratio': pb_ratio,
            'ROE (%)': roe,
            'ROA (%)': roa,
            'Gross Margin (%)': gross_margin,
            'Operating Margin (%)': operating_margin,
            'EBIT Margin (%)': ebit_margin,
            'EBITDA Margin (%)': ebitda_margin,
            'Net Margin (%)': net_margin,
            'Current Ratio': current_ratio,
            'Quick Ratio': quick_ratio,
            'Debt to Assets': debt_to_assets,
            'Debt to Equity': debt_to_equity,
            'Long Term Debt to Assets': long_term_debt_to_assets,
            'Book Value Per Share': book_value_per_share,
            'Report Type': report_type
        }

        return data
    except Exception as e:
        print(f"Error fetching fundamental data for {symbol}: {e}")
        return None


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
    df['signal_ma'] = 0
    df.loc[short_window:, 'signal_ma'] = np.where(df['short_ma'][short_window:] > df['long_ma'][short_window:], 1, 0)
    df['position_ma'] = df['signal_ma'].diff()

    return df


# Стратегія MACD
def macd_strategy(df, short_period=12, long_period=26, signal_period=9):
    df['macd_line'] = df['close'].ewm(span=short_period, adjust=False).mean() - df['close'].ewm(span=long_period, adjust=False).mean()
    df['signal_line'] = df['macd_line'].ewm(span=signal_period, adjust=False).mean()
    df['macd_histogram'] = df['macd_line'] - df['signal_line']

    # Створення сигналів
    df['signal_macd'] = 0
    df['signal_macd'] = np.where(df['macd_line'] > df['signal_line'], 1, 0)
    df['position_macd'] = df['signal_macd'].diff()

    return df, short_period, long_period, signal_period


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
            profit, profit_percentage, _ = backtest_strategy(temp_df, 'position_ma')

            if profit_percentage > best_profit:
                best_profit = profit_percentage
                best_short_window = short_window
                best_long_window = long_window
                best_df = temp_df

    return best_df, best_short_window, best_long_window, best_profit


# Функція для бектестування стратегії
# Функція для бектестування стратегії
def backtest_strategy(df, position_column):
    initial_balance = 10000
    balance = initial_balance
    position = 0  # 1 - довга позиція, 0 - без позиції

    for i in range(1, len(df)):
        # Перевірка, чи є ціна закриття ненульовою та не NaN
        if df['close'].iloc[i] == 0 or pd.isna(df['close'].iloc[i]):
            # Якщо є погане значення, інтерполюємо або використовуємо інший метод обробки
            continue  # або df['close'].iloc[i] = інтерпольоване значення, залежно від потреб

        if df[position_column].iloc[i] == 1:  # Купуємо
            position = balance / df['close'].iloc[i]  # Купуємо за весь баланс
            balance = 0
        elif df[position_column].iloc[i] == -1 and position > 0:  # Продаємо, якщо є відкрита позиція
            balance = position * df['close'].iloc[i]  # Продаємо і отримуємо новий баланс
            position = 0

    # Кінцевий баланс: закриваємо позицію за останньою ціною, якщо є відкрита позиція
    if position != 0 and not pd.isna(df['close'].iloc[-1]) and df['close'].iloc[-1] != 0:
        final_balance = balance + position * df['close'].iloc[-1]
    else:
        final_balance = balance

    profit = final_balance - initial_balance  # Прибуток або збиток
    profit_percentage = (profit / initial_balance) * 100  # Прибуток у відсотках
    return profit, profit_percentage, final_balance


# Функція для розрахунку Take Profit і Stop Loss
def calculate_take_profit_and_stop_loss(df, position_column):
    signals = df[df[position_column] != 0].reset_index()

    take_profits = []
    stop_losses = []

    for i in range(len(signals) - 1):
        signal = signals.iloc[i]
        next_signal = signals.iloc[i + 1]

        period_df = df.loc[signal['index']:next_signal['index']]

        take_profit = 0
        stop_loss = 0

        if signal[position_column] == 1:  # BUY
            if not period_df.empty:
                max_price = period_df['high'].max()
                take_profit = (max_price - signal['close']) / signal['close'] * 100
                min_price = period_df['low'].min()
                stop_loss = (min_price - signal['close']) / signal['close'] * 100

        elif signal[position_column] == -1:  # SELL
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

def optimize_macd(df):
    best_profit = -np.inf
    best_short_period = None
    best_long_period = None
    best_signal_period = None
    best_df = None

    # Перебираємо комбінації коротких, довгих і сигналів періодів
    for short_period in range(8, 14):  # Наприклад, оптимізуємо між 8-13 днями
        for long_period in range(22, 31):  # Оптимізуємо між 22-30 днями
            for signal_period in range(7, 12):  # Оптимізуємо між 7-11 днями
                temp_df, _, _, _ = macd_strategy(df.copy(), short_period, long_period, signal_period)
                profit_macd, profit_percentage_macd, _ = backtest_strategy(temp_df, 'position_macd')

                if profit_percentage_macd > best_profit:
                    best_profit = profit_percentage_macd
                    best_short_period = short_period
                    best_long_period = long_period
                    best_signal_period = signal_period
                    best_df = temp_df

    return best_df, best_short_period, best_long_period, best_signal_period, best_profit


# Оновлена основна функція для бектесту
# Оновлена основна функція для бектесту з фундаментальними показниками
def run_backtest_from_file(file_path, asset_type='stock'):
    asset_df = pd.read_csv(file_path)
    tickers = asset_df['Ticker'].tolist()

    all_results = []

    for ticker in tickers:
        print(f"\nFetching data for {ticker} ({asset_type})...")
        df = fetch_ohlcv(ticker, asset_type)

        if df is None or df.empty:
            print(f"Skipping {ticker} due to insufficient data.")
            continue

        # Оптимізація MA стратегії
        df, short_window, long_window, profit_percentage_ma = optimize_moving_average(df)

        # Оптимізація MACD стратегії
        df, short_period, long_period, signal_period, profit_percentage_macd = optimize_macd(df)

        # Розрахунок Take Profit і Stop Loss для MA
        avg_take_profit_ma, avg_stop_loss_ma = calculate_take_profit_and_stop_loss(df, 'position_ma')

        # Розрахунок Take Profit і Stop Loss для MACD
        avg_take_profit_macd, avg_stop_loss_macd = calculate_take_profit_and_stop_loss(df, 'position_macd')

        # Отримуємо фундаментальні дані для акції
        if asset_type == 'stock':
            fundamental_data = fetch_fundamental_data(ticker)
        else:
            fundamental_data = {}

        # Додаємо результати у форматі рядка для кожного активу
        result = {
            'Symbol': f"{ticker}",
            'Short MA Window': short_window,
            'Long MA Window': long_window,
            'MA Profit (%)': profit_percentage_ma,
            'MA Take Profit (%)': avg_take_profit_ma,
            'MA Stop Loss (%)': avg_stop_loss_ma,
            'MACD Short Period': short_period,
            'MACD Long Period': long_period,
            'MACD Signal Period': signal_period,
            'MACD Profit (%)': profit_percentage_macd,
            'MACD Take Profit (%)': avg_take_profit_macd,
            'MACD Stop Loss (%)': avg_stop_loss_macd
        }

        # Додаємо фундаментальні дані до результату, якщо вони доступні
        if fundamental_data:
            result.update(fundamental_data)

        all_results.append(result)

        print(
            f"Results for {ticker}: MA Profit (%) = {profit_percentage_ma:.2f}, MACD Profit (%) = {profit_percentage_macd:.2f}")

    # Визначаємо шлях збереження результатів
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    folder_path = os.path.join(project_root, 'developer_functions', f'{asset_type}_dev')
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

def run_all():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    file_path_crypto = os.path.join(base_dir, '..', 'crypto_dev', 'crypto_list.csv')
    file_path_stock = os.path.join(base_dir, '..', 'stock_dev', 'stock_list.csv')
    file_path_forex = os.path.join(base_dir, '..', 'forex_dev', 'forex_list.csv')

    # Вибір, який бектест запускати: криптовалюта, акції або форекс

    run_backtest_from_file(file_path_crypto, asset_type='crypto')

    run_backtest_from_file(file_path_stock, asset_type='stock')

    run_backtest_from_file(file_path_forex, asset_type='forex')


if __name__ == "__main__":
    # run_all()
    main()

