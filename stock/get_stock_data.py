import yfinance as yf
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

def get_stock_metrics(stock, ticker, language='English'):
    balance_sheet = stock.quarterly_balance_sheet
    income_statement = stock.quarterly_financials
    dividends = stock.dividends
    dividends.index = dividends.index.tz_localize(None)

    report_date = pd.to_datetime(balance_sheet.columns[0]).date() if not balance_sheet.empty else "N/A"
    net_income = income_statement.loc["Net Income"].iloc[0] if "Net Income" in income_statement.index else None
    total_assets = balance_sheet.loc["Total Assets"].iloc[0] if "Total Assets" in balance_sheet.index else None
    total_equity = balance_sheet.loc["Stockholders Equity"].iloc[0] if "Stockholders Equity" in balance_sheet.index else None
    total_debt = (
        balance_sheet.loc["Long Term Debt"].iloc[0] if "Long Term Debt" in balance_sheet.index else 0
    ) + (
        balance_sheet.loc["Current Debt"].iloc[0] if "Current Debt" in balance_sheet.index else 0
    )
    revenue = income_statement.loc["Total Revenue"].iloc[0] if "Total Revenue" in income_statement.index else None
    operating_income = income_statement.loc["Operating Income"].iloc[0] if "Operating Income" in income_statement.index else None
    current_assets = balance_sheet.loc["Current Assets"].iloc[0] if "Current Assets" in balance_sheet.index else None
    current_liabilities = balance_sheet.loc["Current Liabilities"].iloc[0] if "Current Liabilities" in balance_sheet.index else None

    pe_ratio = stock.info.get('trailingPE', None)
    forward_pe = stock.info.get('forwardPE', None)
    roe = (net_income / total_equity) if total_equity and net_income else None
    roa = (net_income / total_assets) if total_assets and net_income else None
    debt_to_equity = (total_debt / total_equity) if total_equity else None
    current_ratio = (current_assets / current_liabilities) if current_assets and current_liabilities else None
    gross_margin = (
        (income_statement.loc["Gross Profit"].iloc[0] / revenue)
        if revenue and "Gross Profit" in income_statement.index else None
    )
    operating_margin = (operating_income / revenue) if revenue and operating_income else None
    profit_margin = (net_income / revenue) if revenue and net_income else None
    dividend_yield = stock.info.get('dividendYield', None)  # Отримання Dividend Yield з інформації акцій

    # Оцінка фінансових показників для більш індивідуального аналізу
    overvaluation = pe_ratio and pe_ratio > 25
    strong_profitability = roe and roe > 0.15
    moderate_profitability = roe and 0.10 < roe <= 0.15
    weak_profitability = roe and roe <= 0.10
    strong_balance = debt_to_equity and debt_to_equity < 0.5
    high_debt = debt_to_equity and debt_to_equity > 1.0
    solid_margin = gross_margin and gross_margin > 40
    low_liquidity = current_ratio and current_ratio < 1

    # Формуємо висновок на основі показників
    if language == 'Ukrainian':
        assessment_parts = []

        # Оцінка переоцінки
        if overvaluation:
            assessment_parts.append("Компанія може бути переоціненою, що збільшує ризик корекції ціни у майбутньому.")
        else:
            assessment_parts.append("Ціна акцій здається привабливою, що може свідчити про потенційний ріст.")

        # Оцінка прибутковості
        if strong_profitability:
            assessment_parts.append("Показник рентабельності власного капіталу (ROE) свідчить про високу прибутковість.")
        elif moderate_profitability:
            assessment_parts.append("ROE знаходиться на середньому рівні, що свідчить про стабільну, але не видатну прибутковість.")
        elif weak_profitability:
            assessment_parts.append("Низький рівень ROE може бути сигналом слабкої рентабельності.")

        # Оцінка боргового навантаження
        if strong_balance:
            assessment_parts.append("Баланс компанії виглядає здоровим із низьким співвідношенням боргу до власного капіталу.")
        elif high_debt:
            assessment_parts.append("Компанія має високе боргове навантаження, що може збільшити фінансові ризики у майбутньому.")

        # Оцінка рентабельності
        if solid_margin:
            assessment_parts.append("Високий рівень валової маржі свідчить про сильну конкурентну позицію.")
        else:
            assessment_parts.append("Рівень валової маржі свідчить про можливі труднощі в управлінні витратами.")

        # Оцінка ліквідності
        if low_liquidity:
            assessment_parts.append("Низький коефіцієнт поточної ліквідності може викликати труднощі у покритті короткострокових зобов'язань.")
        else:
            assessment_parts.append("Компанія має достатньо ресурсів для покриття своїх поточних зобов'язань.")

        overall_assessment = " ".join(assessment_parts)

    else:
        assessment_parts = []

        # Overvaluation assessment
        if overvaluation:
            assessment_parts.append("The company appears overvalued, increasing the risk of a future price correction.")
        else:
            assessment_parts.append("The stock price seems attractive, indicating potential growth opportunities.")

        # Profitability assessment
        if strong_profitability:
            assessment_parts.append("The ROE indicates strong profitability, a positive signal for investors.")
        elif moderate_profitability:
            assessment_parts.append("The ROE is at a moderate level, indicating stable but not exceptional profitability.")
        elif weak_profitability:
            assessment_parts.append("A low ROE might indicate weaker profitability compared to industry standards.")

        # Debt load assessment
        if strong_balance:
            assessment_parts.append("The company's balance sheet is healthy, with a low debt-to-equity ratio.")
        elif high_debt:
            assessment_parts.append("The company has a high debt burden, which could pose financial risks in the long term.")

        # Margin assessment
        if solid_margin:
            assessment_parts.append("A high gross margin indicates a strong competitive position in the market.")
        else:
            assessment_parts.append("The gross margin suggests potential challenges in managing costs efficiently.")

        # Liquidity assessment
        if low_liquidity:
            assessment_parts.append("Low current ratio may indicate challenges in covering short-term liabilities.")
        else:
            assessment_parts.append("The company appears well-positioned to meet its short-term obligations.")

        overall_assessment = " ".join(assessment_parts)

    # Формуємо звіт з перевірками мови
    if language == 'Ukrainian':
        report = f"**Огляд компанії: {stock.info.get('longName', 'N/A')} ({ticker})**\n"
        report += f"Сектор: {stock.info.get('sector', 'N/A')}\n"
        report += f"Індустрія: {stock.info.get('industry', 'N/A')}\n"
        report += f"Дата звіту: {report_date}\n"
        report += f"Офіційний вебсайт: {stock.info.get('website', 'Немає даних')}\n"
        report += f"\n**Фінансові показники:**\n"
        report += f"Ціна/прибуток (P/E Ratio): {format_number(pe_ratio, is_currency=False)}\n"
        report += f"Форвардний P/E: {format_number(forward_pe, is_currency=False)}\n"
        report += f"ROE: {round(roe * 100, 2) if roe else 'Немає даних'}%\n"
        report += f"ROA: {round(roa * 100, 2) if roa else 'Немає даних'}%\n"
        report += f"Debt-to-Equity Ratio: {round(debt_to_equity, 2) if debt_to_equity else 'Немає даних'}\n"
        report += f"Current Ratio: {round(current_ratio, 2) if current_ratio else 'Немає даних'}\n"
        report += f"Gross Margin: {round(gross_margin * 100, 2) if gross_margin else 'Немає даних'}%\n"
        report += f"Operating Margin: {round(operating_margin * 100, 2) if operating_margin else 'Немає даних'}%\n"
        report += f"Profit Margin: {round(profit_margin * 100, 2) if profit_margin else 'Немає даних'}%\n"
        report += f"Dividend Yield: {round(dividend_yield * 100, 2) if dividend_yield else 'Немає даних'}%\n"
        report += f"P/B Ratio: {format_number(stock.info.get('priceToBook', None), is_currency=False)}\n"
        report += f"\n**Висновок:**\n{overall_assessment}\n"
        report += f"\n**Дані для розрахунків:**\n"
        report += f"Чистий дохід: {format_number(net_income)}, Загальні активи: {format_number(total_assets)}, "
        report += f"Власний капітал: {format_number(total_equity)}\n"
        report += f"Загальний борг: {format_number(total_debt)}, Поточні активи: {format_number(current_assets)}, "
        report += f"Поточні зобов'язання: {format_number(current_liabilities)}\n"
        report += f"Дохід: {format_number(revenue)}, Операційний дохід: {format_number(operating_income)}"
    else:
        report = f"**Company Overview: {stock.info.get('longName', 'N/A')} ({ticker})**\n"
        report += f"Sector: {stock.info.get('sector', 'N/A')}\n"
        report += f"Industry: {stock.info.get('industry', 'N/A')}\n"
        report += f"Report Date: {report_date}\n"
        report += f"Official Website: {stock.info.get('website', 'No data available')}\n"
        report += f"\n**Financial Metrics:**\n"
        report += f"P/E Ratio: {format_number(pe_ratio, is_currency=False)}\n"
        report += f"Forward P/E: {format_number(forward_pe, is_currency=False)}\n"
        report += f"ROE: {round(roe * 100, 2) if roe else 'No data available'}%\n"
        report += f"ROA: {round(roa * 100, 2) if roa else 'No data available'}%\n"
        report += f"Debt-to-Equity Ratio: {round(debt_to_equity, 2) if debt_to_equity else 'No data available'}\n"
        report += f"Current Ratio: {round(current_ratio, 2) if current_ratio else 'No data available'}\n"
        report += f"Gross Margin: {round(gross_margin * 100, 2) if gross_margin else 'No data available'}%\n"
        report += f"Operating Margin: {round(operating_margin * 100, 2) if operating_margin else 'No data available'}%\n"
        report += f"Profit Margin: {round(profit_margin * 100, 2) if profit_margin else 'No data available'}%\n"
        report += f"Dividend Yield: {round(dividend_yield * 100, 2) if dividend_yield else 'No data available'}%\n"
        report += f"P/B Ratio: {format_number(stock.info.get('priceToBook', None), is_currency=False)}\n"
        report += f"\n**Conclusion:**\n{overall_assessment}\n"
        report += f"\n**Data Used for Calculations:**\n"
        report += f"Net Income: {format_number(net_income)}, Total Assets: {format_number(total_assets)}, "
        report += f"Total Equity: {format_number(total_equity)}\n"
        report += f"Total Debt: {format_number(total_debt)}, Current Assets: {format_number(current_assets)}, "
        report += f"Current Liabilities: {format_number(current_liabilities)}\n"
        report += f"Revenue: {format_number(revenue)}, Operating Income: {format_number(operating_income)}"

    return report
