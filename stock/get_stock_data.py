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
    # Get balance sheet and income statement data
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

    # Calculate and format key metrics
    pe_ratio = round(stock.info.get('trailingPE', 0), 2) if stock.info.get('trailingPE') else None
    forward_pe = round(stock.info.get('forwardPE', 0), 2) if stock.info.get('forwardPE') else None
    roe = round((net_income / total_equity) * 100, 2) if total_equity and net_income else None
    roa = round((net_income / total_assets) * 100, 2) if total_assets and net_income else None
    debt_to_equity = round(total_debt / total_equity, 2) if total_equity else None
    current_ratio = round(current_assets / current_liabilities, 2) if current_assets and current_liabilities else None
    gross_margin = round((income_statement.loc["Gross Profit"].iloc[0] / revenue) * 100, 2) if revenue and "Gross Profit" in income_statement.index else None
    operating_margin = round((operating_income / revenue) * 100, 2) if revenue and operating_income else None
    profit_margin = round((net_income / revenue) * 100, 2) if revenue and net_income else None
    dividend_yield = round(stock.info.get('dividendYield', 0) * 100, 2) if stock.info.get('dividendYield') else None
    price_to_book = round(stock.info.get('priceToBook', 0), 2) if stock.info.get('priceToBook') else None

    # Financial analysis assessments
    overvaluation = pe_ratio and pe_ratio > 25
    strong_profitability = roe and roe > 15
    moderate_profitability = roe and 10 < roe <= 15
    weak_profitability = roe and roe <= 10
    strong_balance = debt_to_equity and debt_to_equity < 0.5
    high_debt = debt_to_equity and debt_to_equity > 1.0
    solid_margin = gross_margin and gross_margin > 40
    low_liquidity = current_ratio and current_ratio < 1

    # Generate assessment
    assessment_parts = []

    if language == 'Ukrainian':
        # Оцінка переоцінки
        if overvaluation:
            assessment_parts.append(
                f"Компанія може бути переоціненою (P/E = {pe_ratio}), що збільшує ризик корекції ціни у майбутньому.")
        elif pe_ratio is not None:
            assessment_parts.append(
                f"Ціна акцій (P/E = {pe_ratio}) здається привабливою, що може свідчити про потенційний ріст.")

        # Оцінка прибутковості
        if strong_profitability:
            assessment_parts.append(
                f"Показник рентабельності власного капіталу (ROE = {roe}%) свідчить про високу прибутковість.")
        elif moderate_profitability:
            assessment_parts.append(
                f"ROE (={roe}%) знаходиться на середньому рівні, що свідчить про стабільну, але не видатну прибутковість.")
        elif weak_profitability:
            assessment_parts.append(f"Низький рівень ROE (={roe}%) може бути сигналом слабкої рентабельності.")

        # Оцінка боргового навантаження
        if strong_balance:
            assessment_parts.append(
                f"Баланс компанії виглядає здоровим із низьким співвідношенням боргу до власного капіталу (Debt/Equity = {debt_to_equity}).")
        elif high_debt:
            assessment_parts.append(
                f"Компанія має високе боргове навантаження (Debt/Equity = {debt_to_equity}), що може збільшити фінансові ризики у майбутньому.")

        # Оцінка рентабельності
        if solid_margin:
            assessment_parts.append(
                f"Високий рівень валової маржі (Gross Margin = {gross_margin}%) свідчить про сильну конкурентну позицію.")
        elif gross_margin is not None:
            assessment_parts.append(
                f"Рівень валової маржі (Gross Margin = {gross_margin}%) свідчить про можливі труднощі в управлінні витратами.")

        # Оцінка ліквідності
        if low_liquidity:
            assessment_parts.append(
                f"Низький коефіцієнт поточної ліквідності (Current Ratio = {current_ratio}) може викликати труднощі у покритті короткострокових зобов'язань.")
        elif current_ratio is not None:
            assessment_parts.append(
                f"Компанія має достатньо ресурсів для покриття своїх поточних зобов'язань (Current Ratio = {current_ratio}).")
    else:
        # Overvaluation assessment
        if overvaluation:
            assessment_parts.append(
                f"The company appears overvalued (P/E = {pe_ratio}), increasing the risk of a future price correction.")
        elif pe_ratio is not None:
            assessment_parts.append(
                f"The stock price (P/E = {pe_ratio}) seems attractive, indicating potential growth opportunities.")

        # Profitability assessment
        if strong_profitability:
            assessment_parts.append(
                f"The ROE (={roe}%) indicates strong profitability, a positive signal for investors.")
        elif moderate_profitability:
            assessment_parts.append(
                f"The ROE (={roe}%) is at a moderate level, indicating stable but not exceptional profitability.")
        elif weak_profitability:
            assessment_parts.append(
                f"A low ROE (={roe}%) might indicate weaker profitability compared to industry standards.")

        # Debt load assessment
        if strong_balance:
            assessment_parts.append(
                f"The company's balance sheet is healthy, with a low debt-to-equity ratio (Debt/Equity = {debt_to_equity}).")
        elif high_debt:
            assessment_parts.append(
                f"The company has a high debt burden (Debt/Equity = {debt_to_equity}), which could pose financial risks in the long term.")

        # Margin assessment
        if solid_margin:
            assessment_parts.append(
                f"A high gross margin (Gross Margin = {gross_margin}%) indicates a strong competitive position in the market.")
        elif gross_margin is not None:
            assessment_parts.append(
                f"The gross margin (Gross Margin = {gross_margin}%) suggests potential challenges in managing costs efficiently.")

        # Liquidity assessment
        if low_liquidity:
            assessment_parts.append(
                f"Low current ratio (Current Ratio = {current_ratio}) may indicate challenges in covering short-term liabilities.")
        elif current_ratio is not None:
            assessment_parts.append(
                f"The company appears well-positioned to meet its short-term obligations (Current Ratio = {current_ratio}).")

    overall_assessment = " ".join(assessment_parts)

    # Generate report based on the selected language
    report = f"**Company Overview: {stock.info.get('longName', 'N/A')} ({ticker})**\n"
    report += f"Sector: {stock.info.get('sector', 'N/A')}\n"
    report += f"Industry: {stock.info.get('industry', 'N/A')}\n"
    report += f"Report Date: {report_date}\n"
    report += f"Official Website: {stock.info.get('website', 'No data available')}\n"
    report += f"\n**Financial Metrics:**\n"
    if pe_ratio is not None:
        report += f"P/E Ratio: {format_number(pe_ratio, is_currency=False)}\n"
    if forward_pe is not None:
        report += f"Forward P/E: {format_number(forward_pe, is_currency=False)}\n"
    if roe is not None:
        report += f"ROE: {roe}%\n"
    if roa is not None:
        report += f"ROA: {roa}%\n"
    if debt_to_equity is not None:
        report += f"Debt-to-Equity Ratio: {debt_to_equity}\n"
    if current_ratio is not None:
        report += f"Current Ratio: {current_ratio}\n"
    if gross_margin is not None:
        report += f"Gross Margin: {gross_margin}%\n"
    if operating_margin is not None:
        report += f"Operating Margin: {operating_margin}%\n"
    if profit_margin is not None:
        report += f"Profit Margin: {profit_margin}%\n"
    if dividend_yield is not None:
        report += f"Dividend Yield: {dividend_yield}%\n"
    if price_to_book is not None:
        report += f"P/B Ratio: {format_number(price_to_book, is_currency=False)}\n"

    report += f"\n**Conclusion:**\n{overall_assessment}\n"
    report += f"\n**Data Used for Calculations:**\n"
    report += f"Net Income: {format_number(net_income)}, Total Assets: {format_number(total_assets)}, "
    report += f"Total Equity: {format_number(total_equity)}\n"
    report += f"Total Debt: {format_number(total_debt)}, Current Assets: {format_number(current_assets)}, "
    report += f"Current Liabilities: {format_number(current_liabilities)}\n"
    report += f"Revenue: {format_number(revenue)}, Operating Income: {format_number(operating_income)}"

    return report
