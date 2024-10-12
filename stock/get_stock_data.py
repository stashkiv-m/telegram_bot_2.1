

def get_stock_metrics(stock, ticker):
    try:
        info = stock.info
        metrics = {
            "Company Name": info.get("longName", "No data available"),
            "Ticker": ticker,
            "Sector": info.get("sector", "No data available"),
            "Industry": info.get("industry", "No data available"),
            "Current Price": info.get("currentPrice", "No data available"),
            "Market Cap": info.get("marketCap", "No data available"),
            "Enterprise Value": info.get("enterpriseValue", "No data available"),
            "Trailing P/E": info.get("trailingPE", "No data available"),
            "Forward P/E": info.get("forwardPE", "No data available"),
            "Price to Book": info.get("priceToBook", "No data available"),
            "Return on Equity (ROE)": info.get("returnOnEquity", "No data available"),
            "Return on Assets (ROA)": info.get("returnOnAssets", "No data available"),
            "Debt to Equity": info.get("debtToEquity", "No data available"),
            "Current Ratio": info.get("currentRatio", "No data available"),
            "Dividend Yield": "{:.2f}%".format(info.get("dividendYield", 0) * 100) if info.get(
                "dividendYield") is not None else "No data available",
            "Payout Ratio": "{:.2f}%".format(info.get("payoutRatio", 0) * 100) if info.get(
                "payoutRatio") is not None else "No data available",
            "Gross Margin": "{:.2f}%".format(info.get("grossMargins", 0) * 100) if info.get(
                "grossMargins") is not None else "No data available",
            "Operating Margin": "{:.2f}%".format(info.get("operatingMargins", 0) * 100) if info.get(
                "operatingMargins") is not None else "No data available",
            "Profit Margin": "{:.2f}%".format(info.get("profitMargins", 0) * 100) if info.get(
                "profitMargins") is not None else "No data available",
            "Website": info.get("website", "No website available")

        }
        output = f"**Company Overview: {metrics['Company Name']} ({metrics['Ticker']})**\n"
        output += f"Sector: {metrics['Sector']}\n"
        output += f"Industry: {metrics['Industry']}\n\n"
        output += f"\nOfficial Website: {metrics['Website']}\n"

        for metric, value in metrics.items():
            if metric in ["Company Name", "Sector", "Industry"]:
                continue
            try:
                if metric == "Current Price":
                    output += f"Current price: ${value:.2f}.\n"
                elif metric == "Market Cap":
                    output += f"Market cap: ${value / 1e9:.2f}B.\n"
                elif metric == "Enterprise Value":
                    output += f"Enterprise value: ${value / 1e9:.2f}B.\n"
                elif metric == "Trailing P/E":
                    if value < 15:
                        output += f"Trailing P/E: {value:.2f} (undervalued).\n"
                    elif value > 25:
                        output += f"Trailing P/E: {value:.2f} (overvalued).\n"
                    else:
                        output += f"Trailing P/E: {value:.2f} (fairly valued).\n"
                elif metric == "Forward P/E":
                    if value < 15:
                        output += f"Forward P/E: {value:.2f} (potentially undervalued).\n"
                    elif value > 25:
                        output += f"Forward P/E: {value:.2f} (potentially overvalued).\n"
                    else:
                        output += f"Forward P/E: {value:.2f} (fairly valued).\n"
                elif metric == "Price to Book":
                    if value < 1:
                        output += f"P/B ratio: {value:.2f} (undervalued).\n"
                    elif value > 3:
                        output += f"P/B ratio: {value:.2f} (overvalued).\n"
                    else:
                        output += f"P/B ratio: {value:.2f} (fairly valued).\n"
                elif metric == "Return on Equity (ROE)":
                    value = value * 100
                    if value < 10:
                        output += f"ROE: {value:.2f}% (low).\n"
                    elif value > 20:
                        output += f"ROE: {value:.2f}% (high).\n"
                    else:
                        output += f"ROE: {value:.2f}% (moderate).\n"
                elif metric == "Return on Assets (ROA)":
                    value = value * 100
                    if value < 5:
                        output += f"ROA: {value:.2f}% (low).\n"
                    elif value > 15:
                        output += f"ROA: {value:.2f}% (high).\n"
                    else:
                        output += f"ROA: {value:.2f}% (moderate).\n"
                elif metric == "Debt to Equity":
                    if value < 0.5:
                        output += f"D/E ratio: {value:.2f} (low risk).\n"
                    elif value > 2:
                        output += f"D/E ratio: {value:.2f} (high risk).\n"
                    else:
                        output += f"D/E ratio: {value:.2f} (moderate).\n"
                elif metric == "Current Ratio":
                    if value < 1:
                        output += f"Current ratio: {value:.2f} (potential liquidity issues).\n"
                    elif value > 2:
                        output += f"Current ratio: {value:.2f} (strong liquidity).\n"
                    else:
                        output += f"Current ratio: {value:.2f} (healthy liquidity).\n"
                elif metric == "Dividend Yield":
                    if value == "No data available":
                        output += f"No dividends.\n"
                    elif float(value[:-1]) < 2:
                        output += f"Dividend yield: {value} (low).\n"
                    elif float(value[:-1]) > 5:
                        output += f"Dividend yield: {value} (high).\n"
                    else:
                        output += f"Dividend yield: {value} (moderate).\n"
                elif metric == "Payout Ratio":
                    if value == "No data available":
                        output += f"Payout ratio data not available.\n"
                    elif float(value[:-1]) < 30:
                        output += f"Payout ratio: {value} (low).\n"
                    elif float(value[:-1]) > 50:
                        output += f"Payout ratio: {value} (high).\n"
                    else:
                        output += f"Payout ratio: {value} (sustainable).\n"
                elif metric == "Gross Margin":
                    if value == "No data available":
                        output += f"Gross margin data not available.\n"
                    elif float(value[:-1]) < 20:
                        output += f"Gross margin: {value} (low).\n"
                    elif float(value[:-1]) > 40:
                        output += f"Gross margin: {value} (high).\n"
                    else:
                        output += f"Gross margin: {value} (average).\n"
                elif metric == "Operating Margin":
                    if value == "No data available":
                        output += f"Operating margin data not available.\n"
                    elif float(value[:-1]) < 10:
                        output += f"Operating margin: {value} (low).\n"
                    elif float(value[:-1]) > 20:
                        output += f"Operating margin: {value} (high).\n"
                    else:
                        output += f"Operating margin: {value} (moderate).\n"
                elif metric == "Profit Margin":
                    if value == "No data available":
                        output += f"Profit margin data not available.\n"
                    elif float(value[:-1]) < 5:
                        output += f"Profit margin: {value} (low).\n"
                    elif float(value[:-1]) > 15:
                        output += f"Profit margin: {value} (high).\n"
                    else:
                        output += f"Profit margin: {value} (moderate).\n"
            except TypeError:
                output += f"{metric}: {value}\n"

        output += "\n**Summary:**\n"
        output += "Based on the fundamental metrics, the company shows the following financial health indicators:\n"

        try:
            if metrics["Trailing P/E"] != "No data available" and metrics["Forward P/E"] != "No data available":
                if metrics["Trailing P/E"] < 15 and metrics["Forward P/E"] < 15:
                    output += (
                        "The company's valuation appears to be undervalued based on its P/E ratios, suggesting potential "
                        "for price appreciation.\n")
                elif metrics["Trailing P/E"] > 25 and metrics["Forward P/E"] > 25:
                    output += (
                        "The company's valuation appears to be overvalued based on its P/E ratios, indicating potential "
                        "risk of price correction.\n")
                else:
                    output += (
                        "The company's valuation appears to be fairly valued based on its P/E ratios, suggesting a stable "
                        "price outlook.\n")

            if metrics["Return on Equity (ROE)"] != "No data available":
                if metrics["Return on Equity (ROE)"] > 0.15:
                    output += (
                        "The company demonstrates strong profitability with a high ROE, indicating efficient use of equity "
                        "capital.\n")
                else:
                    output += (
                        "The company shows lower profitability based on its ROE, which could indicate inefficiencies in "
                        "using equity capital.\n")

            if metrics["Debt to Equity"] != "No data available":
                if metrics["Debt to Equity"] < 0.5:
                    output += "The company's balance sheet appears strong with low leverage, reducing financial risk.\n"
                elif metrics["Debt to Equity"] > 2:
                    output += (
                        "The company carries a high level of debt, which may pose a risk during economic downturns or "
                        "periods of high-interest rates.\n")
                else:
                    output += ("The company's balance sheet shows moderate leverage, indicating a balanced approach to "
                               "debt management.\n")
        except Exception as e:
            output += f"Error in Summary: {e}\n"

        output += "\n**Overall Assessment:**\n"
        try:
            if metrics["Trailing P/E"] < 15 and metrics["Return on Equity (ROE)"] > 0.15 and metrics[
                "Debt to Equity"] < 0.5:
                output += (
                    "Based on its low valuation, high profitability, and strong balance sheet, the company appears to be a "
                    "solid investment opportunity.")
            else:
                output += (
                    "Considering its current valuation, profitability, and balance sheet, the company presents a "
                    "balanced investment opportunity with moderate risks.")
        except Exception as e:
            output += f"Error in Overall Assessment: {e}\n"

        return output
    except Exception as e:
        return f"Error retrieving data for {ticker}: {e}"

