import pandas as pd
from datetime import datetime
import csv
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


def get_strategy(update: Update, context: CallbackContext):
    file_path = 'C:\\Users\\Mykhailo\\PycharmProjects\\telegram_bot_2.1\\developer_functions\\stock_dev\\stock_signal_test.csv'

    # Open CSV and read rows
    df = pd.read_csv(file_path)

    # Checking the state before adding fundamental metrics
    state = menu_state().rstrip('\n')

    # Define fundamental thresholds
    min_roe = 8
    min_roa = 4
    min_debt_to_equity = 1.5
    min_div_yield = 3.0

    macd_rows = []
    ma_rows = []

    # Strategy descriptions with shortened names
    strategy_abbr = {
        "High Growth": "HG",
        "Conservative": "Cons",
        "Dividend Accumulator": "DivAcc",
        "Unknown": "Unk"
    }

    strategy_descriptions = {
        "HG": "High Growth: High ROE and ROA with high Debt to Equity.",
        "Cons": "Conservative: Low ROE and ROA with low Debt to Equity.",
        "DivAcc": "Dividend Accumulator: High Dividend Yield, ROE, and ROA.",
        "Unk": "Unknown: No specific strategy classification available."
    }

    for _, row in df.iterrows():
        # Extracting signals and profit data
        macd_signal = row.get('MACD Signal')
        ma_signal = row.get('MA Signal')
        take_profit_macd = safe_float_conversion(row.get('MACD Take Profit (%)'))
        stop_loss_macd = safe_float_conversion(row.get('MACD Stop Loss (%)'))
        profit_macd = safe_float_conversion(row.get('MACD Profit (%)'))
        take_profit_ma = safe_float_conversion(row.get('MA Take Profit (%)'))
        stop_loss_ma = safe_float_conversion(row.get('MA Stop Loss (%)'))
        profit_ma = safe_float_conversion(row.get('MA Profit (%)'))

        # Filter: Only include rows with BUY or SELL signals
        if macd_signal not in ['BUY', 'SELL'] and ma_signal not in ['BUY', 'SELL']:
            continue

        strategy = "Unknown"

        # If in 'stock_signal' state, add fundamental metrics and classify
        if state == 'stock_signal':
            roe = safe_float_conversion(row.get('ROE (%)'))
            roa = safe_float_conversion(row.get('ROA (%)'))
            debt_to_equity = safe_float_conversion(row.get('Debt to Equity'))
            dividend_yield = clean_percentage(row.get('Dividend Yield (%)'))

            if roe is not None and roe > min_roe and roa is not None and roa > min_roa and debt_to_equity is not None and debt_to_equity > min_debt_to_equity:
                strategy = "High Growth"
            elif roe is not None and roe < min_roe and roa is not None and roa < min_roa and debt_to_equity is not None and debt_to_equity < min_debt_to_equity:
                strategy = "Conservative"
            elif dividend_yield is not None and dividend_yield > min_div_yield:
                strategy = "Dividend Accumulator"

        # Shortened strategy name
        strategy_short = strategy_abbr.get(strategy, "Unk")

        # Append rows for MACD and MA signals tables
        if macd_signal in ['BUY', 'SELL']:
            macd_rows.append({
                'Symb': row['Symbol'],
                'MACD': macd_signal,
                'TProfit': f"{take_profit_macd:.2f}" if take_profit_macd is not None else '',
                'SLoss': f"{stop_loss_macd:.2f}" if stop_loss_macd is not None else '',
                'Profit%': f"{profit_macd:.2f}" if profit_macd is not None else '',
                'Strat': strategy_short
            })

        if ma_signal in ['BUY', 'SELL']:
            ma_rows.append({
                'Symb': row['Symbol'],
                'MA': ma_signal,
                'TProfit': f"{take_profit_ma:.2f}" if take_profit_ma is not None else '',
                'SLoss': f"{stop_loss_ma:.2f}" if stop_loss_ma is not None else '',
                'Profit%': f"{profit_ma:.2f}" if profit_ma is not None else '',
                'Strat': strategy_short
            })

    # Convert lists to DataFrames
    macd_df = pd.DataFrame(macd_rows)
    ma_df = pd.DataFrame(ma_rows)

    # Save the combined DataFrame to a text file with two sections and strategy descriptions
    output_file = 'C:\\Users\\Mykhailo\\PycharmProjects\\telegram_bot_2.1\\developer_functions\\stock_dev\\combined_signals.txt'

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("=== MACD Signals ===\n")
        file.write(macd_df.to_string(index=False))
        file.write("\n\n=== MA Signals ===\n")
        file.write(ma_df.to_string(index=False))

        # Add strategy descriptions at the end of the file
        file.write("\n\n=== Strategy Descriptions ===\n")
        for strategy_code, description in strategy_descriptions.items():
            file.write(f"{strategy_code}: {description}\n")

    # Send the file to the user
    with open(output_file, 'rb') as document:
        context.bot.send_document(chat_id=update.effective_chat.id, document=document)

    return macd_df, ma_df


# Testing the function directly
if __name__ == '__main__':
    # Test run of the get_strategy function
    macd_df, ma_df = get_strategy()

    # Display the DataFrames in the console
    print("MACD Signals Table:")
    print(macd_df.head())  # Print the first few rows of the MACD signals table

    print("\nMA Signals Table:")
    print(ma_df.head())  # Print the first few rows of the MA signals table
