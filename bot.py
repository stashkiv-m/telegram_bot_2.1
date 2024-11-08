import logging
import os

from telegram import Update, Bot
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater

from buttoms_and_function_call import *
from developer_functions.general_dev.send_signal_to_user import signal_list_for_user
from general.daily_information import send_daily_events, send_day_end_info
from general.universal_functions import symbol_info
from general.user_list import  user_activity_and_access
from keyboards import *
from language_state import update_language_state, language_state
from run_all_siganlas_calc import schedule_func_call, all_signals_calc_run
from state_update_menu import update_menu_state, menu_state
from telegram.ext import CallbackContext

from stock.market_overwiev import send_market_overview
from user_state import update_user_state, user_state

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
            "https://t.me/stashkiv_mykhailo\n\n"
            "Бот аналізує акції, надаючи технічний та фундаментальий аналіз. Згодом буде крипто та форекс \n"
            "Бот не гарантує прибутків, але надає корисну інформацію для прийняття рішень."
        )
        support_info = (
            "Підтримати проєкт можна за реквізитами:\n\n"
            "PayPal: business.stashkiv@gmail.com\n"
            "ETH: 0x281ce314d2f3762ccb591a987ad9a793bf0be2a7\n\n"
            "Ваш внесок допоможе в розробці нових функцій бота."
        )

    else:
        greeting = (
            "https://t.me/stashkiv_mykhailo\n\n"
            "The bot analyzes stocks, providing technical and fundamental analysis. Crypto and forex will be added later.\n"
            "The bot doesn't guarantee profits but provides valuable information for decision-making."
        )
        support_info = (
            "Support the project via:\n\n"
            "PayPal: business.stashkiv@gmail.com\n"
            "ETH: 0x281ce314d2f3762ccb591a987ad9a793bf0be2a7\n\n"
            "Your contribution helps develop new bot features."
        )

    # Виклик функції з передачею необхідних аргументів

    # Відправляємо повідомлення користувачу
    context.bot.send_message(chat_id=update.effective_chat.id, text=greeting, reply_markup=create_start_keyboard())
    context.bot.send_message(chat_id=update.effective_chat.id, text=support_info)

    # Оновлюємо стан меню
    update_menu_state('start')


def menu(update, context):
    context.user_data['menu_stack'] = ['menu']
    if user_activity_and_access(update, context):
        keyboard = [
            [KeyboardButton("Stock")],
            # [KeyboardButton("Forex")],
            # [KeyboardButton("Crypto")],
            [KeyboardButton("Back")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Menu:', reply_markup=reply_markup)
        update_menu_state('menu')
    else:
        pass


def handle_photo(update: Update, context: CallbackContext) -> None:
    state = user_state().rstrip('\n')
    if state == 'guest':
        ADMIN_CHAT_ID = 1440645936

        # Створюємо екземпляр другого бота
        second_bot = Bot(token='7342427635:AAFwm6vpbifNorUhWoiJvWxE18IVtK4UARQ')

        # Отримуємо дані користувача
        user_id = update.message.from_user.id
        username = update.message.from_user.username if update.message.from_user.username else "No Username"

        # Отримуємо фото з повідомлення
        photo_file = update.message.photo[-1].get_file()  # Отримуємо файл з найкращою якістю

        # Завантажуємо фото локально
        file_path = f"{photo_file.file_id}.jpg"
        photo_file.download(file_path)

        # Формуємо підпис до фото, щоб відправити разом з ID та іменем користувача
        caption_text = f"Фото від користувача:\nID: {user_id}\nUsername: {username}"

        # Використовуємо другого бота для пересилання фото з підписом до адміністратора
        with open(file_path, 'rb') as img:
            second_bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=img, caption=caption_text)

        # Відповідь користувачеві
        update.message.reply_text("Ваш скріншот відправлено на перевірку.")

        # Оновлюємо статус користувача
        update_user_state('wait')

        # Видаляємо локально збережене фото після відправки
        os.remove(file_path)
    else:
        pass

def clear_state_files():
    # Очищаємо файл language_state.csv
    with open("language_state.csv", "w") as file:
        pass  # Очищає файл, зберігаючи його порожнім

    # Очищаємо файл user_state.csv
    with open("user_state.csv", "w") as file:
        pass  # Очищає файл, зберігаючи його порожнім

def main():
    """Start the bot."""
    # Initialize the Updater with your bot's TOKEN
    updater = Updater(TOKEN, use_context=True)
    # test
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    clear_state_files()

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
        if user_activity_and_access(update, context):

            update_menu_state('mrkt_overview')
            send_market_overview(update, context)
        else:
            pass

    def stock_company_info_func_button_call(update: Update, context: CallbackContext) -> None:
        if user_activity_and_access(update, context):
            symbol_info(update, context)
            update_menu_state('stock_company_info')
        else:
            pass

    def stock_signal_func_button_call(update: Update, context: CallbackContext) -> None:
        if user_activity_and_access(update, context):
            update_menu_state('stock_signal')
            signal_list_for_user(update, context)
        else:
            pass

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

    schedule_func_call(all_signals_calc_run, 22, 00)
    schedule_func_call(send_daily_events, 7, 30)
    schedule_func_call(send_day_end_info, 15, 00)

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

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
