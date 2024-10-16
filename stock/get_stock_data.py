def get_stock_metrics(stock, ticker, language='English'):
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

        if language == 'Ukrainian':
            output = f"**Огляд компанії: {metrics['Company Name']} ({metrics['Ticker']})**\n"
            output += f"Сектор: {metrics['Sector']}\n"
            output += f"Індустрія: {metrics['Industry']}\n\n"
            output += f"\nОфіційний вебсайт: {metrics['Website']}\n"
        else:  # English by default
            output = f"**Company Overview: {metrics['Company Name']} ({metrics['Ticker']})**\n"
            output += f"Sector: {metrics['Sector']}\n"
            output += f"Industry: {metrics['Industry']}\n\n"
            output += f"\nOfficial Website: {metrics['Website']}\n"

        for metric, value in metrics.items():
            if metric in ["Company Name", "Sector", "Industry"]:
                continue
            try:
                if metric == "Current Price":
                    if language == 'Ukrainian':
                        output += f"Поточна ціна: ${value:.2f}.\n"
                    else:
                        output += f"Current price: ${value:.2f}.\n"
                elif metric == "Market Cap":
                    if language == 'Ukrainian':
                        output += f"Ринкова капіталізація: ${value / 1e9:.2f} млрд.\n"
                    else:
                        output += f"Market cap: ${value / 1e9:.2f}B.\n"
                elif metric == "Enterprise Value":
                    if language == 'Ukrainian':
                        output += f"Вартість підприємства: ${value / 1e9:.2f} млрд.\n"
                    else:
                        output += f"Enterprise value: ${value / 1e9:.2f}B.\n"
                elif metric == "Trailing P/E":
                    if value < 15:
                        if language == 'Ukrainian':
                            output += f"Trailing P/E: {value:.2f} (недооцінена).\n"
                        else:
                            output += f"Trailing P/E: {value:.2f} (undervalued).\n"
                    elif value > 25:
                        if language == 'Ukrainian':
                            output += f"Trailing P/E: {value:.2f} (переоцінена).\n"
                        else:
                            output += f"Trailing P/E: {value:.2f} (overvalued).\n"
                    else:
                        if language == 'Ukrainian':
                            output += f"Trailing P/E: {value:.2f} (справедливо оцінена).\n"
                        else:
                            output += f"Trailing P/E: {value:.2f} (fairly valued).\n"
                elif metric == "Forward P/E":
                    if value < 15:
                        if language == 'Ukrainian':
                            output += f"Forward P/E: {value:.2f} (потенційно недооцінена).\n"
                        else:
                            output += f"Forward P/E: {value:.2f} (potentially undervalued).\n"
                    elif value > 25:
                        if language == 'Ukrainian':
                            output += f"Forward P/E: {value:.2f} (потенційно переоцінена).\n"
                        else:
                            output += f"Forward P/E: {value:.2f} (potentially overvalued).\n"
                    else:
                        if language == 'Ukrainian':
                            output += f"Forward P/E: {value:.2f} (справедливо оцінена).\n"
                        else:
                            output += f"Forward P/E: {value:.2f} (fairly valued).\n"
                elif metric == "Price to Book":
                    if value < 1:
                        if language == 'Ukrainian':
                            output += f"Ціна до балансової вартості (P/B): {value:.2f} (недооцінена).\n"
                        else:
                            output += f"P/B ratio: {value:.2f} (undervalued).\n"
                    elif value > 3:
                        if language == 'Ukrainian':
                            output += f"Ціна до балансової вартості (P/B): {value:.2f} (переоцінена).\n"
                        else:
                            output += f"P/B ratio: {value:.2f} (overvalued).\n"
                    else:
                        if language == 'Ukrainian':
                            output += f"Ціна до балансової вартості (P/B): {value:.2f} (справедливо оцінена).\n"
                        else:
                            output += f"P/B ratio: {value:.2f} (fairly valued).\n"
                elif metric == "Return on Equity (ROE)":
                    value = value * 100
                    if value < 10:
                        if language == 'Ukrainian':
                            output += f"ROE: {value:.2f}% (низький).\n"
                        else:
                            output += f"ROE: {value:.2f}% (low).\n"
                    elif value > 20:
                        if language == 'Ukrainian':
                            output += f"ROE: {value:.2f}% (високий).\n"
                        else:
                            output += f"ROE: {value:.2f}% (high).\n"
                    else:
                        if language == 'Ukrainian':
                            output += f"ROE: {value:.2f}% (помірний).\n"
                        else:
                            output += f"ROE: {value:.2f}% (moderate).\n"
                elif metric == "Return on Assets (ROA)":
                    value = value * 100
                    if value < 5:
                        if language == 'Ukrainian':
                            output += f"ROA: {value:.2f}% (низький).\n"
                        else:
                            output += f"ROA: {value:.2f}% (low).\n"
                    elif value > 15:
                        if language == 'Ukrainian':
                            output += f"ROA: {value:.2f}% (високий).\n"
                        else:
                            output += f"ROA: {value:.2f}% (high).\n"
                    else:
                        if language == 'Ukrainian':
                            output += f"ROA: {value:.2f}% (помірний).\n"
                        else:
                            output += f"ROA: {value:.2f}% (moderate).\n"
                elif metric == "Debt to Equity":
                    if value < 0.5:
                        if language == 'Ukrainian':
                            output += f"Коефіцієнт боргу до власного капіталу (D/E): {value:.2f} (низький ризик).\n"
                        else:
                            output += f"D/E ratio: {value:.2f} (low risk).\n"
                    elif value > 2:
                        if language == 'Ukrainian':
                            output += f"Коефіцієнт боргу до власного капіталу (D/E): {value:.2f} (високий ризик).\n"
                        else:
                            output += f"D/E ratio: {value:.2f} (high risk).\n"
                    else:
                        if language == 'Ukrainian':
                            output += f"Коефіцієнт боргу до власного капіталу (D/E): {value:.2f} (помірний).\n"
                        else:
                            output += f"D/E ratio: {value:.2f} (moderate).\n"
                elif metric == "Current Ratio":
                    if value < 1:
                        if language == 'Ukrainian':
                            output += f"Коефіцієнт поточної ліквідності: {value:.2f} (можливі проблеми з ліквідністю).\n"
                        else:
                            output += f"Current ratio: {value:.2f} (potential liquidity issues).\n"
                    elif value > 2:
                        if language == 'Ukrainian':
                            output += f"Коефіцієнт поточної ліквідності: {value:.2f} (сильна ліквідність).\n"
                        else:
                            output += f"Current ratio: {value:.2f} (strong liquidity).\n"
                    else:
                        if language == 'Ukrainian':
                            output += f"Коефіцієнт поточної ліквідності: {value:.2f} (здоровий рівень ліквідності).\n"
                        else:
                            output += f"Current ratio: {value:.2f} (healthy liquidity).\n"
                elif metric == "Dividend Yield":
                    if value == "No data available":
                        if language == 'Ukrainian':
                            output += f"Дані про дивіденди недоступні.\n"
                        else:
                            output += f"No dividends.\n"
                    elif float(value[:-1]) < 2:
                        if language == 'Ukrainian':
                            output += f"Дивідендна дохідність: {value} (низька).\n"
                        else:
                            output += f"Dividend yield: {value} (low).\n"
                    elif float(value[:-1]) > 5:
                        if language == 'Ukrainian':
                            output += f"Дивідендна дохідність: {value} (висока).\n"
                        else:
                            output += f"Dividend yield: {value} (high).\n"
                    else:
                        if language == 'Ukrainian':
                            output += f"Дивідендна дохідність: {value} (помірна).\n"
                        else:
                            output += f"Dividend yield: {value} (moderate).\n"
                elif metric == "Payout Ratio":
                    if value == "No data available":
                        if language == 'Ukrainian':
                            output += f"Дані про коефіцієнт виплат недоступні.\n"
                        else:
                            output += f"Payout ratio data not available.\n"
                    elif float(value[:-1]) < 30:
                        if language == 'Ukrainian':
                            output += f"Коефіцієнт виплат: {value} (низький).\n"
                        else:
                            output += f"Payout ratio: {value} (low).\n"
                    elif float(value[:-1]) > 50:
                        if language == 'Ukrainian':
                            output += f"Коефіцієнт виплат: {value} (високий).\n"
                        else:
                            output += f"Payout ratio: {value} (high).\n"
                    else:
                        if language == 'Ukrainian':
                            output += f"Коефіцієнт виплат: {value} (стабільний).\n"
                        else:
                            output += f"Payout ratio: {value} (sustainable).\n"
                elif metric == "Gross Margin":
                    if value == "No data available":
                        if language == 'Ukrainian':
                            output += f"Дані про валову маржу недоступні.\n"
                        else:
                            output += f"Gross margin data not available.\n"
                    elif float(value[:-1]) < 20:
                        if language == 'Ukrainian':
                            output += f"Валова маржа: {value} (низька).\n"
                        else:
                            output += f"Gross margin: {value} (low).\n"
                    elif float(value[:-1]) > 40:
                        if language == 'Ukrainian':
                            output += f"Валова маржа: {value} (висока).\n"
                        else:
                            output += f"Gross margin: {value} (high).\n"
                    else:
                        if language == 'Ukrainian':
                            output += f"Валова маржа: {value} (середня).\n"
                        else:
                            output += f"Gross margin: {value} (average).\n"
                elif metric == "Operating Margin":
                    if value == "No data available":
                        if language == 'Ukrainian':
                            output += f"Дані про операційну маржу недоступні.\n"
                        else:
                            output += f"Operating margin data not available.\n"
                    elif float(value[:-1]) < 10:
                        if language == 'Ukrainian':
                            output += f"Операційна маржа: {value} (низька).\n"
                        else:
                            output += f"Operating margin: {value} (low).\n"
                    elif float(value[:-1]) > 20:
                        if language == 'Ukrainian':
                            output += f"Операційна маржа: {value} (висока).\n"
                        else:
                            output += f"Operating margin: {value} (high).\n"
                    else:
                        if language == 'Ukrainian':
                            output += f"Операційна маржа: {value} (помірна).\n"
                        else:
                            output += f"Operating margin: {value} (moderate).\n"
                elif metric == "Profit Margin":
                    if value == "No data available":
                        if language == 'Ukrainian':
                            output += f"Дані про чисту маржу недоступні.\n"
                        else:
                            output += f"Profit margin data not available.\n"
                    elif float(value[:-1]) < 5:
                        if language == 'Ukrainian':
                            output += f"Чиста маржа: {value} (низька).\n"
                        else:
                            output += f"Profit margin: {value} (low).\n"
                    elif float(value[:-1]) > 15:
                        if language == 'Ukrainian':
                            output += f"Чиста маржа: {value} (висока).\n"
                        else:
                            output += f"Profit margin: {value} (high).\n"
                    else:
                        if language == 'Ukrainian':
                            output += f"Чиста маржа: {value} (помірна).\n"
                        else:
                            output += f"Profit margin: {value} (moderate).\n"
            except TypeError:
                output += f"{metric}: {value}\n"

        if language == 'Ukrainian':
            output += "\n**Резюме:**\n"
            output += "На основі фундаментальних показників, компанія демонструє наступні фінансові показники:\n"

            try:
                if metrics["Trailing P/E"] != "No data available" and metrics["Forward P/E"] != "No data available":
                    if metrics["Trailing P/E"] < 15 and metrics["Forward P/E"] < 15:
                        output += "Оцінка компанії виглядає недооціненою на основі коефіцієнтів P/E, що вказує на потенційний ріст ціни.\n"
                    elif metrics["Trailing P/E"] > 25 and metrics["Forward P/E"] > 25:
                        output += "Оцінка компанії виглядає переоціненою на основі коефіцієнтів P/E, що може свідчити про можливість корекції ціни.\n"
                    else:
                        output += "Оцінка компанії виглядає справедливою на основі коефіцієнтів P/E, що вказує на стабільність цін.\n"

                if metrics["Return on Equity (ROE)"] != "No data available":
                    if metrics["Return on Equity (ROE)"] > 0.15:
                        output += "Компанія демонструє високу прибутковість з високим ROE, що свідчить про ефективне використання капіталу.\n"
                    else:
                        output += "Компанія показує нижчу прибутковість на основі ROE, що може свідчити про неефективність використання капіталу.\n"

                if metrics["Debt to Equity"] != "No data available":
                    if metrics["Debt to Equity"] < 0.5:
                        output += "Баланс компанії виглядає сильним з низьким рівнем заборгованості, що зменшує фінансовий ризик.\n"
                    elif metrics["Debt to Equity"] > 2:
                        output += "Компанія має високий рівень заборгованості, що може становити ризик під час економічного спаду або періоду високих процентних ставок.\n"
                    else:
                        output += "Баланс компанії показує помірний рівень заборгованості, що вказує на збалансований підхід до управління боргом.\n"
            except Exception as e:
                output += f"Помилка у Резюме: {e}\n"

            output += "\n**Загальна Оцінка:**\n"
            try:
                if metrics["Trailing P/E"] < 15 and metrics["Return on Equity (ROE)"] > 0.15 and metrics["Debt to Equity"] < 0.5:
                    output += "На основі низької оцінки, високої прибутковості та міцного балансу, компанія виглядає привабливим об'єктом для інвестування."
                else:
                    output += "З огляду на поточну оцінку, прибутковість та баланс, компанія представляє збалансовану інвестиційну можливість з помірними ризиками."
            except Exception as e:
                output += f"Помилка у Загальній Оцінці: {e}\n"
        else:
            output += "\n**Summary:**\n"
            output += "Based on the fundamental metrics, the company shows the following financial health indicators:\n"

            try:
                if metrics["Trailing P/E"] != "No data available" and metrics["Forward P/E"] != "No data available":
                    if metrics["Trailing P/E"] < 15 and metrics["Forward P/E"] < 15:
                        output += "The company's valuation appears to be undervalued based on its P/E ratios, suggesting potential for price appreciation.\n"
                    elif metrics["Trailing P/E"] > 25 and metrics["Forward P/E"] > 25:
                        output += "The company's valuation appears to be overvalued based on its P/E ratios, indicating potential risk of price correction.\n"
                    else:
                        output += "The company's valuation appears to be fairly valued based on its P/E ratios, suggesting a stable price outlook.\n"

                if metrics["Return on Equity (ROE)"] != "No data available":
                    if metrics["Return on Equity (ROE)"] > 0.15:
                        output += "The company demonstrates strong profitability with a high ROE, indicating efficient use of equity capital.\n"
                    else:
                        output += "The company shows lower profitability based on its ROE, which could indicate inefficiencies in using equity capital.\n"

                if metrics["Debt to Equity"] != "No data available":
                    if metrics["Debt to Equity"] < 0.5:
                        output += "The company's balance sheet appears strong with low leverage, reducing financial risk.\n"
                    elif metrics["Debt to Equity"] > 2:
                        output += "The company carries a high level of debt, which may pose a risk during economic downturns or periods of high-interest rates.\n"
                    else:
                        output += "The company's balance sheet shows moderate leverage, indicating a balanced approach to debt management.\n"
            except Exception as e:
                output += f"Error in Summary: {e}\n"

            output += "\n**Overall Assessment:**\n"
            try:
                if metrics["Trailing P/E"] < 15 and metrics["Return on Equity (ROE)"] > 0.15 and metrics["Debt to Equity"] < 0.5:
                    output += "Based on its low valuation, high profitability, and strong balance sheet, the company appears to be a solid investment opportunity."
                else:
                    output += "Considering its current valuation, profitability, and balance sheet, the company presents a balanced investment opportunity with moderate risks."
            except Exception as e:
                output += f"Error in Overall Assessment: {e}\n"

        return output
    except Exception as e:
        return f"Error retrieving data for {ticker}: {e}"
