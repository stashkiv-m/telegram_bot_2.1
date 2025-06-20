import yfinance as yf
from telegram.ext import MessageHandler, Filters


from crypto.get_crypto_data import *
from developer_functions.general_dev.chart import generate_chart
from general.user_list import get_user_watchlist
from keyboards import get_watchlist_inline_keyboard
from language_state import language_state
from state_update_menu import menu_state
from stock.get_stock_data import get_stock_metrics


from language_state import language_state


def symbol_info(update, context):
    language = language_state().rstrip('\n')
    if language == "Ukrainian":
        prompt = "Введіть тікер, який вас цікавить:"
    else:
        prompt = "Enter the symbol you are interested in:"

    context.bot.send_message(chat_id=update.effective_chat.id, text=prompt)

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
            # analysis = analyze_ticker(ticker=ticker, data=data, language=language, state=state)

            img_path = generate_chart(ticker)
            reply_markup = get_watchlist_inline_keyboard(ticker)

            # Відправляємо графік і результати аналізу користувачу
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=open(img_path, 'rb'),

            )
            # Форматуємо текст з заголовками для кожної секції
            full_message = f"**Fundamental Metrics:**\n{metrics_table}\n"
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=full_message,
                parse_mode='Markdown',
                reply_markup=reply_markup  # <- ось тут будуть кнопки!
            )

            # Відправляємо повідомлення користувачу
            # context.bot.send_message(chat_id=update.effective_chat.id, text=full_message, parse_mode='Markdown')

            # context.bot.send_message(chat_id=update.effective_chat.id, text=analysis)

        elif state == 'crypto_info':
            symbol = yf.Ticker(ticker + '-USD')
            data = symbol.history(period="1y")

            # Генеруємо текстовий аналіз для криптовалюти
            # analysis = analyze_ticker(ticker=ticker, data=data, language=language, state=state)

            img_path = generate_chart(ticker + '-USD')

            # Відправляємо графік та аналіз користувачу
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img_path, 'rb'))

            # Отримуємо та відправляємо таблицю метрик для криптовалюти
            metrics_table = get_crypto_info_from_coinmarketcap(ticker, language)
            full_message = (
                f"**Fundamental Metrics:**\n{metrics_table}\n"
            )

            # Відправляємо повідомлення користувачу
            context.bot.send_message(chat_id=update.effective_chat.id, text=full_message, parse_mode='Markdown')

        elif state == 'forex_pairs_info':
            symbol = yf.Ticker(ticker + '=X')
            data = symbol.history(period="1y")

            # Генеруємо текстовий аналіз для форекса
            # analysis = analyze_ticker(ticker=ticker, data=data, language=language, state=state)
            analysis = 'Technical analysis is not yet available.'

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


def show_watchlist_with_changes(update, context):
    user_id = update.effective_user.id
    tickers = get_user_watchlist(user_id)
    if not tickers:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ваш Watchlist порожній."
        )
        return

    msg = "Ваш Watchlist за 24 години:\n"
    for ticker in tickers:
        try:
            data = yf.Ticker(ticker).history(period="2d")
            if data.shape[0] < 2:
                change_str = "немає даних"
                icon = "❔"
            else:
                price_yesterday = data['Close'].iloc[-2]
                price_today = data['Close'].iloc[-1]
                change = ((price_today / price_yesterday) - 1) * 100
                sign = "+" if change > 0 else ""
                icon = "📈" if change > 0 else ("📉" if change < 0 else "➖")
                change_str = f"{sign}{change:.2f}%"
            msg += f"{icon} {ticker} {change_str}\n"
        except Exception as e:
            msg += f"❌ {ticker} (error)\n"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg
    )
