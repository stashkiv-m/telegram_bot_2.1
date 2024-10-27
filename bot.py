import logging
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater

from buttoms_and_function_call import *
from developer_functions.general_dev.send_signal_to_user import signal_list_for_user
from general.universal_functions import symbol_info
from general.user_list import  add_user_activity
from keyboards import *
from language_state import update_language_state, language_state
from run_all_siganlas_calc import schedule_signal_updates
from state_update_menu import update_menu_state
from telegram.ext import CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Token for your bot (ensure to keep this token private in real-world applications)

TOKEN = '7749471664:AAEp85bkb0szrSBDso9bxU2FSy8JU0RVSEY'


def start(update: Update, context: CallbackContext) -> None:
    # Зберігаємо стан меню
    context.user_data['menu_stack'] = ['start']

    # Отримуємо мову користувача
    language = language_state().rstrip('\n')

    # Відправляємо привітання та опис проекту залежно від мови
    if language == 'Ukrainian':
        greeting = (
            "https://t.me/stashkiv_mykhailo створив цього бота, щоб надати людям доступ до найкращих ідей для інвестицій та спекуляцій.\n\n"
            "Цей проект спрямований на підвищення фінансової грамотності населення, щоб люди не потрапляли на шахрайські схеми та інші фінансові пастки.\n"
            "Усі кошти, зібрані за допомогою цього бота, будуть спрямовані на розробку нових функцій.\n"
            "Ті, хто підтримає проект, отримають передчасний доступ до нових функцій та можливостей бота.\n\n"
            "Бот може аналізувати акції, криптовалюти та форекс, надаючи технічний аналіз і рекомендації. В планах — використання AI для більш точного аналізу та нових функцій.\n"
            "Бот не може гарантувати прибуток або повністю передбачити рух ринку, але може надати корисну інформацію для прийняття рішень."
        )
        support_info = (
            "Якщо хочете підтримати проект, буду вдячний за фінансову підтримку:\n\n"
            "PayPal: business.stashkiv@gmail.com\n\n"
            "ETH ERC 20 гаманець: 0x281ce314d2f3762ccb591a987ad9a793bf0be2a7\n\n"
            "Усі внески будуть використані на розвиток нових можливостей бота та покращення його функціональності."
        )
    else:
        greeting = (
            "https://t.me/stashkiv_mykhailo created this bot to provide people with access to the best ideas for investments and speculations.\n\n"
            "This project aims to improve financial literacy, helping people avoid scams and other financial traps.\n"
            "All funds collected through this bot will be used for developing new features.\n"
            "Supporters will receive early access to new features and capabilities of the bot.\n\n"
            "The bot can analyze stocks, cryptocurrencies, and forex, providing technical analysis and recommendations. Future plans include integrating AI for more precise analysis and new functionalities.\n"
            "The bot cannot guarantee profits or fully predict market movements, but it can provide valuable insights for decision-making."
        )
        support_info = (
            "If you'd like to support the project, I would appreciate any financial contributions:\n\n"
            "PayPal: business.stashkiv@gmail.com\n\n"
            "ETH ERC 20 Wallet: 0x281ce314d2f3762ccb591a987ad9a793bf0be2a7\n\n"
            "All contributions will be used to develop new features and improve the bot's functionality."
        )

    # Виклик функції з передачею необхідних аргументів

    # Відправляємо повідомлення користувачу
    context.bot.send_message(chat_id=update.effective_chat.id, text=greeting, reply_markup=create_start_keyboard())
    context.bot.send_message(chat_id=update.effective_chat.id, text=support_info)

    # Оновлюємо стан меню
    update_menu_state('start')


def menu(update, context):
    context.user_data['menu_stack'] = ['menu']
    # Отримуємо ID користувача та його ім'я
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Викликаємо функцію для запису активності користувача
    add_user_activity(user_id, username)

    keyboard = [
        [KeyboardButton("Stock")],
        # [KeyboardButton("Forex")],
        # [KeyboardButton("Crypto")],
        [KeyboardButton("Back")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Меню:', reply_markup=reply_markup)
    update_menu_state('menu')


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

    def language_func_button_call(update: Update, context: CallbackContext) -> None:
        language_keyboard(update, context)
        update_menu_state('language')

    def ukr_language(update: Update, context: CallbackContext) -> None:
        update_language_state('Ukrainian')
        context.bot.send_message(chat_id=update.effective_chat.id, text="Мова змінена на українську 🇺🇦")

    def english_language(update: Update, context: CallbackContext) -> None:
        update_language_state('English')
        context.bot.send_message(chat_id=update.effective_chat.id, text="Language changed to English. 🇬🇧")

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
        signal_list_for_user(update, context)

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
        signal_list_for_user(update, context)

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
        signal_list_for_user(update, context)

    schedule_signal_updates()


    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex(r'^About Bot$'), about_bot_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r'^Language'), language_func_button_call))
    dp.add_handler(MessageHandler(Filters.regex(r'^Ukrainian'), ukr_language))
    dp.add_handler(MessageHandler(Filters.regex(r'^English'), english_language))
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
