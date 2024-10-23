import yfinance as yf

# Створюємо об'єкт Ticker для заданого символу (наприклад, AAPL для Apple)
ticker = yf.Ticker("AAPL")

# Отримуємо новини про компанію
news = ticker.news

# Виводимо новини
for article in news:
    print(f"Title: {article['title']}")
    print(f"Publisher: {article['publisher']}")
    print(f"Link: {article['link']}")
    print(f"Published Date: {article['providerPublishTime']}")
    print("-" * 80)
