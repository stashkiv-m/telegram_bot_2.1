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



def determine_strategy(row=None):
    """Determines the strategy for a stock based on fundamental metrics and returns both the strategy code and description.
       If row is None, returns strategy abbreviations and descriptions only."""

    # Оновлений набір стратегій з додатковою стратегією для негативного ROE або ROA
    strategy_abbr = {
        "High Growth Undervalued": "HG_Und",
        "High Quality": "HQ",
        "Dividend Growth": "DivGr",
        "Dividend Leader": "DivLd",
        "Distressed": "Dist",
        "Stable Financial": "StblFin",
        "Value Play": "ValPl",
        "Aggressive Growth": "AggGr",
        "Balanced Opportunity": "BalOp",
        "Moderate Income": "ModInc",
        "Mixed Fundamentals": "MixFund",
        "Negative Returns": "NegRet",
        "Unknown": "Unk"
    }

    strategy_descriptions = {
        "HG_Und": "High Growth and Undervalued: High ROE, ROA, low Debt, high margins, and undervalued.",
        "HQ": "High Quality: High ROE, ROA, low Debt, and high margins.",
        "DivGr": "Dividend Growth: High ROE, ROA, low Debt, high margins, with dividends.",
        "DivLd": "Dividend Leader: High ROE, ROA, and strong dividend payout.",
        "Dist": "Distressed: High debt, negative earnings, and poor margins.",
        "StblFin": "Stable Financial: High liquidity ratios, positive margins, and strong financial stability.",
        "ValPl": "Value Play: Low PE and P/B ratio, indicating undervalued stocks.",
        "AggGr": "Aggressive Growth: High revenue and asset turnover ratios, focusing on growth.",
        "BalOp": "Balanced Opportunity: Mixed fundamentals but some growth potential.",
        "ModInc": "Moderate Income: Mixed income metrics with low to moderate risk.",
        "MixFund": "Mixed Fundamentals: Stable with low growth potential, but not at risk.",
        "NegRet": "Negative Returns: Stocks with negative ROE or ROA.",
        "Unk": "Unknown: No specific strategy classification available."
    }

    if row is None:
        return strategy_abbr, strategy_descriptions

    # Метрики для фільтрації стратегій
    roe = safe_float_conversion(row.get('ROE (%)'))
    roa = safe_float_conversion(row.get('ROA (%)'))
    debt_to_equity = safe_float_conversion(row.get('Debt to Equity'))
    gross_margin = safe_float_conversion(row.get('Gross Margin (%)'))
    operating_margin = safe_float_conversion(row.get('Operating Margin (%)'))
    net_margin = safe_float_conversion(row.get('Net Margin (%)'))
    current_ratio = safe_float_conversion(row.get('Current Ratio'))
    quick_ratio = safe_float_conversion(row.get('Quick Ratio'))
    pe_ratio = safe_float_conversion(row.get('PE Ratio'))
    pb_ratio = safe_float_conversion(row.get('P/B Ratio'))
    dividend_yield = clean_percentage(row.get('Dividend Yield (%)'))
    asset_turnover = safe_float_conversion(row.get('Asset Turnover'))

    # Визначення стратегій з додатковою умовою для негативного ROE або ROA
    if roe is not None and roe < 0 or roa is not None and roa < 0:
        strategy = "Negative Returns"
    elif roe is not None and roa is not None and debt_to_equity is not None and gross_margin is not None and \
            pe_ratio is not None and pb_ratio is not None and operating_margin is not None and net_margin is not None:
        if roe > 15 and roa > 10 and debt_to_equity < 1.5 and gross_margin > 15 and (pe_ratio < 10 or pb_ratio < 1) \
                and operating_margin > 0 and net_margin > 0:
            strategy = "High Growth Undervalued"
        elif roe > 15 and roa > 10 and debt_to_equity < 1 and gross_margin > 15 and operating_margin > 0 and net_margin > 0:
            strategy = "High Quality"
        elif roe > 12 and roa > 8 and debt_to_equity < 0.5 and gross_margin > 15 and dividend_yield is not None and \
                dividend_yield > 2 and operating_margin > 0 and net_margin > 0:
            strategy = "Dividend Growth"
        elif roe > 10 and dividend_yield is not None and dividend_yield > 3 and operating_margin > 0 and net_margin > 0:
            strategy = "Dividend Leader"
        elif debt_to_equity > 2 and (net_margin < 0 or operating_margin < 0):
            strategy = "Distressed"
        elif current_ratio is not None and quick_ratio is not None and asset_turnover is not None and \
                current_ratio > 2 and quick_ratio > 1.5 and operating_margin > 0 and net_margin > 0 and asset_turnover > 0.3:
            strategy = "Stable Financial"
        elif pe_ratio < 15 and pb_ratio < 1 and operating_margin > 0 and net_margin > 0:
            strategy = "Value Play"
        elif roe > 10 and roa > 8 and gross_margin > 15 and operating_margin > 0 and net_margin > 0:
            strategy = "Aggressive Growth"
        elif pe_ratio < 2 and gross_margin > 20 and current_ratio is not None and current_ratio > 1:
            strategy = "Balanced Opportunity"
        elif debt_to_equity > 0.5 and debt_to_equity < 1.5 and current_ratio is not None and \
                current_ratio > 1 and operating_margin > 0 and dividend_yield is not None and dividend_yield > 1:
            strategy = "Moderate Income"
        elif 0 < roe < 5 and 0 < roa < 5 and gross_margin > 15 and operating_margin > 0:
            strategy = "Mixed Fundamentals"
        else:
            strategy = "Unknown"
    else:
        strategy = "Unknown"

    # Повернення результатів
    strategy_short = strategy_abbr[strategy]
    strategy_description = strategy_descriptions[strategy_short]
    return strategy_short, strategy_description


# Перевірка функції для нових умов (без конкретних даних)

def create_user_table_by_strategy(df, title):
    """Generates a formatted table grouped by strategy for the given DataFrame."""
    table_str = f"\n=== {title} ===\n"
    if df.empty:
        return table_str + "No data available.\n"

    # Group by 'Strat' and sort each group by 'Profit%' in descending order
    grouped = df.groupby('Strat')
    for strategy, group in grouped:
        table_str += f"\n--- {strategy} ---\n"
        group = group.sort_values(by='Profit%', ascending=False)
        headers = " | ".join(df.columns)
        separator = "|".join(['-' * len(col) for col in df.columns])
        rows = "\n".join(" | ".join(str(val).ljust(6)[:6] for val in row) for row in group.values)
        table_str += f"| {headers} |\n|{separator}|\n{rows}\n"
    return table_str


def filter_and_classify_signals(df, state, forex_min_profit=5.0, other_min_profit=20.0):
    """Filters and classifies signals based on the state and profit thresholds."""
    macd_rows, ma_rows = [], []

    for _, row in df.iterrows():
        macd_signal = row.get('MACD Signal')
        ma_signal = row.get('MA Signal')
        take_profit_macd = safe_float_conversion(row.get('MACD Take Profit (%)'))
        stop_loss_macd = safe_float_conversion(row.get('MACD Stop Loss (%)'))
        profit_macd = safe_float_conversion(row.get('MACD Profit (%)'))
        take_profit_ma = safe_float_conversion(row.get('MA Take Profit (%)'))
        stop_loss_ma = safe_float_conversion(row.get('MA Stop Loss (%)'))
        profit_ma = safe_float_conversion(row.get('MA Profit (%)'))

        if macd_signal not in ['Buy', 'Sell'] and ma_signal not in ['Buy', 'Sell']:
            continue

        min_profit_threshold = forex_min_profit if state == 'forex_signal' else other_min_profit

        if (profit_macd is not None and profit_macd < min_profit_threshold) and \
                (profit_ma is not None and profit_ma < min_profit_threshold):
            continue

        strategy_short, _ = determine_strategy(row) if state == 'stock_signal' else ("Unk", "")

        if macd_signal in ['Buy', 'Sell'] and (profit_macd is not None and profit_macd >= min_profit_threshold):
            macd_row = {
                'Symb': row['Symbol'], 'MACD': macd_signal,
                'TProfit': f"{take_profit_macd:.2f}"[:6] if take_profit_macd is not None else '',
                'SLoss': f"{stop_loss_macd:.2f}"[:6] if stop_loss_macd is not None else '',
                'Profit%': f"{profit_macd:.2f}"[:6] if profit_macd is not None else '',
                'Strat': strategy_short if state == 'stock_signal' else ''
            }
            macd_rows.append(macd_row)

        if ma_signal in ['Buy', 'Sell'] and (profit_ma is not None and profit_ma >= min_profit_threshold):
            ma_row = {
                'Symb': row['Symbol'], 'MA': ma_signal,
                'TProfit': f"{take_profit_ma:.2f}"[:6] if take_profit_ma is not None else '',
                'SLoss': f"{stop_loss_ma:.2f}"[:6] if stop_loss_ma is not None else '',
                'Profit%': f"{profit_ma:.2f}"[:6] if profit_ma is not None else '',
                'Strat': strategy_short if state == 'stock_signal' else ''
            }
            ma_rows.append(ma_row)

    return pd.DataFrame(macd_rows), pd.DataFrame(ma_rows)


def signal_list_for_user(update: Update, context: CallbackContext):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    state = menu_state().rstrip('\n')

    if state == 'crypto_signals':
        file_path = os.path.join(BASE_DIR, '..', 'crypto_dev', 'crypto_signal.csv')
        output_file = os.path.join(BASE_DIR, '..', 'crypto_dev', 'crypto_signals.txt')
    elif state == 'stock_signal':
        file_path = os.path.join(BASE_DIR, '..', 'stock_dev', 'stock_signal_test.csv')
        output_file = os.path.join(BASE_DIR, '..', 'stock_dev', 'stock_signals.txt')
    elif state == 'forex_signal':
        file_path = os.path.join(BASE_DIR, '..', 'forex_dev', 'forex_signal.csv')
        output_file = os.path.join(BASE_DIR, '..', 'forex_dev', 'forex_signals.txt')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Невідомий тип активу.")
        return

    df = pd.read_csv(file_path)
    macd_df, ma_df = filter_and_classify_signals(df, state)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(create_user_table_by_strategy(macd_df, "MACD Signals"))
        file.write(create_user_table_by_strategy(ma_df, "MA Signals"))

        if state == 'stock_signal':
            _, strategy_descriptions = determine_strategy(None)
            file.write("\n\n=== Strategy Descriptions ===\n")
            for code, description in strategy_descriptions.items():
                file.write(f"{code}: {description}\n")

    with open(output_file, 'rb') as document:
        context.bot.send_document(chat_id=update.effective_chat.id, document=document)

    return macd_df, ma_df
