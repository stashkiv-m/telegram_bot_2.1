import numpy as np
import pandas as pd
import os
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext

from state_update_menu import menu_state


def abbreviate_industry(industry_name, max_word_length=3, abbrev_dict=None):
    words = industry_name.split()
    abbreviated = ''.join([word[:max_word_length].capitalize() for word in words])
    if abbrev_dict is not None:
        abbrev_dict[abbreviated] = industry_name  # Додаємо до словника відповідність
    return abbreviated


def analyze_stock_data(file_path, group_by="Industry"):
    data = pd.read_csv(file_path)
    data.replace("-", np.nan, inplace=True)

    # Словник для збереження відповідностей між скороченнями та повними назвами
    abbrev_dict = {}

    # Скорочуємо назви індустрій для компактного відображення
    data['Industry'] = data['Industry'].apply(
        lambda x: abbreviate_industry(x, abbrev_dict=abbrev_dict) if pd.notna(x) else x)

    numeric_cols = ['Market Cap', 'ROE (%)', 'ROA (%)', 'Net Margin (%)',
                    'Debt to Assets', 'Book Value Per Share'] + [f'close_day_{i}' for i in range(1, 8)]
    data[numeric_cols] = data[numeric_cols].apply(pd.to_numeric, errors='coerce')

    grouped = data.groupby(group_by).agg({
        'Market Cap': 'mean',
        'ROE (%)': 'mean',
        'ROA (%)': 'mean',
        'Net Margin (%)': 'mean',
        'Debt to Assets': 'mean',
        'Book Value Per Share': 'mean'
    }).reset_index()

    def format_market_cap(value):
        if value >= 1e9:
            return f"{value / 1e9:.2f} $B"
        elif value >= 1e6:
            return f"{value / 1e6:.2f} $M"
        else:
            return f"{value:.2f}"

    top_5_market_cap = grouped.nlargest(5, 'Market Cap')
    top_5_market_cap['Market Cap'] = top_5_market_cap['Market Cap'].apply(format_market_cap)

    top_5_roe_roa = grouped.nlargest(5, ['ROE (%)', 'ROA (%)'])
    top_5_net_margin = grouped.nlargest(5, 'Net Margin (%)')
    bottom_5_debt_assets = grouped.nsmallest(5, 'Debt to Assets')
    bottom_5_book_value = grouped.nsmallest(5, 'Book Value Per Share')

    close_days = [f'close_day_{i}' for i in range(1, 8)]
    data['close_avg'] = data[close_days].mean(axis=1)
    data['growth'] = (data['close_day_7'] - data['close_day_1']) / data['close_day_1'] * 100

    industry_growth = data.groupby(group_by)['growth'].mean().reset_index()
    top_3_growth_industries = industry_growth.nlargest(3, 'growth')
    bottom_3_decline_industries = industry_growth.nsmallest(3, 'growth')

    top_5_stocks_growth = data.nlargest(5, 'growth')[['Symbol', 'growth']]
    bottom_5_stocks_decline = data.nsmallest(5, 'growth')[['Symbol', 'growth']]

    macd_counts = data[data['MACD Signal'].isin(['Buy', 'Sell'])]
    macd_counts_by_group = macd_counts.groupby([group_by, 'MACD Signal']).size().unstack(fill_value=0).reset_index()

    total_macd_signals = macd_counts.shape[0]
    macd_counts_by_group['Buy_pct'] = (macd_counts_by_group['Buy'] / total_macd_signals * 100).round(2)
    macd_counts_by_group['Sell_pct'] = (macd_counts_by_group['Sell'] / total_macd_signals * 100).round(2)

    total_buy_signals = macd_counts['MACD Signal'].value_counts().get('Buy', 0)
    total_sell_signals = macd_counts['MACD Signal'].value_counts().get('Sell', 0)
    total_buy_pct = (total_buy_signals / total_macd_signals * 100).round(2)
    total_sell_pct = (total_sell_signals / total_macd_signals * 100).round(2)

    top_5_buy_groups = macd_counts_by_group.nlargest(5, 'Buy')[[group_by, 'Buy', 'Buy_pct']]
    top_5_sell_groups = macd_counts_by_group.nlargest(5, 'Sell')[[group_by, 'Sell', 'Sell_pct']]

    # Відфільтруємо словник, щоб залишити лише використовувані індустрії
    used_industries = pd.concat([
        top_5_market_cap[group_by],
        top_5_roe_roa[group_by],
        top_5_net_margin[group_by],
        bottom_5_debt_assets[group_by],
        bottom_5_book_value[group_by],
        top_3_growth_industries[group_by],
        bottom_3_decline_industries[group_by],
        top_5_buy_groups[group_by],
        top_5_sell_groups[group_by]
    ]).unique()

    abbrev_dict_filtered = {abbrev: abbrev_dict[abbrev] for abbrev in used_industries if abbrev in abbrev_dict}

    return {
        'total_buy_signals': f"{total_buy_signals} ({total_buy_pct}%)",
        'total_sell_signals': f"{total_sell_signals} ({total_sell_pct}%)",
        'top_5_buy_groups': top_5_buy_groups,
        'top_5_sell_groups': top_5_sell_groups,
        'top_5_stocks_growth': top_5_stocks_growth,
        'bottom_5_stocks_decline': bottom_5_stocks_decline,
        'top_5_market_cap': top_5_market_cap,
        'top_5_roe_roa': top_5_roe_roa,
        'top_5_net_margin': top_5_net_margin,
        'bottom_5_debt_assets': bottom_5_debt_assets,
        'bottom_5_book_value': bottom_5_book_value,
        'top_3_growth_industries': top_3_growth_industries,
        'bottom_3_decline_industries': bottom_3_decline_industries,
        'industry_abbreviations': abbrev_dict_filtered  # Використовуємо тільки потрібні скорочення
    }


def format_results(results):
    formatted_output = {}

    def format_table(df, headers, col_widths):
        table = "| " + " | ".join([f"{h:{w}}" for h, w in zip(headers, col_widths)]) + " |\n"
        table += "|-" + "-|-".join(["-" * w for w in col_widths]) + "-|\n"
        for _, row in df.iterrows():
            row_data = " | ".join(
                [f"{str(x):{w}}"[:w] if isinstance(x, str) else f"{x:.2f}".rjust(w) for x, w in zip(row, col_widths)])
            table += f"| {row_data} |\n"
        return table

    # Загальна кількість сигналів
    formatted_output['Total Buy Signals'] = f"{results['total_buy_signals']}"
    formatted_output['Total Sell Signals'] = f"{results['total_sell_signals']}"

    # # Сигнали по індустріях
    # formatted_output['Top 5 Buy Signal Industries'] = format_table(results['top_5_buy_groups'],
    #                                                                ['Industry', 'Buy', 'Buy_pct'], [15, 5, 8])
    # formatted_output['Top 5 Sell Signal Industries'] = format_table(results['top_5_sell_groups'],
    #                                                                 ['Industry', 'Sell', 'Sell_pct'], [15, 5, 8])
    #
    # # Top 5 та Bottom 5 акцій по росту та падінню
    # formatted_output['Top 5 Stocks Growth'] = format_table(results['top_5_stocks_growth'], ['Symbol', 'growth'],
    #                                                        [10, 10])
    # formatted_output['Bottom 5 Stocks Decline'] = format_table(results['bottom_5_stocks_decline'], ['Symbol', 'growth'],
    #                                                            [10, 10])

    # Решта інформації про ринок
    formatted_output['Top 5 Market Cap Industries (Avg)'] = format_table(results['top_5_market_cap'],
                                                                         ['Industry', 'Market Cap'], [15, 10])
    formatted_output['Top 5 ROE Industries (Avg)'] = format_table(
        results['top_5_roe_roa'][['Industry', 'ROE (%)']].nlargest(5, 'ROE (%)'), ['Industry', 'ROE (%)'], [15, 10])
    formatted_output['Top 5 ROA Industries (Avg)'] = format_table(
        results['top_5_roe_roa'][['Industry', 'ROA (%)']].nlargest(5, 'ROA (%)'), ['Industry', 'ROA (%)'], [15, 10])
    formatted_output['Top 5 Net Margin Industries (Avg)'] = format_table(
        results['top_5_net_margin'][['Industry', 'Net Margin (%)']], ['Industry', 'Net Margin (%)'], [15, 10])
    formatted_output['Bottom 5 Debt to Assets Industries (Avg)'] = format_table(
        results['bottom_5_debt_assets'][['Industry', 'Debt to Assets']], ['Industry', 'Debt to Assets'], [15, 10])
    formatted_output['Bottom 5 Book Value Industries (Avg)'] = format_table(
        results['bottom_5_book_value'][['Industry', 'Book Value Per Share']], ['Industry', 'Book Value Per Share'],
        [15, 10])
    formatted_output['Top 3 Growth Industries (Avg)'] = format_table(results['top_3_growth_industries'],
                                                                     ['Industry', 'growth'], [15, 10])
    formatted_output['Bottom 3 Decline Industries (Avg)'] = format_table(results['bottom_3_decline_industries'],
                                                                         ['Industry', 'growth'], [15, 10])

    # Додаємо розділ для словника скорочень індустрій
    abbrev_dict = results['industry_abbreviations']
    abbrev_table = "| Abbreviation | Full Industry Name |\n"
    abbrev_table += "|--------------|---------------------|\n"
    for abbrev, full_name in abbrev_dict.items():
        abbrev_table += f"| {abbrev:<12} | {full_name} |\n"
    formatted_output['Industry Abbreviations'] = abbrev_table

    return formatted_output




def analyze_and_format(file_path, group_by="Industry"):
    results = analyze_stock_data(file_path, group_by)
    return format_results(results)


def stock_market_overview():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(BASE_DIR, '..', 'developer_functions', 'stock_dev', 'stock_signal_test.csv')
    output_folder = os.path.join(BASE_DIR, '..', 'developer_functions', 'stock_dev', 'market_overwiev')

    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' not found.")
        return None

    if not os.path.exists(output_folder):
        print(f"Error: Output directory '{output_folder}' not found.")
        return None

    # Очищення папки
    for file in os.listdir(output_folder):
        file_path = os.path.join(output_folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(output_folder, f"market_overview_{date_str}.txt")

    # Генерація та запис результатів аналізу
    formatted_results = analyze_and_format(input_file_path)
    if formatted_results is not None:
        with open(output_file, "w", encoding="utf-8") as file:
            for key, value in formatted_results.items():
                file.write(f"{key}:\n{value}\n\n")
        return output_file  # Повертаємо шлях до згенерованого файлу
    else:
        print(f"Error: Could not analyze data from '{input_file_path}'")
        return None


# Функція для надсилання файлу користувачу
def send_market_overview(update: Update, context: CallbackContext):
    state = menu_state().rstrip('\n')
    if state == 'mrkt_overview':
        # Створюємо файл огляду ринку
        file_path = stock_market_overview()

        if file_path and os.path.exists(file_path):
            # Надсилаємо файл користувачу
            chat_id = update.effective_chat.id
            context.bot.send_document(chat_id=chat_id, document=open(file_path, 'rb'))
    else:
        pass



