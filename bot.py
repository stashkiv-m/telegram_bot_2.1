import logging
import os
from telegram import Update, Bot, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater
from buttoms_and_function_call import *
from developer_functions.general_dev.send_signal_to_user import signal_list_for_user
from general.daily_information import send_daily_events, send_day_end_info
from general.universal_functions import symbol_info
from general.user_list import user_activity_and_access, add_user_activity
from keyboards import *
from language_state import update_language_state, language_state
from run_all_siganlas_calc import schedule_func_call, all_signals_calc_run
from state_update_menu import update_menu_state, menu_state
from stock.market_overwiev import send_market_overview
from user_state import update_user_state, user_state

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token
TOKEN = '7749471664:AAEp85bkb0szrSBDso9bxU2FSy8JU0RVSEY'
ACCESS_CHECK_ENABLED = False


# Log new user
def log_new_user(update: Update):
    user = update.effective_user
    user_id = user.id
    username = user.username or "No Username"
    first_name = user.first_name or ""
    last_name = user.last_name or ""

    with open("user_log.csv", "a", encoding='utf-8') as f:
        f.write(f"{user_id},{username},{first_name},{last_name}\n")


# Start command

def start(update: Update, context: CallbackContext) -> None:
    log_new_user(update)
    user_id = update.effective_user.id
    username = update.effective_user.username or "No Username"
    add_user_activity(user_id, username)  # 🟢 Записуємо в таблицю
    context.user_data['menu_stack'] = ['start']
    language = language_state().rstrip('\n')

    greeting = (
        "https://t.me/stashkiv_mykhailo\n\n"
        "This bot analyzes financial markets and provides useful information for making decisions.\n"
        "- 📈 Stock analysis: fundamental and technical indicators.\n"
        "- 📊 Buy/sell signals based on MACD and MA indicators.\n"
        "- 🗂 Industry/profitability classification.\n"
        "- 🔔 Economic event alerts.\n\n"
        "Crypto and forex coming soon.\n"
        "The bot doesn't guarantee profits."
    ) if language != 'Ukrainian' else (
        "https://t.me/stashkiv_mykhailo\n\n"
        "Цей бот аналізує фінансові ринки та надає корисну інформацію.\n"
        "- 📈 Фундаментальний і технічний аналіз акцій.\n"
        "- 📊 Сигнали купівлі/продажу (MACD, MA).\n"
        "- 🗂 Класифікація за галузями та прибутковістю.\n"
        "- 🔔 Економічний календар.\n\n"
        "Незабаром крипта і форекс.\n"
        "Бот не гарантує прибутків."
    )

    context.bot.send_message(chat_id=update.effective_chat.id, text=greeting, reply_markup=create_start_keyboard())
    update_menu_state('start')


# Menu handler

def menu(update: Update, context: CallbackContext):
    context.user_data['menu_stack'] = ['menu']
    if not ACCESS_CHECK_ENABLED or user_activity_and_access(update, context):
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("Stock")], [KeyboardButton("Back")]], resize_keyboard=True
        )
        context.bot.send_message(chat_id=update.effective_chat.id, text='Menu:', reply_markup=keyboard)
        update_user_state('active')
        update_menu_state('menu')


# Handle photo

def handle_photo(update: Update, context: CallbackContext) -> None:
    if user_state().rstrip('\n') in ('guest', 'expired'):
        ADMIN_CHAT_ID = 1440645936
        second_bot = Bot(token='7561762364:AAEH5uobIEzbZ3CQl01fVPnBUKAw9iUDeJM')

        user = update.message.from_user
        user_id = user.id
        username = user.username or "No Username"
        photo_file = update.message.photo[-1].get_file()
        file_path = f"{photo_file.file_id}.jpg"
        photo_file.download(file_path)

        caption = f"New payment notification!\nID: {user_id}\nUsername: {username}"
        with open(file_path, 'rb') as img:
            second_bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=img, caption=caption)

        update.message.reply_text("Ваш скріншот відправлено на перевірку.")
        update_user_state('wait')
        os.remove(file_path)


# Clear user states

def clear_state_files():
    open("language_state.csv", "w").close()
    open("user_state.csv", "w").close()


# Main function

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    clear_state_files()

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(MessageHandler(Filters.regex(r'^📋 Menu$'), menu))
    dp.add_handler(MessageHandler(Filters.regex(r'^ℹ️ About Bot$'), lambda u, c:
    about_bot(u, c) or update_menu_state('about')))
    dp.add_handler(MessageHandler(Filters.regex(r'^🌐 Language'), lambda u, c: language_keyboard(u, c) or update_menu_state('language')))
    dp.add_handler(MessageHandler(Filters.regex(r'^🇺🇦 Ukrainian'), lambda u, c: update_language_state('Ukrainian') or c.bot.send_message(chat_id=u.effective_chat.id, text="Мова змінена на українську 🇺🇦")))
    dp.add_handler(MessageHandler(Filters.regex(r'^🇬🇧 English'), lambda u, c: update_language_state('English') or c.bot.send_message(chat_id=u.effective_chat.id, text="Language changed to English. 🇬🇧")))

    dp.add_handler(MessageHandler(Filters.regex(r'^Stock$'), lambda u, c: stock_keyboard(u, c) or update_menu_state('stock_menu')))
    dp.add_handler(MessageHandler(Filters.regex(r'^🏢 Company information$'), lambda u, c: symbol_info(u, c) or update_menu_state('stock_company_info')))
    dp.add_handler(MessageHandler(Filters.regex(r'^📊 Stock Signals$'), lambda u, c: signal_list_for_user(u, c) or update_menu_state('stock_signal')))
    dp.add_handler(MessageHandler(Filters.regex(r'^Back$'), back_function))

    # Schedulers
    schedule_func_call(all_signals_calc_run, 15, 1)
    schedule_func_call(send_daily_events, 7, 30)
    schedule_func_call(send_day_end_info, 15, 0)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
