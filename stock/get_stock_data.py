import pandas as pd


def format_number(value, is_currency=True):
    if value is None:
        return "N/A"
    elif abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B" if not is_currency else f"${value / 1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M" if not is_currency else f"${value / 1_000_000:.2f}M"
    else:
        return f"{value:,.2f}" if not is_currency else f"${value:,.2f}"


def explain_metric(name, lang='English'):
    explanations = {
        "P/E Ratio": {
            "en": "Price-to-Earnings: how much investors are willing to pay per dollar of earnings.",
            "ua": "Ціна/Прибуток: скільки інвестори готові платити за 1 долар прибутку."
        },
        "Price to Book": {
            "en": "Price-to-Book: compares market price to book value.",
            "ua": "Ціна до балансової вартості: порівнює ринкову ціну з балансовою вартістю компанії."
        },
        "Dividend Yield": {
            "en": "Shows annual dividend income as a percentage of stock price.",
            "ua": "Річний дивіденд у відсотках до ціни акції."
        },
        "ROE": {
            "en": "Return on Equity: how efficiently equity generates profit.",
            "ua": "Рентабельність капіталу: ефективність використання власного капіталу."
        },
        "Debt-to-Equity": {
            "en": "Shows leverage by comparing total debt to equity.",
            "ua": "Відношення боргу до капіталу: показує рівень заборгованості компанії."
        },
        "Profit Margin": {
            "en": "Net income as a percentage of revenue.",
            "ua": "Чистий прибуток як відсоток від доходу."
        }
    }
    return explanations.get(name, {}).get('ua' if lang == 'Ukrainian' else 'en', "No description")

def analyze_metric(name, value):
    if value is None:
        return "N/A", "Н/Д"
    analysis_en, analysis_ua = "", ""
    if name == "P/E Ratio":
        if value < 10: analysis_en, analysis_ua = "Undervalued", "Недооцінена"
        elif value > 30: analysis_en, analysis_ua = "Overvalued", "Переоцінена"
        else: analysis_en, analysis_ua = "Fairly valued", "Справедливо оцінена"
    elif name == "ROE":
        if value > 20: analysis_en, analysis_ua = "High profitability", "Висока прибутковість"
        elif value > 10: analysis_en, analysis_ua = "Moderate profitability", "Середня прибутковість"
        else: analysis_en, analysis_ua = "Low profitability", "Низька прибутковість"
    elif name == "Debt-to-Equity":
        if value < 1: analysis_en, analysis_ua = "Low debt", "Низький борг"
        elif value < 2: analysis_en, analysis_ua = "Moderate debt", "Середній борг"
        else: analysis_en, analysis_ua = "High debt", "Високий борг"
    elif name == "Dividend Yield":
        if value > 5: analysis_en, analysis_ua = "High dividend", "Високі дивіденди"
        elif value > 2: analysis_en, analysis_ua = "Moderate dividend", "Середні дивіденди"
        else: analysis_en, analysis_ua = "Low dividend", "Низькі дивіденди"
    elif name == "Price to Book":
        if value < 1: analysis_en, analysis_ua = "Undervalued", "Недооцінена"
        elif value > 3: analysis_en, analysis_ua = "Overvalued", "Переоцінена"
        else: analysis_en, analysis_ua = "Fair value", "Справедлива ціна"
    elif name == "Profit Margin":
        if value > 20: analysis_en, analysis_ua = "Strong margin", "Висока маржа"
        elif value > 10: analysis_en, analysis_ua = "Moderate margin", "Середня маржа"
        else: analysis_en, analysis_ua = "Low margin", "Низька маржа"
    else:
        analysis_en, analysis_ua = "No analysis", "Без аналізу"
    return analysis_en, analysis_ua

def get_stock_metrics(stock, ticker, language='English'):
    info = stock.info
    balance_sheet = stock.quarterly_balance_sheet
    income = stock.quarterly_financials

    def safe_get(func):
        try: return func()
        except: return None

    roe = safe_get(lambda: round((income.loc["Net Income"].iloc[0] / balance_sheet.loc["Stockholders Equity"].iloc[0]) * 100, 2))
    pe_ratio = safe_get(lambda: round(info.get("trailingPE", 0), 2))
    price_to_book = safe_get(lambda: round(info.get("priceToBook", 0), 2))
    dividend_yield = safe_get(lambda: round(info.get("dividendYield", 0) * 100, 2))
    debt_to_equity = safe_get(lambda: round(
        (balance_sheet.loc["Long Term Debt"].iloc[0] + balance_sheet.loc["Current Debt"].iloc[0]) /
        balance_sheet.loc["Stockholders Equity"].iloc[0], 2
    ))
    profit_margin = safe_get(lambda: round(
        (income.loc["Net Income"].iloc[0] / income.loc["Total Revenue"].iloc[0]) * 100, 2
    ))

    metrics = {
        "P/E Ratio": pe_ratio,
        "Price to Book": price_to_book,
        "Dividend Yield": dividend_yield,
        "ROE": roe,
        "Debt-to-Equity": debt_to_equity,
        "Profit Margin": profit_margin
    }

    report = f"📊 **{info.get('longName', ticker)}**\n"
    report += f"{'📁 Sector:' if language == 'English' else '📁 Сектор:'} {info.get('sector', 'N/A')}\n"
    report += f"{'🏭 Industry:' if language == 'English' else '🏭 Індустрія:'} {info.get('industry', 'N/A')}\n\n"
    report += f"{'📈 Metrics and Analysis:' if language == 'English' else '📈 Показники та Аналіз:'}\n"

    for name, value in metrics.items():
        desc = explain_metric(name, language)
        analysis_en, analysis_ua = analyze_metric(name, value)
        value_str = f"{value:.2f}" if isinstance(value, float) else "N/A"
        analysis = analysis_ua if language == 'Ukrainian' else analysis_en
        report += f"\n🔹 *{name}*: {value_str}\n"
        report += f"    - {desc}\n"
        report += f"    - {analysis}\n"

    return report
