import yfinance as yf
from telegram.ext import MessageHandler, Filters

from crypto.get_crypto_data import *
from general.chart import generate_chart
from state_update_menu import menu_state, update_menu_state
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
    ticker = update.message.text.upper()
    try:
        if state == 'stock_company_info':
            symbol = yf.Ticker(ticker)
            metrics_table = get_stock_metrics(symbol, ticker)
            img_path = generate_chart(ticker)

            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img_path, 'rb'))
            context.bot.send_message(chat_id=update.effective_chat.id, text=metrics_table)

        elif state == 'crypto_info':
            img_path = generate_chart(ticker + '-USD')
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img_path, 'rb'))

            metrics_table = get_crypto_info_from_coinmarketcap(ticker)
            context.bot.send_message(chat_id=update.effective_chat.id, text=metrics_table)

        elif state == 'forex_pairs_info':
            # Аналогічно можна додати функцію для форекса
            img_path = generate_chart(ticker + '=X')
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img_path, 'rb'))


    except Exception as e:
        if state == 'stock_company_info':
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error! Ticker '{ticker}' not found. "
                                                                            f"Please check the input. (Ex: AAPL)")
        elif state == 'crypto_info':
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error! Ticker '{ticker}' not found. "
                                                                            f"Please check the input. (Ex: BTC)")
        elif state == 'forex_pairs_info':
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error! Ticker '{ticker}' not found. "
                                                                            f"Please check the input. (Ex: EUR-USD)")



