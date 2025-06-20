import os
import pandas as pd
from telegram import Update
from telegram.ext import CallbackContext

from language_state import language_state
from state_update_menu import menu_state


def abbreviate_industry(industry_name, max_word_length=3, abbrev_dict=None):
    words = industry_name.split()
    abbreviated = ''.join([word[:max_word_length].capitalize() for word in words])
    if abbrev_dict is not None:
        abbrev_dict[abbreviated] = industry_name
    return abbreviated


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
    language = language_state().rstrip('\n')

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

    if language == 'Ukrainian':
        strategy_descriptions = {
            "HG_Und": "Високий ріст і недооціненість: високий ROE, ROA, низький борг, високі маржі та недооціненість.",
            "HQ": "Висока якість: високий ROE, ROA, низький борг і високі маржі.",
            "DivGr": "Зростання дивідендів: високий ROE, ROA, низький борг, високі маржі та дивіденди.",
            "DivLd": "Лідер дивідендів: високий ROE, ROA та сильна виплата дивідендів.",
            "Dist": "Складне становище: високий борг, негативні прибутки та низькі маржі.",
            "StblFin": "Стабільність фінансів: високі коефіцієнти ліквідності, позитивні маржі та фінансова стабільність.",
            "ValPl": "Цінова гра: низький PE та P/B коефіцієнти, що вказують на недооціненість.",
            "AggGr": "Агресивне зростання: високі доходи та оборот активів, зосередження на зростанні.",
            "BalOp": "Збалансована можливість: змішані фінансові показники, але є потенціал зростання.",
            "ModInc": "Помірний дохід: змішані доходи з низьким або помірним ризиком.",
            "MixFund": "Змішані фінанси: стабільність з низьким потенціалом зростання, але без ризиків.",
            "NegRet": "Негативна дохідність: акції з негативним ROE або ROA.",
            "Unk": "Невідомо: конкретна стратегія не визначена."
        }
    else:
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

    strategy_short = strategy_abbr[strategy]
    strategy_description = strategy_descriptions[strategy_short]
    return strategy_short, strategy_description


def create_user_table_by_strategy(df, title, abbrev_dict):
    """Generates a formatted table grouped by strategy for the given DataFrame."""
    table_str = f"\n=== {title} ===\n"
    if df.empty:
        return table_str + "No data available.\n"

    grouped = df.groupby('Strat')
    for strategy, group in grouped:
        table_str += f"\n--- {strategy} ---\n"
        group = group.sort_values(by='Profit%', ascending=False)
        group = group.drop(columns=['Strat'])

        headers = " | ".join(group.columns)
        separator = "|".join(['-' * len(col) for col in group.columns])
        rows = "\n".join(" | ".join(str(val).ljust(6)[:6] for val in row) for row in group.values)
        table_str += f"| {headers} |\n|{separator}|\n{rows}\n"

    return table_str


def add_industry_abbreviations(abbrev_dict):
    abbrev_table = "\n\n=== Industry Abbreviations ===\n"
    abbrev_table += "| Abbreviation | Full Industry Name |\n"
    abbrev_table += "|--------------|---------------------|\n"
    for abbrev, full_name in sorted(abbrev_dict.items()):  # Додаємо сортування за алфавітом
        abbrev_table += f"| {abbrev:<12} | {full_name} |\n"
    return abbrev_table


def add_strategy_descriptions(strategy_descriptions):
    strategy_table = "\n\n=== Strategy Descriptions ===\n"
    for code, description in strategy_descriptions.items():
        strategy_table += f"{code}: {description}\n"
    return strategy_table


def filter_and_classify_signals(df, state, forex_min_profit=5.0, other_min_profit=15.0):
    macd_rows, ma_rows = [], []
    abbrev_dict = {}

    for _, row in df.iterrows():
        # Виводимо поточний рядок для перевірки

        macd_signal = row.get('MACD Signal')
        ma_signal = row.get('MA Signal')

        # Виводимо сигнали

        # Перевірка мінімального порогу прибутковості
        min_profit_threshold = forex_min_profit if state == 'forex_signal' else other_min_profit
        profit_macd = safe_float_conversion(row.get('MACD Profit (%)'))
        profit_ma = safe_float_conversion(row.get('MA Profit (%)'))

        # Пропускаємо рядки, які не відповідають критеріям сигналів і прибутковості
        if macd_signal not in ['Buy', 'Sell'] and ma_signal not in ['Buy', 'Sell']:

            continue
        if (profit_macd is not None and profit_macd < min_profit_threshold) and \
                (profit_ma is not None and profit_ma < min_profit_threshold):

            continue

        industry = row.get('Industry')
        # Скорочуємо назву галузі
        if pd.notna(industry):
            industry = abbreviate_industry(industry, abbrev_dict=abbrev_dict)

        # Визначаємо стратегію для акцій
        strategy_short, _ = determine_strategy(row) if state == 'stock_signal' else ("Unk", "")

        if macd_signal in ['Buy', 'Sell'] and (profit_macd is not None and profit_macd >= min_profit_threshold):
            macd_row = {
                'Symb': row['Symbol'], 'MACD': macd_signal,
                'TProfit': f"{profit_macd:.2f}"[:6] if profit_macd is not None else '',
                'SLoss': f"{safe_float_conversion(row.get('MA Stop Loss (%)')):.2f}"[:6] if safe_float_conversion(row.get('MA Stop Loss (%)')) is not None else '',
                'Profit%': f"{profit_macd:.2f}"[:6],
                'Strat': strategy_short,
                'Industry': industry
            }
            macd_rows.append(macd_row)

        if ma_signal in ['Buy', 'Sell'] and (profit_ma is not None and profit_ma >= min_profit_threshold):
            ma_row = {
                'Symb': row['Symbol'], 'MA': ma_signal,
                'TProfit': f"{profit_ma:.2f}"[:6] if profit_ma is not None else '',
                'SLoss': f"{safe_float_conversion(row.get('MA Stop Loss (%)')):.2f}"[:6] if safe_float_conversion(row.get('MA Stop Loss (%)')) is not None else '',
                'Profit%': f"{profit_ma:.2f}"[:6],
                'Strat': strategy_short,
                'Industry': industry
            }
            ma_rows.append(ma_row)

    return pd.DataFrame(macd_rows), pd.DataFrame(ma_rows), abbrev_dict


def signal_list_for_user(update: Update, context: CallbackContext):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    state = menu_state().rstrip('\n')

    if state == 'crypto_signals':
        file_path = os.path.join(BASE_DIR, '..', 'crypto_dev', 'crypto_signal.csv')
        output_file = os.path.join(BASE_DIR, '..', 'crypto_dev', 'crypto_signals.txt')
    elif state == 'stock_signal':
        file_path = os.path.join(BASE_DIR, '..', 'stock_dev', 'stock_signal.csv')
        output_file = os.path.join(BASE_DIR, '..', 'stock_dev', 'stock_signals.txt')
    elif state == 'forex_signal':
        file_path = os.path.join(BASE_DIR, '..', 'forex_dev', 'forex_signal.csv')
        output_file = os.path.join(BASE_DIR, '..', 'forex_dev', 'forex_signals.txt')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Невідомий тип активу.")
        return

    df = pd.read_csv(file_path)

    macd_df, ma_df, abbrev_dict = filter_and_classify_signals(df, state)
    _, strategy_descriptions = determine_strategy(row=None)

    with open(output_file, 'w', encoding='utf-8') as file:
        table_macd = create_user_table_by_strategy(macd_df, "MACD Signals", abbrev_dict)
        table_ma = create_user_table_by_strategy(ma_df, "MA Signals", abbrev_dict)

        file.write(table_macd)
        file.write(table_ma)
        file.write(add_industry_abbreviations(abbrev_dict))
        file.write(add_strategy_descriptions(strategy_descriptions))

    with open(output_file, 'rb') as document:
        context.bot.send_document(chat_id=update.effective_chat.id, document=document)

    return macd_df, ma_df

