import yfinance as yf
import numpy as np


def get_volatility_metrics(symbol):
    # Завантажуємо історичні дані
    data = yf.download(symbol, period='6mo', interval='1d')

    # Розрахунок технічних індикаторів для оцінки волатильності
    data['ATR'] = talib.ATR(data['High'], data['Low'], data['Close'], timeperiod=14)

    # Історична волатильність (за стандартним відхиленням зміни логарифмів ціни)
    data['log_returns'] = np.log(data['Close'] / data['Close'].shift(1))
    data['Historical_Volatility'] = data['log_returns'].rolling(window=30).std() * np.sqrt(
        252)  # Волатильність на основі 30 днів

    # Розрахунок Bollinger Bands (волатильність на основі стандартних відхилень)
    data['Upper_Band'], data['Middle_Band'], data['Lower_Band'] = talib.BBANDS(data['Close'], timeperiod=20, nbdevup=2,
                                                                               nbdevdn=2, matype=0)

    # Останні значення метрик
    latest_data = {
        'ATR': data['ATR'].iloc[-1],  # Середній діапазон руху ціни
        'Historical_Volatility': data['Historical_Volatility'].iloc[-1],  # Історична волатильність
        'Bollinger_Bands': {
            'Upper Band': data['Upper_Band'].iloc[-1],
            'Middle Band': data['Middle_Band'].iloc[-1],
            'Lower Band': data['Lower_Band'].iloc[-1]
        }
    }

    return latest_data


# Приклад використання
symbol = 'EURUSD=X'  # Використовуємо Yahoo Finance тикер для EUR/USD
volatility_data = get_volatility_metrics(symbol)

# Виводимо результати
for key, value in volatility_data.items():
    print(f"{key}: {value}")
