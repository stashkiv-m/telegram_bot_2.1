import yfinance as yf
import pandas as pd

import yfinance as yf
import pandas as pd

def calculate_financial_ratios(symbol, report_type='Quarterly'):
    try:
        stock = yf.Ticker(symbol)
        print(f"\nFetching data for {symbol}...")

        # Вибір даних на основі типу звіту
        balance_sheet = stock.quarterly_balance_sheet if report_type == 'Quarterly' else stock.balance_sheet
        financials = stock.quarterly_financials if report_type == 'Quarterly' else stock.financials
        cashflow = stock.quarterly_cashflow if report_type == 'Quarterly' else stock.cashflow

        # Отримуємо дані
        net_income = financials.loc['Net Income'].iloc[0] if 'Net Income' in financials.index else None
        total_equity = balance_sheet.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in balance_sheet.index else None
        total_assets = balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in balance_sheet.index else None
        long_term_debt = balance_sheet.loc['Long Term Debt'].iloc[0] if 'Long Term Debt' in balance_sheet.index else None
        total_debt = long_term_debt + balance_sheet.loc['Current Debt'].iloc[0] if 'Current Debt' in balance_sheet.index else long_term_debt
        current_assets = balance_sheet.loc['Current Assets'].iloc[0] if 'Current Assets' in balance_sheet.index else None
        current_liabilities = balance_sheet.loc['Current Liabilities'].iloc[0] if 'Current Liabilities' in balance_sheet.index else None
        revenue = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials.index else None
        operating_income = financials.loc['Operating Income'].iloc[0] if 'Operating Income' in financials.index else None
        gross_profit = financials.loc['Gross Profit'].iloc[0] if 'Gross Profit' in financials.index else None
        ebit = operating_income if operating_income else None
        pre_tax_income = financials.loc['Pretax Income'].iloc[0] if 'Pretax Income' in financials.index else None
        ebitda = financials.loc['EBITDA'].iloc[0] if 'EBITDA' in financials.index else None
        cash_from_operations = cashflow.loc['Total Cash From Operating Activities'].iloc[0] if 'Total Cash From Operating Activities' in cashflow.index else None
        inventory = balance_sheet.loc['Inventory'].iloc[0] if 'Inventory' in balance_sheet.index else None
        receivables = balance_sheet.loc['Net Receivables'].iloc[0] if 'Net Receivables' in balance_sheet.index else None
        intangible_assets = balance_sheet.loc['Intangible Assets'].iloc[0] if 'Intangible Assets' in balance_sheet.index else 0
        shares_outstanding = stock.info.get('sharesOutstanding')
        market_cap = stock.info.get('marketCap')
        cash = balance_sheet.loc['Cash'].iloc[0] if 'Cash' in balance_sheet.index else None

        # Розрахунок показників
        pe_ratio = market_cap / net_income if market_cap and net_income else None
        ps_ratio = market_cap / revenue if market_cap and revenue else None
        price_to_cash_flow = market_cap / cash_from_operations if market_cap and cash_from_operations else None
        pb_ratio = market_cap / total_equity if market_cap and total_equity else None
        enterprise_value = market_cap + total_debt - cash if market_cap and total_debt and cash else None
        ev_to_ebitda = enterprise_value / ebitda if enterprise_value and ebitda else None
        roe = (net_income / total_equity) * 100 if net_income and total_equity else None
        roa = (net_income / total_assets) * 100 if net_income and total_assets else None
        gross_margin = (gross_profit / revenue) * 100 if gross_profit and revenue else None
        operating_margin = (operating_income / revenue) * 100 if operating_income and revenue else None
        ebit_margin = (ebit / revenue) * 100 if ebit and revenue else None
        ebitda_margin = (ebitda / revenue) * 100 if ebitda and revenue else None
        net_margin = (net_income / revenue) * 100 if net_income and revenue else None
        pre_tax_margin = (pre_tax_income / revenue) * 100 if pre_tax_income and revenue else None
        current_ratio = current_assets / current_liabilities if current_assets and current_liabilities else None
        quick_ratio = (current_assets - inventory) / current_liabilities if inventory and current_liabilities else None
        inventory_turnover = financials.loc['Cost of Revenue'].iloc[0] / inventory if 'Cost of Revenue' in financials.index and inventory else None
        receivable_turnover = revenue / receivables if revenue and receivables else None
        days_sales_in_receivables = 365 / receivable_turnover if receivable_turnover else None
        debt_to_assets = total_debt / total_assets if total_debt and total_assets else None
        debt_to_equity = total_debt / total_equity if total_debt and total_equity else None
        long_term_debt_to_assets = long_term_debt / total_assets if long_term_debt and total_assets else None
        long_term_debt_to_equity = long_term_debt / total_equity if long_term_debt and total_equity else None
        asset_turnover = revenue / total_assets if revenue and total_assets else None
        roi = (net_income / (total_assets + total_debt)) * 100 if net_income and total_assets and total_debt else None
        return_on_tangible_equity = (net_income / (total_equity - intangible_assets)) * 100 if net_income and total_equity and intangible_assets else None
        book_value_per_share = total_equity / shares_outstanding if total_equity and shares_outstanding else None
        operating_cash_flow_per_share = cash_from_operations / shares_outstanding if cash_from_operations and shares_outstanding else None
        free_cash_flow_per_share = cash_from_operations / shares_outstanding if cash_from_operations and shares_outstanding else None

        # Створення структури даних
        data = {
            'Ticker': symbol,
            'Market Cap': market_cap,
            'PE Ratio': pe_ratio,
            'PS Ratio': ps_ratio,
            'Price to Cash Flow': price_to_cash_flow,
            'PB Ratio': pb_ratio,
            'Enterprise Value': enterprise_value,
            'EV to EBITDA': ev_to_ebitda,
            'ROE (%)': roe,
            'ROA (%)': roa,
            'Gross Margin (%)': gross_margin,
            'Operating Margin (%)': operating_margin,
            'EBIT Margin (%)': ebit_margin,
            'EBITDA Margin (%)': ebitda_margin,
            'Net Margin (%)': net_margin,
            'Pre-Tax Profit Margin (%)': pre_tax_margin,
            'Current Ratio': current_ratio,
            'Quick Ratio': quick_ratio,
            'Inventory Turnover': inventory_turnover,
            'Receivable Turnover': receivable_turnover,
            'Days Sales in Receivables': days_sales_in_receivables,
            'Debt to Assets': debt_to_assets,
            'Debt to Equity': debt_to_equity,
            'Long Term Debt to Assets': long_term_debt_to_assets,
            'Long Term Debt to Equity': long_term_debt_to_equity,
            'Asset Turnover': asset_turnover,
            'ROI (%)': roi,
            'Return on Tangible Equity (%)': return_on_tangible_equity,
            'Book Value Per Share': book_value_per_share,
            'Operating Cash Flow Per Share': operating_cash_flow_per_share,
            'Free Cash Flow Per Share': free_cash_flow_per_share,
            'Report Type': report_type,
            'Net Income': net_income,
            'Total Equity': total_equity,
            'Total Assets': total_assets,
            'Total Debt': total_debt,
            'Revenue': revenue,
            'Operating Income': operating_income,
            'Gross Profit': gross_profit,
            'Cash from Operations': cash_from_operations,
            'EBITDA': ebitda,
            'Cash': cash
        }

        print(f"Data calculated for {symbol}.")
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def process_stock_list(input_csv_path, output_csv_path):
    # Зчитуємо список тикерів з файлу CSV
    df = pd.read_csv(input_csv_path)
    tickers = df['Ticker']

    # Збираємо результати для кожного тикера
    results = []
    for ticker in tickers:
        print(f"Processing {ticker}...")
        data = calculate_financial_ratios(ticker, report_type='Quarterly')
        if data:
            results.append(data)

    # Створюємо DataFrame з результатами та зберігаємо у новий CSV-файл
    results_df = pd.DataFrame(results)
    # Фільтруємо колонки, які дійсно присутні в DataFrame
    available_columns = [col for col in results_df.columns if col in results_df]
    results_df = results_df[available_columns]
    results_df.to_csv(output_csv_path, index=False)
    print(f"\nData saved to {output_csv_path}")

# Використання функції
input_csv_path = r"C:\Users\Mykhailo\PycharmProjects\telegram_bot_2.1\developer_functions\stock_dev\stock_list.csv"
output_csv_path = r"C:\Users\Mykhailo\PycharmProjects\telegram_bot_2.1\developer_functions\stock_dev\stock_fundamental_data.csv"
process_stock_list(input_csv_path, output_csv_path)
