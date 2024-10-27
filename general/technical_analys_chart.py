import numpy as np


def calculate_trend_lines_and_levels(data, interval_percent=35):
    """
    Розраховує координати трендових ліній, ключові рівні та 200-денну ковзну середню (EMA).

    Параметри:
    - data: DataFrame, що містить історичні дані з колонками 'High', 'Low' та 'Close'.
    - interval_percent: відсоток, що визначає розмір інтервалу для пошуку ключових рівнів.

    Повертає:
    - top_line_start, top_line_end: координати верхньої трендової лінії.
    - bottom_line_start, bottom_line_end: координати нижньої трендової лінії.
    - key_levels: список ключових рівнів.
    - ma_200: значення 200-денної ковзної середньої.
    """

    def rmax(data):
        return [(i, p) for i, p in enumerate(data['High']) if p == max(data['High'][max(0, i - 5):i + 6])]

    def rmin(data):
        return [(i, p) for i, p in enumerate(data['Low']) if p == min(data['Low'][max(0, i - 5):i + 6])]

    def get_trend_line(points, data_length):
        if len(points) < 2:
            return None, None
        start = points[0]
        end = max(points[1:], key=lambda x: x[1])
        m = (end[1] - start[1]) / (end[0] - start[0])
        y_end = m * (data_length - start[0]) + start[1]
        return start, (data_length, y_end)

    # Розрахунок верхньої та нижньої ліній тренду
    top_line_start, top_line_end = get_trend_line(rmax(data), len(data))
    bottom_line_start, bottom_line_end = get_trend_line(rmin(data), len(data))

    # Розрахунок ключових рівнів
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

    # Вибір трьох найважливіших рівнів
    levels.sort(key=lambda x: x[1], reverse=True)
    key_levels = [level[0] for level in levels[:3]]  # Три найважливіші рівні

    # Розрахунок 200-денної ковзної середньої (EMA)
    ma_200 = data['Close'].ewm(span=200, adjust=False).mean().iloc[-1]

    return top_line_start, top_line_end, bottom_line_start, bottom_line_end, key_levels, ma_200


def generate_text_analysis(ticker, top_line_start, top_line_end, bottom_line_start, bottom_line_end, key_levels, ma_200,
                           latest_close, language='Ukrainian', state=''):
    """
    Генерує текстовий опис технічного аналізу на основі розрахованих ліній тренду, ключових рівнів та 200-денної EMA.
    Враховує напрямок руху ціни, близькість до ключових рівнів та можливі сценарії пробою або відбою від рівнів.
    """

    # Визначення напрямку тренду на основі EMA 200 та відстані від неї
    distance_to_ma = abs(latest_close - ma_200)
    trend_strength_threshold = 0.02 * latest_close  # Наприклад, 2% відстань для сильного тренду
    neutral_threshold = 0.01 * latest_close  # Поріг для нейтрального тренду (1%)

    if distance_to_ma < neutral_threshold:
        trend_direction = "neutral" if language == 'English' else "нейтральний"
    elif latest_close > ma_200 and distance_to_ma > trend_strength_threshold:
        trend_direction = "strong upward" if language == 'English' else "сильний висхідний"
    elif latest_close < ma_200 and distance_to_ma > trend_strength_threshold:
        trend_direction = "strong downward" if language == 'English' else "сильний низхідний"
    elif latest_close > ma_200:
        trend_direction = "upward" if language == 'English' else "висхідний"
    else:
        trend_direction = "downward" if language == 'English' else "низхідний"

    support_resistance_analysis = []

    # Аналіз трендових ліній для 'stock_company_info'
    if state == 'stock_company_info' and top_line_start and top_line_end:
        support_resistance_analysis.append(
            f"The {ticker} shows a {trend_direction} trend with an upper trendline starting at "
            f"{top_line_start[1]:.2f} and ending at {top_line_end[1]:.2f}."
            if language == 'English' else
            f"Актив {ticker} демонструє {trend_direction} тренд із верхньою трендовою лінією, що починається на рівні "
            f"{top_line_start[1]:.2f} та закінчується на {top_line_end[1]:.2f}."
        )

    # Визначення найближчого рівня та відстані до нього
    closest_level = min(key_levels, key=lambda x: abs(x - latest_close))
    distance_to_level = abs(latest_close - closest_level)
    level_proximity_threshold = 0.02 * latest_close  # Поріг близькості для рівнів (2%)

    # Логіка для різних сценаріїв
    if distance_to_level < level_proximity_threshold:
        if trend_direction in ["upward", "strong upward"]:
            support_resistance_analysis.append(
                f"The price of {ticker} is close to the key level {closest_level:.2f} in an upward trend. "
                "If the price consolidates at this level, a breakout is possible. However, if the trend weakens, a pullback could occur."
                if language == 'English' else
                f"Ціна активу {ticker} знаходиться біля ключового рівня {closest_level:.2f} при висхідному тренді. "
                "Якщо ціна консолідується на цьому рівні, можливий пробій. Проте, якщо тренд ослабне, можливий відкат."
            )
        elif trend_direction in ["downward", "strong downward"]:
            support_resistance_analysis.append(
                f"The price is near the key level {closest_level:.2f} in a downward trend. "
                "A consolidation at this level could lead to further decline, but a bounce might indicate a temporary support."
                if language == 'English' else
                f"Ціна перебуває біля ключового рівня {closest_level:.2f} при низхідному тренді. "
                "Консолідація на цьому рівні може призвести до подальшого падіння, але відскок може вказати на тимчасову підтримку."
            )
        else:
            support_resistance_analysis.append(
                f"The price of {ticker} is currently near the key level {closest_level:.2f}, suggesting indecisiveness. "
                "Traders should monitor for potential breakouts or rebounds."
                if language == 'English' else
                f"Ціна активу {ticker} наразі перебуває біля ключового рівня {closest_level:.2f}, що свідчить про невизначеність. "
                "Трейдерам варто спостерігати за можливими пробоями або відскоками."
            )
    elif latest_close > closest_level:
        support_resistance_analysis.append(
            f"The price has just broken above the key level {closest_level:.2f}, which may suggest further upward movement."
            if language == 'English' else
            f"Ціна щойно пробила ключовий рівень {closest_level:.2f}, що може вказувати на подальший висхідний рух."
        )
    else:
        support_resistance_analysis.append(
            f"The price is approaching the support level at {closest_level:.2f}. If this level holds, it could offer a buying opportunity. "
            "A failure to hold may signal further decline."
            if language == 'English' else
            f"Ціна наближається до рівня підтримки на рівні {closest_level:.2f}. Якщо рівень витримає, це може бути гарною можливістю для покупки. "
            "Невдача утримати рівень може сигналізувати про подальше падіння."
        )

    # Загальний аналіз ситуації на ринку
    analysis = "\n".join(support_resistance_analysis)
    analysis += (
        f"\nCurrently, the price is trading at {latest_close:.2f}. Observe how the price interacts with these levels for potential breakout or reversal signals."
        if language == 'English' else
        f"\nНаразі ціна торгується на рівні {latest_close:.2f}. Слідкуйте за взаємодією ціни з цими рівнями для можливих сигналів пробою або розвороту."
    )

    # Додаткові рекомендації на основі тренду
    if trend_direction == "strong upward" or trend_direction == "upward":
        analysis += (
            "\nThe upward trend suggests potential further growth, especially if resistance levels are broken."
            if language == 'English' else
            "\nВисхідний тренд вказує на можливість подальшого зростання, особливо якщо рівні опору будуть пробиті."
        )
    elif trend_direction == "strong downward" or trend_direction == "downward":
        analysis += (
            "\nThe downward trend indicates market weakness; exercise caution with purchases."
            if language == 'English' else
            "\nНизхідний тренд вказує на слабкість ринку; будьте обережні з покупками."
        )
    elif trend_direction == "neutral":
        analysis += (
            "\nThe neutral trend suggests uncertainty, which may precede a change in price direction."
            if language == 'English' else
            "\nНейтральний тренд вказує на невизначеність, що може передувати зміні напрямку ціни."
        )

    return analysis



def analyze_ticker(ticker, data, language='Ukrainian', state=''):
    """
    Розраховує трендові лінії, ключові рівні та повертає текстовий аналіз для активу.

    Параметри:
    - ticker: тикер активу.
    - data: DataFrame, що містить історичні дані.
    - language: мова аналізу ('Ukrainian' або 'English').
    - state: стан меню, який впливає на аналіз ('stock_company_info' чи інші).

    Повертає:
    - Текстовий опис технічного аналізу.
    """
    # Розрахунок трендових ліній, рівнів та EMA 200
    top_line_start, top_line_end, bottom_line_start, bottom_line_end, key_levels, ma_200 = calculate_trend_lines_and_levels(data)
    latest_close = data['Close'].iloc[-1]

    # Генерація текстового аналізу
    return generate_text_analysis(
        ticker=ticker,
        top_line_start=top_line_start,
        top_line_end=top_line_end,
        bottom_line_start=bottom_line_start,
        bottom_line_end=bottom_line_end,
        key_levels=key_levels,
        ma_200=ma_200,
        latest_close=latest_close,
        language=language,
        state=state
    )
