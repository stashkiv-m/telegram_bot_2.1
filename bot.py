import logging
import os
from telegram import Update, Bot, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater
from buttoms_and_function_call import *
from developer_functions.general_dev.send_signal_to_user import signal_list_for_user
from general.daily_information import send_daily_events, send_day_end_info
from general.universal_functions import symbol_info, show_watchlist_with_changes
from general.user_list import user_activity_and_access, add_user_activity, remove_from_watchlist, add_to_watchlist
from keyboards import *
from language_state import update_language_state, language_state
from run_all_siganlas_calc import schedule_func_call, all_signals_calc_run
from state_update_menu import update_menu_state, menu_state
from user_state import update_user_state, user_state
from general.user_list import add_to_watchlist, remove_from_watchlist  # якщо ці функції в цьому файлі
from telegram.ext import CallbackQueryHandler


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
        "🔥 You’ve received **full free access** to all bot features — forever!\n\n"
        "https://t.me/stashkiv_mykhailo\n\n"
        "🤖 This bot automatically analyzes the financial markets and helps you make smarter investment decisions:\n"
        "- 📈 Stock analysis: fundamental and technical indicators.\n"
        "- 📊 Buy/sell signals based on MACD and MA indicators.\n"
        "- 🧠 Clear explanations of each metric.\n"
        "- 🗂 Classification by industry and profitability.\n"
        "- 🔔 Daily economic event alerts.\n\n"
        "💡 Soon: support for crypto and forex.\n"
        "🚫 The bot doesn’t guarantee profits, but helps you invest more wisely.\n\n"
        "🙌 Like the bot? **Share it with friends** — that’s the best way to support the project!"
    ) if language != 'Ukrainian' else (
        "🔥 Ви отримали **повний безкоштовний доступ** до всіх функцій бота — назавжди!\n\n"
        "https://t.me/stashkiv_mykhailo\n\n"
        "🤖 Цей бот автоматично аналізує фінансові ринки та допомагає приймати обґрунтовані інвестиційні рішення:\n"
        "- 📈 Фундаментальний і технічний аналіз акцій.\n"
        "- 📊 Сигнали купівлі/продажу (MACD, MA).\n"
        "- 🧠 Прості пояснення кожного показника.\n"
        "- 🗂 Класифікація за галузями та прибутковістю.\n"
        "- 🔔 Щоденні сповіщення про економічні події.\n\n"
        "💡 Незабаром — підтримка крипти та форексу.\n"
        "🚫 Бот не гарантує прибутків, але допомагає інвестувати розумніше.\n\n"
        "🙌 Подобається бот? **Поділіться з друзями** — це найкраща підтримка проєкту!"
    )

    context.bot.send_message(chat_id=update.effective_chat.id, text=greeting, reply_markup=create_start_keyboard())
    update_menu_state('start')


# Menu handler

# def menu(update: Update, context: CallbackContext):
#     context.user_data['menu_stack'] = ['menu']
#     if not ACCESS_CHECK_ENABLED or user_activity_and_access(update, context):
#         keyboard = ReplyKeyboardMarkup(
#             [[KeyboardButton("Stock")], [KeyboardButton("Back")]], resize_keyboard=True
#         )
#         context.bot.send_message(chat_id=update.effective_chat.id, text='Menu:', reply_markup=keyboard)
#         update_user_state('active')
#         update_menu_state('menu')

def menu(update, context):
    language = language_state().rstrip('\n')
    context.user_data['menu_stack'] = context.user_data.get('menu_stack', []) + ['stock']
    if language == "Ukrainian":
        keyboard = [
            [KeyboardButton("🏢 Інформація про компанію")],
            [KeyboardButton("📑 Watchlist")],
            [KeyboardButton("📊 Сигнали акцій")],
            [KeyboardButton("⬅️ Назад")]
        ]
        text = "Ласкаво просимо у розділ Акцій"
    else:
        keyboard = [
            [KeyboardButton("🏢 Company information")],
            [KeyboardButton("📑 Watchlist")],
            [KeyboardButton("📊 Stock Signals")],
            [KeyboardButton("⬅️ Back")]
        ]
        text = "Welcome to Stock"
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
    update_menu_state('stock')

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


def watchlist_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username
    data = query.data  # типу "add_AAPL" або "remove_AAPL"
    action, ticker = data.split('_', 1)

    if action == "add":
        if add_to_watchlist(user_id, username, ticker):
            query.answer("Додано до Watchlist!")
        else:
            query.answer("Вже у вашому Watchlist!")
    elif action == "remove":
        if remove_from_watchlist(user_id, ticker):
            query.answer("Видалено з Watchlist!")
        else:
            query.answer("Цього тікера немає у вашому Watchlist.")


# Clear user states

def clear_state_files():
    open("language_state.csv", "w").close()
    open("user_state.csv", "w").close()


# Main function

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CallbackQueryHandler(watchlist_callback))

    clear_state_files()

    # Register command handlers
    def regex_multilang(*variants):
        return r'^(' + '|'.join(variants) + ')$'

    dp.add_handler(CommandHandler("start", start))


    # Меню (Menu)
    dp.add_handler(MessageHandler(
        Filters.regex(regex_multilang("📋 Menu", "📋 Меню")),
        menu
    ))

    # Про бота (About Bot)
    dp.add_handler(MessageHandler(
        Filters.regex(regex_multilang("ℹ️ About Bot", "ℹ️ Про бота")),
        lambda u, c: about_bot(u, c) or update_menu_state('about')
    ))

    # Мова (Language)
    dp.add_handler(MessageHandler(
        Filters.regex(regex_multilang("🌐 Language", "🌐 Мова")),
        lambda u, c: language_keyboard(u, c) or update_menu_state('language')
    ))

    # Українська / English
    dp.add_handler(MessageHandler(
        Filters.regex(r'^🇺🇦 Ukrainian$'),
        lambda u, c: update_language_state('Ukrainian') or c.bot.send_message(chat_id=u.effective_chat.id,
                                                                              text="Мова змінена на українську 🇺🇦")
    ))
    dp.add_handler(MessageHandler(
        Filters.regex(r'^🇬🇧 English$'),
        lambda u, c: update_language_state('English') or c.bot.send_message(chat_id=u.effective_chat.id,
                                                                            text="Language changed to English. 🇬🇧")
    ))

    # Stock розділ
    dp.add_handler(MessageHandler(
        Filters.regex(regex_multilang("Stock", "Акції")),
        lambda u, c: stock_keyboard(u, c) or update_menu_state('stock_menu')
    ))
    dp.add_handler(MessageHandler(
        Filters.regex(regex_multilang("🏢 Company information", "🏢 Інформація про компанію")),
        lambda u, c: symbol_info(u, c) or update_menu_state('stock_company_info')
    ))
    dp.add_handler(MessageHandler(
        Filters.regex(regex_multilang("📊 Stock Signals", "📊 Сигнали акцій")),
        lambda u, c: update_menu_state('stock_signal') or signal_list_for_user(u, c)
    ))

    # Watchlist розділ
    dp.add_handler(MessageHandler(
        Filters.regex(regex_multilang("📑 Watchlist", "📑 Watchlist")),  # назва однакова, залишено для сумісності
        show_watchlist_with_changes
    ))
    dp.add_handler(MessageHandler(
        Filters.regex(regex_multilang("👀 Show My Watchlist", "👀 Показати мій Watchlist")),
        show_watchlist_with_changes
    ))
    dp.add_handler(MessageHandler(
        Filters.regex(regex_multilang("➕ Add to Watchlist", "➕ Додати у Watchlist")),
        lambda u, c: c.bot.send_message(chat_id=u.effective_chat.id, text="Введіть тікер для додавання у Watchlist:")
    ))
    dp.add_handler(MessageHandler(
        Filters.regex(regex_multilang("➖ Remove from Watchlist", "➖ Видалити з Watchlist")),
        lambda u, c: c.bot.send_message(chat_id=u.effective_chat.id, text="Введіть тікер для видалення з Watchlist:")
    ))

    # Back (Назад)
    dp.add_handler(MessageHandler(
        Filters.regex(regex_multilang("⬅️ Back", "⬅️ Назад")),
        back_function
    ))

    # Додай сюди інші кнопки та розділи за аналогією (crypto, forex, інше меню...)

    # Schedulers
    schedule_func_call(all_signals_calc_run, 15, 1)
    schedule_func_call(send_daily_events, 7, 30)
    schedule_func_call(send_day_end_info, 15, 0)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
