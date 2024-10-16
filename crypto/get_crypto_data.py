import requests

def get_crypto_info_from_coinmarketcap(symbol, language='English'):
    api_key = 'a4029b53-55ed-402c-bacd-ad94c442a684'
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

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
            circulating_supply = crypto_data['circulating_supply']
            max_supply = crypto_data.get('max_supply', 'N/A')
            total_supply = crypto_data['total_supply']
            last_updated = crypto_data['last_updated']
            slug = crypto_data['slug']  # Ідентифікатор для формування посилання

            # Створення посилання на CoinMarketCap
            url_to_coinmarketcap = f"https://coinmarketcap.com/currencies/{slug}/"

            if language == 'Ukrainian':
                result = f"""
                {name}
                Символ: {symbol}
                Ціна: ${price:.2f}
                Ринкова капіталізація: ${market_cap:,.0f}
                Обсяг (24 години): ${volume_24h:,.0f}
                Обігове забезпечення: {circulating_supply:,.0f} {symbol}
                Загальне забезпечення: {total_supply:,.0f} {symbol}
                Максимальне забезпечення: {max_supply:,.0f} {symbol}
                Зміна ціни за 1 годину: {percent_change_1h:.2f}%
                Зміна ціни за 24 години: {percent_change_24h:.2f}%
                Зміна ціни за 7 днів: {percent_change_7d:.2f}%
                Зміна ціни за 30 днів: {percent_change_30d:.2f}%
                Зміна ціни за 90 днів: {percent_change_90d:.2f}%

                Більше інформації: {url_to_coinmarketcap}
                """
            else:
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
            if language == 'Ukrainian':
                return f"Дані для активу {symbol} наразі недоступні."
            else:
                return f"No data found for {symbol}."
    except Exception as e:
        if language == 'Ukrainian':
            return f"Помилка отримання даних для активу {symbol}: для цього активу поки що інші дані не доступні."
        else:
            return f"Error retrieving data for {symbol}: other data for this asset is currently unavailable."
