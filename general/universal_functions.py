import yfinance as yf
from telegram.ext import MessageHandler, Filters

from crypto.get_crypto_data import *
from developer_functions.general_dev.chart import generate_chart
from general.technical_analys_chart import analyze_ticker
from language_state import language_state
from state_update_menu import menu_state
from stock.get_stock_data import get_stock_metrics


def symbol_info(update, context):
    # Надіслати повідомлення користувачеві з проханням ввести тікер акції
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Enter the symbol you are interested in:')

    # Реєструвати обробник повідомлень для обробки введення користувача
    dp = context.dispatcher
    dp.add_handler(MessageHandler(Filters.text, handle_ticker_input))


def handle_ticker_input(update, context):
    state = menu_state().rstrip('\n')
    language = language_state().rstrip('\n')
    ticker = update.message.text.upper()

    try:
        # Завантажуємо дані на основі стану
        if state == 'stock_company_info':
            symbol = yf.Ticker(ticker)
            data = symbol.history(period="1y")

            # Отримуємо таблицю метрик для акції
            metrics_table = get_stock_metrics(symbol, ticker, language)

            # Генеруємо текстовий аналіз і шлях до графіка
            analysis = analyze_ticker(ticker=ticker, data=data, language=language, state=state)
            img_path = generate_chart(ticker)

            # Відправляємо графік і результати аналізу користувачу
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img_path, 'rb'))
            # Форматуємо текст з заголовками для кожної секції
            full_message = (
                f"**Technical Analysis:**\n{analysis}\n\n"
                f"**Fundamental Metrics:**\n{metrics_table}\n"
            )

            # Відправляємо повідомлення користувачу
            context.bot.send_message(chat_id=update.effective_chat.id, text=full_message, parse_mode='Markdown')

            # context.bot.send_message(chat_id=update.effective_chat.id, text=analysis)

        elif state == 'crypto_info':
            symbol = yf.Ticker(ticker + '-USD')
            data = symbol.history(period="1y")

            # Генеруємо текстовий аналіз для криптовалюти
            analysis = analyze_ticker(ticker=ticker, data=data, language=language, state=state)
            img_path = generate_chart(ticker + '-USD')

            # Відправляємо графік та аналіз користувачу
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img_path, 'rb'))

            # Отримуємо та відправляємо таблицю метрик для криптовалюти
            metrics_table = get_crypto_info_from_coinmarketcap(ticker, language)
            full_message = (
                f"**Technical Analysis:**\n{analysis}\n\n"
                f"**Fundamental Metrics:**\n{metrics_table}\n"
            )

            # Відправляємо повідомлення користувачу
            context.bot.send_message(chat_id=update.effective_chat.id, text=full_message, parse_mode='Markdown')

        elif state == 'forex_pairs_info':
            symbol = yf.Ticker(ticker + '=X')
            data = symbol.history(period="1y")

            # Генеруємо текстовий аналіз для форекса
            analysis = analyze_ticker(ticker=ticker, data=data, language=language, state=state)
            img_path = generate_chart(ticker + '=X')

            # Відправляємо графік та аналіз користувачу
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img_path, 'rb'))
            full_message = (
                f"**Technical Analysis:**\n{analysis}\n\n"
            )

            # Відправляємо повідомлення користувачу
            context.bot.send_message(chat_id=update.effective_chat.id, text=full_message, parse_mode='Markdown')

    except Exception as e:
        # Відправка повідомлення про помилку в залежності від стану
        error_message = f"Error! Ticker '{ticker}' not found. Please check the input."
        if state == 'stock_company_info':
            error_message += " (Ex: AAPL)"
        elif state == 'crypto_info':
            error_message += " (Ex: BTC)"
        elif state == 'forex_pairs_info':
            error_message += " (Ex: EUR-USD)"

        context.bot.send_message(chat_id=update.effective_chat.id, text=error_message)




