import csv
import os
import yfinance as yf
from telegram.ext import MessageHandler, Filters
from state_update_menu import menu_state  # Передбачається, що ця функція коректно працює


def add_ticker_to_list(update, context):
    dp = context.dispatcher

    # Видалити всі текстові хендлери, щоб уникнути конфліктів
    clear_text_handlers(dp)

    # Додати новий хендлер для введення тікера
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, add_ticker_func))

    context.bot.send_message(chat_id=update.effective_chat.id, text='Enter the ticker to add to the watch list:')


def remove_ticker_from_list(update, context):
    dp = context.dispatcher

    # Видалити всі текстові хендлери, щоб уникнути конфліктів
    clear_text_handlers(dp)

    # Додати новий хендлер для введення тікера
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, delete_ticker))

    context.bot.send_message(chat_id=update.effective_chat.id, text='Enter a ticker to remove it from the watchlist:')


def clear_text_handlers(dp):
    """Видаляє всі текстові хендлери, щоб уникнути конфліктів."""
    for handler in dp.handlers[0]:  # Перевірка першого рівня хендлерів
        if isinstance(handler, MessageHandler) and handler.filters == (Filters.text & ~Filters.command):
            dp.remove_handler(handler)


def add_ticker_func(update, context):
    state = menu_state().strip()
    print(f"Menu state: '{state}'")  # Діагностика стану меню
    if state != 'add_to_watchlist':
        update.message.reply_text("Invalid state for adding a ticker.")
        return

    ticker = update.message.text.upper()
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stock_dev"))
    file_path = os.path.join(base_dir, "tickers.csv")

    os.makedirs(base_dir, exist_ok=True)

    if not is_valid_ticker(ticker):
        update.message.reply_text(f"The ticker {ticker} is invalid or not supported.")
        return

    existing_tickers = get_existing_tickers(file_path)

    if ticker in existing_tickers:
        update.message.reply_text(f"The ticker {ticker} is already in the file. Current list of tickers: {', '.join(existing_tickers)}")
        return

    stock = yf.Ticker(ticker)
    try:
        metrics = {
            "Ticker": ticker,
            "Trailing P/E": stock.info.get("trailingPE", "N/A"),
            "Forward P/E": stock.info.get("forwardPE", "N/A"),
            "Price to Book": stock.info.get("priceToBook", "N/A"),
            "Return on Equity (ROE)": stock.info.get("returnOnEquity", "N/A"),
            "Return on Assets (ROA)": stock.info.get("returnOnAssets", "N/A"),
            "Debt to Equity": stock.info.get("debtToEquity", "N/A"),
            "Current Ratio": stock.info.get("currentRatio", "N/A"),
            "Dividend Yield": stock.info.get("dividendYield", "N/A"),
            "Payout Ratio": stock.info.get("payoutRatio", "N/A"),
            "Gross Margin": stock.info.get("grossMargins", "N/A"),
            "Operating Margin": stock.info.get("operatingMargins", "N/A"),
            "Profit Margin": stock.info.get("profitMargins", "N/A"),
        }
    except Exception as e:
        update.message.reply_text(f"Failed to fetch data for {ticker}. Error: {str(e)}")
        return

    file_exists = os.path.exists(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=metrics.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(metrics)

    update.message.reply_text(f"The ticker {ticker} has been added with metrics.")
    print(f"Ticker {ticker} has been written to {file_path}")


def delete_ticker(update, context):
    state = menu_state().strip()
    print(f"Menu state: '{state}'")  # Діагностика стану меню
    if state != 'remove_from_watchlist':
        update.message.reply_text("Invalid state for removing a ticker.")
        return

    ticker_to_delete = update.message.text.upper()
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stock_dev"))
    file_path = os.path.join(base_dir, "tickers.csv")

    if not os.path.exists(file_path):
        update.message.reply_text("The ticker list file does not exist.")
        return

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)

    if len(rows) <= 1:
        update.message.reply_text("The ticker list is empty. Nothing to delete.")
        return

    header = rows[0]
    tickers = [row[0] for row in rows[1:]]

    if ticker_to_delete not in tickers:
        update.message.reply_text(f"The ticker {ticker_to_delete} is not in the list.")
        return

    tickers.remove(ticker_to_delete)

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for ticker in tickers:
            writer.writerow([ticker])

    update.message.reply_text(f"The ticker {ticker_to_delete} has been removed.")
    print(f"Ticker {ticker_to_delete} has been removed from {file_path}")


def is_valid_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period="1d")
        return not stock_data.empty
    except Exception:
        return False


def get_existing_tickers(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        return [row[0] for row in reader][1:]


def send_ticker_list(update, context):
    """Send the list of tickers to the user."""
    # Absolute path to the stock_dev directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stock_dev"))
    file_path = os.path.join(base_dir, "tickers.csv")

    # Check if the file exists
    if not os.path.exists(file_path):
        update.message.reply_text("The ticker list file does not exist.")
        return

    # Read the existing tickers
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Check if the file has any tickers (excluding the header)
    if len(rows) <= 1:
        update.message.reply_text("The ticker list is empty.")
        return

    # Extract tickers, skipping the header
    tickers = [row[0] for row in rows[1:]]

    # Send the list of tickers to the user
    update.message.reply_text(f"Current list of tickers: {', '.join(tickers)}")

    # Log to the console
    print(f"Sent ticker list: {', '.join(tickers)}")