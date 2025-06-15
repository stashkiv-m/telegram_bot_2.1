import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import yfinance as yf
import mplfinance as mpf

from state_update_menu import menu_state

matplotlib.use('Agg')  # Бекенд без GUI


def generate_chart(ticker, ignore_state_check=False):

    """
    Малює графік свічок для акцій або криптовалют з індикаторами MACD, трендовими лініями та ключовими рівнями.
    """

    # Очищуємо папку зображень перед створенням нового графіку
    def clear_folder(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f'Error deleting file {file_path}: {e}')

    # Розрахунок MACD індикаторів
    def calculate_macd(data):
        data['ema_12'] = data['Close'].ewm(span=12, adjust=False).mean()
        data['ema_26'] = data['Close'].ewm(span=26, adjust=False).mean()
        data['macd'] = data['ema_12'] - data['ema_26']
        data['signal'] = data['macd'].ewm(span=9, adjust=False).mean()
        data['macd_diff'] = data['macd'] - data['signal']
        return data

    # Створюємо додаткові графіки для MACD
    def create_addplots(data):
        mask = np.where(data['macd_diff'] > 0, 'g', 'r')
        addplot = [
            mpf.make_addplot(data['macd'], panel=2, color='fuchsia'),
            mpf.make_addplot(data['signal'], panel=2, color='skyblue'),
            mpf.make_addplot(data['macd_diff'], panel=2, type='bar', color=mask, alpha=0.5)
        ]
        return addplot

    # Розраховуємо лінії тренду та ключові рівні
    def calculate_trend_lines(data):
        def rmax(data):
            return [(i, p) for i, p in enumerate(data['High']) if p == max(data['High'][max(0, i - 5):i + 6])]

        def rmin(data):
            return [(i, p) for i, p in enumerate(data['Low']) if p == min(data['Low'][max(0, i - 5):i + 6])]

        def get_trend_line(points, data_length):
            start = points[0]
            end = max(points[1:], key=lambda x: x[1])
            m = (end[1] - start[1]) / (end[0] - start[0])
            y_end = m * (data_length - start[0]) + start[1]
            return start, (data_length, y_end)

        top_line_start, top_line_end = get_trend_line(rmax(data), len(data))
        bottom_line_start, bottom_line_end = get_trend_line(rmin(data), len(data))

        interval_percent = 35
        high = data['High'].max()
        low = data['Low'].min()
        range_size = high - low
        interval_size = range_size * (interval_percent / 100)

        levels = []
        for i in np.arange(low, high, interval_size):
            count_highs = np.sum((data['High'] >= i) & (data['High'] < i + interval_size))
            count_lows = np.sum((data['Low'] >= i) & (data['Low'] < i + interval_size))
            total_count = count_highs + count_lows
            levels.append((i + interval_size / 2, total_count))

        levels.sort(key=lambda x: x[1], reverse=True)
        key_levels = [level[0] for level in levels[:3]]  # Три найважливіші рівні

        return top_line_start, top_line_end, bottom_line_start, bottom_line_end, key_levels

    # Завантажуємо дані про акцію
    stock = yf.Ticker(ticker)
    data = stock.history(period="1y")

    # Очищуємо папку перед створенням нового графіку
    img_folder = "C:\\Users\\Mykhailo\\PycharmProjects\\bot_2.0\\img\\charts"
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
    clear_folder(img_folder)

    # Розрахунок MACD, трендових ліній та ключових рівнів
    data = calculate_macd(data)
    top_line_start, top_line_end, bottom_line_start, bottom_line_end, key_levels = calculate_trend_lines(data)
    addplot = create_addplots(data)

    # Створюємо графік свічок
    fig, axes = mpf.plot(data, type='candle', volume=True, style='charles',
                         figratio=(14, 7), figscale=1.2,
                         mav=(20, 50, 100),
                         ylabel='Price (USD)', ylabel_lower='Volume',
                         addplot=addplot,
                         panel_ratios=(6, 2, 1), returnfig=True)

    # Додаємо трендові лінії та ключові рівні на графік
    state = (menu_state() or '').rstrip('\n') if not ignore_state_check else ''

    ax = axes[0]
    if state == 'stock_company_info':
        ax.plot([top_line_start[0], top_line_end[0]], [top_line_start[1], top_line_end[1]], color='green', lw=1)
        ax.plot([bottom_line_start[0], bottom_line_end[0]], [bottom_line_start[1], bottom_line_end[1]], color='blue', lw=1)

    for level in key_levels:
        ax.axhline(y=level, color='orange', linestyle='--', lw=1)

    if ax.get_legend_handles_labels()[0]:
        ax.legend(loc='upper left', fontsize='small', frameon=False)

    ax.set_title(f'{ticker} Stock Price', fontsize=10, pad=10)
    ax.yaxis.set_tick_params(labelsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.xaxis.set_tick_params(labelsize=8, pad=5)

    for label in ax.get_xticklabels():
        label.set_ha('center')
        label.set_y(-0.03)

    ax.yaxis.grid(True, linestyle='--', alpha=0.7)

    fig.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.10)

    # Зберігаємо графік
    img_path = os.path.join(img_folder, f'{ticker}.png')
    fig.savefig(img_path, bbox_inches='tight', dpi=300)
    plt.close(fig)

    return img_path

# Виклик функції для перевірки
