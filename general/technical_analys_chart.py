import numpy as np
import pandas as pd
import yfinance as yf
from scipy.signal import find_peaks


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
    key_level = [level[0] for level in levels[:3]]  # Три найважливіші рівні

    return top_line_start, top_line_end, bottom_line_start, bottom_line_end, key_level


def calculate_relative_highs_lows(df, date_column="Date", high_column="High", low_column="Low", period_days=365):
    # Переконаємося, що колонка з датами має формат datetime
    df[date_column] = pd.to_datetime(df[date_column])

    # Фільтруємо дані за заданий період
    start_date = df[date_column].max() - pd.Timedelta(days=period_days)
    df_filtered = df[df[date_column] >= start_date].reset_index(drop=True)

    # Знаходимо відносні максимуми для колонки High
    high_peaks, _ = find_peaks(df_filtered[high_column])

    # Знаходимо відносні мінімуми для колонки Low
    low_troughs, _ = find_peaks(-df_filtered[low_column])

    # Додаємо колонки для результатів
    df_filtered["Relative High"] = False
    df_filtered["Relative Low"] = False

    df_filtered.loc[high_peaks, "Relative High"] = True
    df_filtered.loc[low_troughs, "Relative Low"] = True

    return df_filtered


# Приклад використання функції
# Задайте ваш DataFrame і бажаний період у днях
# df = ваш DataFrame
# result = calculate_relative_highs_lows(df, date_column="Date", high_column="High", low_column="Low", period_days=180)
# print(result)


def price_position(prices, trends_lines):
    price = prices[-1]
    trends_line = trends_lines[-1]
    lines_sorted = sorted(trends_line)  # Сортуємо лінії за значенням
    lower_line = None
    upper_line = None

    for i in range(len(lines_sorted)):
        if lines_sorted[i] <= price:
            lower_line = lines_sorted[i]
        elif lines_sorted[i] > price:
            upper_line = lines_sorted[i]
            break

    return lower_line, price, upper_line


def get_y_trend_lines(coords, x):
    """
    Обчислює координати Y для верхньої та нижньої трендових ліній за заданим X.

    :param coords: Список координат у форматі [(x1, y1), (x2, y2), (x3, y3), (x4, y4)],
                   де перші дві координати — верхня лінія тренду,
                   а інші дві — нижня.
    :param x: Значення X, для якого потрібно обчислити Y.
    :return: Словник із координатами Y для верхньої та нижньої ліній.
    """
    last_line_x = coords[1][0] - x
    # Розпакування координат
    x1, y1 = coords[0]
    x2, y2 = coords[1]
    x3, y3 = coords[2]
    x4, y4 = coords[3]

    # Формули для обчислення Y за рівнянням прямої y = mx + b
    # Верхня лінія
    m_upper = (y2 - y1) / (x2 - x1)  # Кутовий коефіцієнт
    b_upper = y1 - m_upper * x1  # Вільний член
    y_upper = m_upper * last_line_x + b_upper

    # Нижня лінія
    m_lower = (y4 - y3) / (x4 - x3)  # Кутовий коефіцієнт
    b_lower = y3 - m_lower * x3  # Вільний член
    y_lower = m_lower * last_line_x + b_lower

    return {"upper_y": y_upper, "lower_y": y_lower}


def find_extrema_indices(data, periods, mode):
    """
    Finds the indices of relative extrema (minima or maxima) in a list of data based on the given period.

    Parameters:
    - data (list): The list of numeric values.
    - periods (int): The number of previous and subsequent periods to consider.
    - mode (str): Either 'min' for minima or 'max' for maxima.

    Returns:
    - list: A list of indices corresponding to extrema.
    """
    if mode not in ["min", "max"]:
        raise ValueError("Mode must be either 'min' or 'max'.")

    extrema_indices = []
    for i in range(len(data)):
        # Define the range of indices to check
        start_idx = max(0, i - periods)
        end_idx = min(len(data), i + periods + 1)
        window = data[start_idx:end_idx]

        # Determine if current value is a local extremum
        if mode == "min" and data[i] == min(window):
            extrema_indices.append(i)
        elif mode == "max" and data[i] == max(window):
            extrema_indices.append(i)

    return extrema_indices


def determine_trend(lines):
    y_start_top = (lines[0][1])
    y_end_top = (lines[1][1])
    y_start_bot = (lines[2][1])
    y_end_bot = (lines[3][1])
    if y_start_top < y_end_top and y_start_bot < y_end_bot:
        return 'upward trend'
    if y_start_top > y_end_top and y_start_bot > y_end_bot:
        return 'downward trend'


stock = yf.Ticker("AAPL")
data = stock.history(period="1y")
# Використання функції


def technical_analysis():
    price_list = (data['Close'].tolist()[-30:])
    price_list_high = (data['High'].tolist()[-30:])
    price_list_low = (data['Low'].tolist()[-30:])
    print(price_list_high)
    # print(price_list_low)

    tend_lines = (calculate_trend_lines(data))
    key_levels = tend_lines[-1]
    trend_line = tend_lines[0:4]

    extrema_indices_max = find_extrema_indices(price_list_high, 15, 'max')
    extrema_indices_min = find_extrema_indices(price_list_high, 15, 'min')
    trend = determine_trend(trend_line)
    print(extrema_indices_max)
    # print(extrema_indices_min)
    # print(key_levels)
    # print(trend_line)
    # print(trend)
    # print(get_y_trend_lines(trend_line, extrema_indices_max[0]))

    def extrema_and_line(extrema_index, key_levels, trend_lines, price_list):
        print('extr', extrema_index)

        last_index = extrema_index[-1]
        y_coords = get_y_trend_lines(trend_lines, last_index)
        print('y', y_coords)
        print(price_list[last_index])
        print(price_list)
    extrema_and_line(extrema_indices_max, key_levels, trend_line, price_list_high)


technical_analysis()
