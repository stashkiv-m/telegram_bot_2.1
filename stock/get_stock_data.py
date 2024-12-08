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
        "P/E Ratio": f"{format_number(pe_ratio, False)} (Overvalued)" if pe_ratio and pe_ratio > 25 else f"{format_number(pe_ratio, False)} (Undervalued)" if pe_ratio else "N/A",
        "Price to Sales": f"{format_number(price_to_sales, False)} (High)" if price_to_sales and price_to_sales > 2 else f"{format_number(price_to_sales, False)} (Low)" if price_to_sales else "N/A",
        "Price to Cash Flow": f"{format_number(price_to_cash_flow, False)} (High)" if price_to_cash_flow and price_to_cash_flow > 15 else f"{format_number(price_to_cash_flow, False)} (Low)" if price_to_cash_flow else "N/A",
        "Price to Book": f"{format_number(price_to_book, False)} (High)" if price_to_book and price_to_book > 1 else f"{format_number(price_to_book, False)} (Low)" if price_to_book else "N/A",
        "Forward P/E": f"{format_number(forward_pe, False)} (Overvalued)" if forward_pe and forward_pe > 20 else f"{format_number(forward_pe, False)} (Undervalued)" if forward_pe else "N/A",
        "ROE": f"{roe}% (High)" if roe and roe > 15 else f"{roe}% (Moderate)" if roe and 10 <= roe <= 15 else f"{roe}% (Low)" if roe else "N/A",
        "ROA": f"{roa}% (High)" if roa and roa > 10 else f"{roa}% (Low)" if roa else "N/A",
        "Debt-to-Equity": f"{debt_to_equity} (High Risk)" if debt_to_equity and debt_to_equity > 1.0 else f"{debt_to_equity} (Low Risk)" if debt_to_equity else "N/A",
        "Current Ratio": f"{current_ratio} (Liquid)" if current_ratio and current_ratio >= 1 else f"{current_ratio} (Illiquid)" if current_ratio else "N/A",
        "Quick Ratio": f"{quick_ratio} (Strong)" if quick_ratio and quick_ratio >= 1 else f"{quick_ratio} (Weak)" if quick_ratio else "N/A",
        "Gross Margin": f"{gross_margin}% (Strong)" if gross_margin and gross_margin > 40 else f"{gross_margin}% (Average)" if gross_margin else "N/A",
        "Operating Margin": f"{operating_margin}% (Strong)" if operating_margin and operating_margin > 20 else f"{operating_margin}% (Average)" if operating_margin else "N/A",
        "Profit Margin": f"{profit_margin}% (High)" if profit_margin and profit_margin > 10 else f"{profit_margin}% (Low)" if profit_margin else "N/A",
        "Dividend Yield": f"{dividend_yield}% (High)" if dividend_yield and dividend_yield > 3 else f"{dividend_yield}% (Low)" if dividend_yield else "N/A",
        "Asset Turnover": f"{asset_turnover} (Efficient)" if asset_turnover and asset_turnover > 1 else f"{asset_turnover} (Inefficient)" if asset_turnover else "N/A",
        "Inventory Turnover": f"{inventory_turnover} (High)" if inventory_turnover and inventory_turnover > 5 else f"{inventory_turnover} (Low)" if inventory_turnover else "N/A",
        "Receivable Turnover": f"{receivable_turnover} (High)" if receivable_turnover and receivable_turnover > 5 else f"{receivable_turnover} (Low)" if receivable_turnover else "N/A"
    }

    # Dynamic conclusion based on all indicators
    conclusion = get_dynamic_conclusion(
        short_assessments,
        net_income,
        total_debt,
        roe,
        gross_margin,
        dividend_yield,
        language
    )

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

    report += f"\n**Conclusion:**\n{conclusion}\n"
    report += f"Net Income: {format_number(net_income)}, Total Assets: {format_number(total_assets)}, "
    report += f"Total Equity: {format_number(total_equity)}\n"
    report += f"Total Debt: {format_number(total_debt)}, Current Assets: {format_number(current_assets)}, "
    report += f"Current Liabilities: {format_number(current_liabilities)}\n"
    report += f"Revenue: {format_number(revenue)}, Operating Income: {format_number(operating_income)}"

    return report


def get_dynamic_conclusion(
    short_assessments, net_income, total_debt, roe, gross_margin, dividend_yield, language='English'
):
    high_profitability = "High" in short_assessments['ROE']
    moderate_profitability = "Moderate" in short_assessments['ROE']
    low_profitability = "Low" in short_assessments['ROE']
    high_debt = "High Risk" in short_assessments['Debt-to-Equity']
    low_debt = "Low Risk" in short_assessments['Debt-to-Equity']
    strong_liquidity = "High" in short_assessments['Current Ratio']
    average_liquidity = "Moderate" in short_assessments['Current Ratio']
    low_liquidity = "Low" in short_assessments['Current Ratio']
    attractive_dividends = "High" in short_assessments['Dividend Yield']
    moderate_dividends = "Moderate" in short_assessments['Dividend Yield']
    low_valuation = "Undervalued" in short_assessments['P/E Ratio'] and "Low" in short_assessments['Price to Book']

    # Висновок залежить від мови
    if language == 'Ukrainian':
        conclusion = []

        # Оцінка прибутковості (ROE)
        if high_profitability:
            conclusion.append(
                f"Компанія має високу прибутковість з рентабельністю власного капіталу (ROE) на рівні {roe}%, що показує ефективне використання капіталу."
            )
        elif moderate_profitability:
            conclusion.append(
                f"Рентабельність власного капіталу (ROE) становить {roe}%, що свідчить про стабільну прибутковість, хоча і не надто високу."
            )
        elif low_profitability:
            conclusion.append(
                f"Рентабельність власного капіталу (ROE) на рівні {roe}% є низькою, що може вказувати на обмежену прибутковість компанії."
            )

        # Оцінка боргу
        if high_debt:
            conclusion.append(
                f"Компанія має високий рівень боргу ({format_number(total_debt)}), що підвищує ризики та може вплинути на її фінансову стабільність."
            )
        elif low_debt:
            conclusion.append(
                f"Борг компанії є низьким, що сприяє зниженню фінансових ризиків та підтримці стабільності."
            )

        # Оцінка ліквідності
        if strong_liquidity:
            conclusion.append(
                "Компанія має високу ліквідність, що дозволяє їй швидко покривати короткострокові зобов'язання."
            )
        elif average_liquidity:
            conclusion.append(
                "Ліквідність компанії знаходиться на середньому рівні, що забезпечує достатню фінансову гнучкість."
            )
        elif low_liquidity:
            conclusion.append(
                "Низька ліквідність може обмежувати можливості компанії у виплаті поточних зобов'язань."
            )

        # Валовий прибуток
        if gross_margin:
            conclusion.append(
                f"Валовий прибуток компанії становить {gross_margin}%, що свідчить про {'високу' if gross_margin > 40 else 'середню' if gross_margin > 20 else 'низьку'} ефективність у контролі над витратами."
            )

        # Дивідендна дохідність
        if attractive_dividends:
            conclusion.append(
                f"Висока дивідендна дохідність ({dividend_yield}%) є привабливою для інвесторів, які шукають стабільний дохід."
            )
        elif moderate_dividends:
            conclusion.append(
                f"Помірна дивідендна дохідність ({dividend_yield}%) може зацікавити інвесторів, але не є дуже високою."
            )
        else:
            conclusion.append(
                "Дивідендна дохідність відсутня або дуже низька, що може не задовольняти інвесторів, які шукають дохід від дивідендів."
            )

        # Оцінка вартості
        if low_valuation:
            conclusion.append(
                "Акції компанії недооцінені, що може представляти вигідну інвестиційну можливість."
            )

        return " ".join(conclusion)

    else:  # English as default
        conclusion = []

        # Profitability assessment (ROE)
        if high_profitability:
            conclusion.append(
                f"The company shows high profitability, with a return on equity (ROE) of {roe}%, indicating effective capital use."
            )
        elif moderate_profitability:
            conclusion.append(
                f"The return on equity (ROE) is {roe}%, reflecting moderate profitability, stable yet not rapid."
            )
        elif low_profitability:
            conclusion.append(
                f"The return on equity (ROE) of {roe}% is low, potentially indicating limited profitability."
            )

        # Debt assessment
        if high_debt:
            conclusion.append(
                f"The company has a high debt level ({format_number(total_debt)}), increasing financial risks and possibly affecting stability."
            )
        elif low_debt:
            conclusion.append(
                f"The company has low debt, which reduces financial risk and supports stability."
            )

        # Liquidity assessment
        if strong_liquidity:
            conclusion.append(
                "The company has high liquidity, allowing it to quickly cover short-term obligations."
            )
        elif average_liquidity:
            conclusion.append(
                "The company's liquidity is moderate, providing adequate financial flexibility."
            )
        elif low_liquidity:
            conclusion.append(
                "Low liquidity may limit the company's ability to meet current obligations."
            )

        # Gross margin assessment
        if gross_margin:
            conclusion.append(
                f"The company's gross margin is {gross_margin}%, indicating {'high' if gross_margin > 40 else 'average' if gross_margin > 20 else 'low'} cost control efficiency."
            )

        # Dividend yield assessment
        if attractive_dividends:
            conclusion.append(
                f"A high dividend yield ({dividend_yield}%) makes the company appealing for income-seeking investors."
            )
        elif moderate_dividends:
            conclusion.append(
                f"A moderate dividend yield ({dividend_yield}%) may interest investors, though it is not very high."
            )
        else:
            conclusion.append(
                "The dividend yield is absent or very low, which may not satisfy income-focused investors."
            )

        # Valuation
        if low_valuation:
            conclusion.append(
                "The company's stock is considered undervalued, presenting a potentially attractive investment opportunity."
            )

        return " ".join(conclusion)

