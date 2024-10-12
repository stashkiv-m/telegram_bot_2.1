import requests


def get_crypto_info_from_coinmarketcap(symbol):
    api_key = 'a4029b53-55ed-402c-bacd-ad94c442a684'
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    parameters = {
        'symbol': symbol.upper(),  # Символ криптовалюти
        'convert': 'USD'  # Конвертація у долари
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,  # Твій API ключ
    }

    try:
        response = requests.get(url, headers=headers, params=parameters)
        data = response.json()

        # Отримання ключових даних
        if 'data' in data and symbol.upper() in data['data']:
            crypto_data = data['data'][symbol.upper()]
            name = crypto_data['name']
            symbol = crypto_data['symbol']
            price = crypto_data['quote']['USD']['price']
            market_cap = crypto_data['quote']['USD']['market_cap']
            volume_24h = crypto_data['quote']['USD']['volume_24h']
            percent_change_1h = crypto_data['quote']['USD']['percent_change_1h']
            percent_change_24h = crypto_data['quote']['USD']['percent_change_24h']
            percent_change_7d = crypto_data['quote']['USD']['percent_change_7d']
            percent_change_30d = crypto_data['quote']['USD']['percent_change_30d']
            percent_change_90d = crypto_data['quote']['USD']['percent_change_90d']
            ath_price = crypto_data.get('ath', 'N/A')  # All-time high
            circulating_supply = crypto_data['circulating_supply']
            max_supply = crypto_data.get('max_supply', 'N/A')
            total_supply = crypto_data['total_supply']
            launch_date = crypto_data.get('date_added', 'N/A')  # Дата запуску
            last_updated = crypto_data['last_updated']
            slug = crypto_data['slug']  # Ідентифікатор для формування посилання

            # Створення посилання на CoinMarketCap
            url_to_coinmarketcap = f"https://coinmarketcap.com/currencies/{slug}/"

            result = f"""
                {name}
            Symbol: {symbol}
            Price: ${price:.2f}
            Market Cap: ${market_cap:,.0f}
            Volume (24h): ${volume_24h:,.0f}
            Circulating Supply: {circulating_supply:,.0f} {symbol}
            Total Supply: {total_supply:,.0f} {symbol}
            Max Supply: {max_supply:,.0f} {symbol}
            1h Price Change: {percent_change_1h:.2f}%
            24h Price Change: {percent_change_24h:.2f}%
            7d Price Change: {percent_change_7d:.2f}%
            30d Price Change: {percent_change_30d:.2f}%
            90d Price Change: {percent_change_90d:.2f}%

            More Info: {url_to_coinmarketcap}
            """
            return result
        else:
            return f"No data found for {symbol}."

    except Exception as e:
        return f"Error retrieving data: {e}"
