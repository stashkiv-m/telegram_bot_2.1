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
    cashflow = stock.quarterly_cashflow
    dividends = stock.dividends
    dividends.index = dividends.index.tz_localize(None)

    report_date = pd.to_datetime(balance_sheet.columns[0]).date() if not balance_sheet.empty else "N/A"
    net_income = income_statement.loc["Net Income"].iloc[0] if "Net Income" in income_statement.index else None
    total_assets = balance_sheet.loc["Total Assets"].iloc[0] if "Total Assets" in balance_sheet.index else None
    total_equity = balance_sheet.loc["Stockholders Equity"].iloc[
        0] if "Stockholders Equity" in balance_sheet.index else None
    total_debt = (
                     balance_sheet.loc["Long Term Debt"].iloc[0] if "Long Term Debt" in balance_sheet.index else 0
                 ) + (
                     balance_sheet.loc["Current Debt"].iloc[0] if "Current Debt" in balance_sheet.index else 0
                 )
    revenue = income_statement.loc["Total Revenue"].iloc[0] if "Total Revenue" in income_statement.index else None
    gross_profit = income_statement.loc["Gross Profit"].iloc[0] if "Gross Profit" in income_statement.index else None
    operating_income = income_statement.loc["Operating Income"].iloc[
        0] if "Operating Income" in income_statement.index else None
    current_assets = balance_sheet.loc["Current Assets"].iloc[0] if "Current Assets" in balance_sheet.index else None
    current_liabilities = balance_sheet.loc["Current Liabilities"].iloc[
        0] if "Current Liabilities" in balance_sheet.index else None
    cash_from_operations = cashflow.loc["Total Cash From Operating Activities"].iloc[
        0] if "Total Cash From Operating Activities" in cashflow.index else None

    # Calculate and format key metrics
    pe_ratio = round(stock.info.get('trailingPE', 0), 2) if stock.info.get('trailingPE') else None
    price_to_sales = round(stock.info.get('priceToSalesTrailing12Months', 0), 2) if stock.info.get(
        'priceToSalesTrailing12Months') else None
    price_to_cash_flow = round(stock.info.get('priceToCashFlow', 0), 2) if stock.info.get('priceToCashFlow') else None
    price_to_book = round(stock.info.get('priceToBook', 0), 2) if stock.info.get('priceToBook') else None
    forward_pe = round(stock.info.get('forwardPE', 0), 2) if stock.info.get('forwardPE') else None
    roe = round((net_income / total_equity) * 100, 2) if total_equity and net_income else None
    roa = round((net_income / total_assets) * 100, 2) if total_assets and net_income else None
    debt_to_equity = round(total_debt / total_equity, 2) if total_equity else None
    current_ratio = round(current_assets / current_liabilities, 2) if current_assets and current_liabilities else None
    quick_ratio = round((current_assets - balance_sheet.loc["Inventory"].iloc[0]) / current_liabilities,
                        2) if "Inventory" in balance_sheet.index and current_liabilities else None
    gross_margin = round((gross_profit / revenue) * 100, 2) if revenue and gross_profit else None
    operating_margin = round((operating_income / revenue) * 100, 2) if revenue and operating_income else None
    profit_margin = round((net_income / revenue) * 100, 2) if revenue and net_income else None
    dividend_yield = round(stock.info.get('dividendYield', 0) * 100, 2) if stock.info.get('dividendYield') else None
    asset_turnover = round(revenue / total_assets, 2) if revenue and total_assets else None
    inventory_turnover = round(revenue / balance_sheet.loc["Inventory"].iloc[0],
                               2) if "Inventory" in balance_sheet.index and revenue else None
    receivable_turnover = round(revenue / balance_sheet.loc["Net Receivables"].iloc[0],
                                2) if "Net Receivables" in balance_sheet.index and revenue else None

    # Short assessments for each metric
    short_assessments = {
        "P/E Ratio": f"{format_number(pe_ratio)}" if pe_ratio else "N/A",
        "Price to Sales": f"{format_number(price_to_sales, False)}" if price_to_sales else "N/A",
        "Price to Cash Flow": f"{format_number(price_to_cash_flow, False)}" if price_to_cash_flow else "N/A",
        "Price to Book": f"{format_number(price_to_book, False)}" if price_to_book else "N/A",
        "Forward P/E": f"{format_number(forward_pe, False)}" if forward_pe else "N/A",
        "ROE": f"{roe}%" if roe else "N/A",
        "ROA": f"{roa}%" if roa else "N/A",
        "Debt-to-Equity": f"{debt_to_equity}" if debt_to_equity else "N/A",
        "Current Ratio": f"{current_ratio}" if current_ratio else "N/A",
        "Quick Ratio": f"{quick_ratio}" if quick_ratio else "N/A",
        "Gross Margin": f"{gross_margin}%" if gross_margin else "N/A",
        "Operating Margin": f"{operating_margin}%" if operating_margin else "N/A",
        "Profit Margin": f"{profit_margin}%" if profit_margin else "N/A",
        "Dividend Yield": f"{dividend_yield}%" if dividend_yield else "N/A",
        "Asset Turnover": f"{asset_turnover}" if asset_turnover else "N/A",
        "Inventory Turnover": f"{inventory_turnover}" if inventory_turnover else "N/A",
        "Receivable Turnover": f"{receivable_turnover}" if receivable_turnover else "N/A"
    }

    # Generate report
    report = f"**Company Overview: {stock.info.get('longName', 'N/A')} ({ticker})**\n"
    report += f"Sector: {stock.info.get('sector', 'N/A')}\n"
    report += f"Industry: {stock.info.get('industry', 'N/A')}\n"
    report += f"Report Date: {report_date}\n"
    report += f"Official Website: {stock.info.get('website', 'No data available')}\n"
    report += f"\n**Financial Metrics:**\n"
    for key, value in short_assessments.items():
        if value != "N/A":
            report += f"{key}: {value}\n"

    return report






