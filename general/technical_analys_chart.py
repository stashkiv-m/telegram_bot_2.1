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

    Параметри:
    - ticker: тикер активу.
    - top_line_start, top_line_end: координати верхньої трендової лінії.
    - bottom_line_start, bottom_line_end: координати нижньої трендової лінії.
    - key_levels: список ключових рівнів.
    - ma_200: значення 200-денної ковзної середньої (EMA).
    - latest_close: остання ціна закриття.
    - language: мова аналізу ('Ukrainian' або 'English').
    - state: стан меню, який впливає на аналіз ('stock_company_info' чи інші).

    Повертає:
    - Текстовий опис технічного аналізу українською або англійською мовою.
    """

    # Визначення напрямку тренду на основі EMA 200
    distance_to_ma = abs(latest_close - ma_200)
    neutral_threshold = 0.01 * latest_close  # Поріг для нейтрального тренду (1%)

    if distance_to_ma < neutral_threshold:
        trend_direction = "neutral" if language == 'English' else "нейтральний"
    elif latest_close > ma_200:
        trend_direction = "upward" if language == 'English' else "висхідний"
    else:
        trend_direction = "downward" if language == 'English' else "низхідний"

    support_resistance_analysis = []

    # Додаємо аналіз трендових ліній лише для 'stock_company_info'
    if state == 'stock_company_info':
        if top_line_start and top_line_end:
            support_resistance_analysis.append(
                f"The {ticker} shows a {trend_direction} trend with an upper trendline starting at "
                f"{top_line_start[1]:.2f} and ending at {top_line_end[1]:.2f}."
                if language == 'English' else
                f"Актив {ticker} демонструє {trend_direction} тренд із верхньою трендовою лінією, що починається на рівні "
                f"{top_line_start[1]:.2f} та закінчується на {top_line_end[1]:.2f}."
            )
        if bottom_line_start and bottom_line_end:
            support_resistance_analysis.append(
                f"The lower trendline starts at {bottom_line_start[1]:.2f} and ends at {bottom_line_end[1]:.2f}, "
                f"indicating a potential support zone."
                if language == 'English' else
                f"Нижня трендова лінія починається на рівні {bottom_line_start[1]:.2f} та закінчується на {bottom_line_end[1]:.2f}, "
                f"що може свідчити про потенційну зону підтримки."
            )
    else:
        support_resistance_analysis.append(
            f"The {ticker} shows a {trend_direction} trend."
            if language == 'English' else
            f"Актив {ticker} демонструє {trend_direction} тренд."
        )

    # Аналіз ключових рівнів з урахуванням близькості до ціни
    levels_description = ", ".join(f"{level:.2f}" for level in key_levels)
    closest_level = min(key_levels, key=lambda x: abs(x - latest_close))
    distance_to_level = abs(latest_close - closest_level)
    level_proximity_threshold = 0.01 * latest_close

    if distance_to_level < level_proximity_threshold:
        support_resistance_analysis.append(
            f"The price of {ticker} is currently near the key level {closest_level:.2f}. "
            "Traders should be cautious as various scenarios are possible: the price may consolidate before a breakout, indicating market uncertainty, "
            "or it may bounce off this level."
            if language == 'English' else
            f"Ціна активу {ticker} наразі перебуває поблизу ключового рівня {closest_level:.2f}. "
            "Трейдерам варто бути обережними, оскільки можливі різні сценарії: ціна може консолідуватися перед пробоєм, що свідчить про невпевненість ринку, "
            "або ж відскочити від цього рівня."
        )
    elif latest_close > closest_level:
        support_resistance_analysis.append(
            f"The price has just broken above the key level {closest_level:.2f}, which may indicate a potential move toward the next resistance level. "
            "Support at this level could present a buying opportunity."
            if language == 'English' else
            f"Ціна щойно пробила ключовий рівень {closest_level:.2f}, що може свідчити про можливий подальший рух до наступного рівня опору. "
            "Підтримка на цьому рівні може стати хорошою можливістю для покупців."
        )
    else:
        support_resistance_analysis.append(
            f"The price is approaching the key level {closest_level:.2f}. If the price breaks through easily, further movement toward the next support zone is possible. "
            "However, if a pause or rebound occurs, it may indicate a temporary halt in the decline."
            if language == 'English' else
            f"Ціна наближається до ключового рівня {closest_level:.2f}. Якщо ціна легко проб'є цей рівень, то можливий подальший рух до наступної зони підтримки. "
            "Якщо ж відбудеться зупинка або відскок, це може свідчити про тимчасову паузу в падінні."
        )

    # Загальний аналіз ситуації на ринку
    analysis = "\n".join(support_resistance_analysis)
    analysis += (
        f"\nCurrently, the price is trading at {latest_close:.2f}, suggesting that traders should closely monitor these key levels."
        "\nIt is recommended to observe the asset's behavior around these levels for potential breakout or reversal signals."
        if language == 'English' else
        f"\nНаразі ціна торгується на рівні {latest_close:.2f}, що вказує на необхідність уважного спостереження за цими ключовими рівнями."
        "\nРекомендується стежити за поведінкою активу навколо цих рівнів для потенційних сигналів про пробій або розворот."
    )

    # Додаткові рекомендації на основі тренду
    if trend_direction == ("upward" if language == 'English' else "висхідний"):
        if distance_to_level < level_proximity_threshold:
            analysis += (
                "\nConsidering the upward trend and proximity to the level, consolidation before a breakout is possible. "
                "However, if the level is broken, this could signal further growth."
                if language == 'English' else
                "\nВраховуючи висхідний тренд та близькість до рівня, можлива консолідація перед пробоєм. "
                "Однак, якщо рівень буде пробитий, це може стати сигналом для подальшого зростання."
            )
        else:
            analysis += (
                "\nThe upward trend suggests potential further growth, especially if the price breaks through resistance."
                if language == 'English' else
                "\nВисхідний тренд вказує на можливість подальшого зростання, особливо якщо ціна пробиває опір."
            )
    elif trend_direction == ("downward" if language == 'English' else "низхідний"):
        if distance_to_level < level_proximity_threshold:
            analysis += (
                "\nWith a downward trend and proximity to the level, a bounce from support or consolidation is possible. "
                "If the level does not hold, further decline to the next support is likely."
                if language == 'English' else
                "\nПри низхідному тренді та близькості до рівня, можливий відскок від підтримки або консолідація. "
                "Якщо рівень не витримає, можливий подальший спад до наступної підтримки."
            )
        else:
            analysis += (
                "\nThe downward trend indicates market weakness, and caution is advised with purchases until clear reversal signals appear."
                if language == 'English' else
                "\nНизхідний тренд вказує на слабкість ринку, і варто бути обережними з покупками до появи чітких сигналів на розворот."
            )
    else:
        analysis += (
            "\nThe neutral trend suggests market uncertainty, which may indicate a potential change in price direction. "
            "It is crucial to closely watch for breakouts to understand the future movement."
            if language == 'English' else
            "\nНейтральний тренд вказує на невизначеність на ринку, що може свідчити про потенційну зміну напрямку ціни. "
            "Варто уважно стежити за пробоями рівнів для розуміння подальшого напрямку."
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
