import logging
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater

from buttoms_and_function_call import *
from developer_functions.general_dev.send_signal_to_user import get_strategy
# from developer_functions.general_dev.send_signal_to_user import process_signals
# from developer_functions.general_dev.send_signal_to_user import process_signals
from general.universal_functions import symbol_info
from general.user_list import handle_user_interaction
from keyboards import *
from run_all_siganlas_calc import schedule_signal_updates
from state_update_menu import update_menu_state

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Token for your bot (ensure to keep this token private in real-world applications)
TOKEN = '7721716265:AAEuzhZyZM_pT0FQHsbx-FziENEg-cNT5do'


def start(update: Update, context: CallbackContext) -> None:
    context.user_data['menu_stack'] = ['start']

    # Виклик функції з передачею необхідних аргументів
    handle_user_interaction(update, context)

    # Відправляємо повідомлення користувачу
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='https://t.me/stashkiv_mykhailo created'
                                  ' this bot to provide people with access to the'
                                  ' best ideas for investments and speculations.',
                             reply_markup=create_start_keyboard())

    update_menu_state('start')


def main():
    """Start the bot."""
    # Initialize the Updater with your bot's TOKEN
    updater = Updater(TOKEN, use_context=True)
    # test
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    def about_bot_func_button_call(update: Update, context: CallbackContext) -> None:
        about_bot(update, context)
        update_menu_state('about')

    def help_func_button_call(update: Update, context: CallbackContext) -> None:
        help_button(update, context)
        update_menu_state('help')

    def stock_func_button_call(update: Update, context: CallbackContext) -> None:
        stock_keyboard(update, context)
        update_menu_state('stock_menu')

    def stock_mrkt_overview_func_button_call(update: Update, context: CallbackContext) -> None:
        test_button(update, context)
        update_menu_state('mrkt_overview')

    def stock_company_info_func_button_call(update: Update, context: CallbackContext) -> None:
        symbol_info(update, context)
        update_menu_state('stock_company_info')

    def stock_signal_func_button_call(update: Update, context: CallbackContext) -> None:
        update_menu_state('stock_signal')
        get_strategy(update, context)

    def forex_func_button_call(update: Update, context: CallbackContext) -> None:
        forex_keyboard(update, context)
        update_menu_state('forex_menu')

    def forex_mrkt_overview_func_button_call(update: Update, context: CallbackContext) -> None:
        test_button(update, context)
        update_menu_state('forex_mrkt_overview')

    def forex_pairs_info_func_button_call(update: Update, context: CallbackContext) -> None:
        symbol_info(update, context)
        update_menu_state('forex_pairs_info')

    def forex_signals_func_button_call(update: Update, context: CallbackContext) -> None:
        update_menu_state('forex_signal')
        # process_signals(update, context)

    def crypto_func_button_call(update: Update, context: CallbackContext) -> None:
        crypto_keyboard(update, context)
        update_menu_state('crypto_menu')

    def crypto_mrkt_overview_func_button_call(update: Update, context: CallbackContext) -> None:
        test_button(update, context)
        update_menu_state('crypto_mrkt_overview')

    def crypto_info_func_button_call(update: Update, context: CallbackContext) -> None:
        symbol_info(update, context)
        update_menu_state('crypto_info')

    def crypto_signals_func_button_call(update: Update, context: CallbackContext) -> None:
        update_menu_state('crypto_signals')
        # process_signals(update, context)

    schedule_signal_updates()

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex(r'^About Bot$'), about_bot_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r'^Help$'), help_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r'^Menu$'), menu))

    # Register message handlers for stock menu
    dp.add_handler(MessageHandler(Filters.regex(r'^Stock$'), stock_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r"^Stocks Market Overview"), stock_mrkt_overview_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r'^Company information$'), stock_company_info_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r'^Stock Signals$'), stock_signal_func_button_call))

    # Register message handlers for Forex menu
    dp.add_handler(MessageHandler(Filters.regex(r'^Forex$'), forex_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r'^Forex Market Overview$'), forex_mrkt_overview_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r'^Pairs info$'), forex_pairs_info_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r'^Forex Signals$'), forex_signals_func_button_call))

    # Register message handlers for Crypto menu
    dp.add_handler(MessageHandler(Filters.regex(r'^Crypto$'), crypto_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r'^Crypto Market Overview$'), crypto_mrkt_overview_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r'^Cryptocurrencies info$'), crypto_info_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r'^Crypto Signals$'), crypto_signals_func_button_call))

    # Back button
    dp.add_handler(MessageHandler(Filters.regex(r'^Back$'), back_function))

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM, or SIGABRT.
    updater.idle()


if __name__ == '__main__':
    main()
