from telegram import KeyboardButton, ReplyKeyboardMarkup
from general.user_list import get_user_watchlist
from state_update_menu import update_menu_state
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from language_state import language_state


def get_watchlist_inline_keyboard(symbol):
    language = language_state().rstrip('\n')
    if language == "Ukrainian":
        keyboard = [
            [
                InlineKeyboardButton("➕ Додати у Watchlist", callback_data=f"add_{symbol}"),
                InlineKeyboardButton("➖ Видалити з Watchlist", callback_data=f"remove_{symbol}")
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("➕ Add to Watchlist", callback_data=f"add_{symbol}"),
                InlineKeyboardButton("➖ Remove from Watchlist", callback_data=f"remove_{symbol}")
            ]
        ]
    return InlineKeyboardMarkup(keyboard)


def create_start_keyboard():
    language = language_state().rstrip('\n')
    if language == "Ukrainian":
        keyboard = [
            [KeyboardButton("📋 Меню")],
            [KeyboardButton("🌐 Мова")],
            [KeyboardButton("ℹ️ Про бота")]
        ]
    else:
        keyboard = [
            [KeyboardButton("📋 Menu")],
            [KeyboardButton("🌐 Language")],
            [KeyboardButton("ℹ️ About Bot")]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def watchlist_keyboard(update, context):
    language = language_state().rstrip('\n')
    if language == "Ukrainian":
        keyboard = [
            [KeyboardButton("👀 Показати мій Watchlist")],
            [KeyboardButton("➕ Додати у Watchlist")],
            [KeyboardButton("➖ Видалити з Watchlist")],
            [KeyboardButton("Назад")]
        ]
        menu_text = "Меню Watchlist:\n— Додавайте, переглядайте або видаляйте акції зі свого Watchlist!"
    else:
        keyboard = [
            [KeyboardButton("👀 Show My Watchlist")],
            [KeyboardButton("➕ Add to Watchlist")],
            [KeyboardButton("➖ Remove from Watchlist")],
            [KeyboardButton("Back")]
        ]
        menu_text = "Watchlist Menu:\n— Додавайте, переглядайте або видаляйте акції зі свого Watchlist!"
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=menu_text,
        reply_markup=reply_markup
    )
    update_menu_state('watchlist')


def create_back_keyboard():
    language = language_state().rstrip('\n')
    button = "Назад" if language == "Ukrainian" else "Back"
    return ReplyKeyboardMarkup([[KeyboardButton(button)]], resize_keyboard=True)


def stock_keyboard(update, context):
    language = language_state().rstrip('\n')
    context.user_data['menu_stack'] = context.user_data.get('menu_stack', []) + ['stock']
    if language == "Ukrainian":
        keyboard = [
            [KeyboardButton("🏢 Інформація про компанію")],
            [KeyboardButton("📑 Watchlist")],
            [KeyboardButton("📊 Сигнали акцій")],
            [KeyboardButton("Назад")]
        ]
        text = "Ласкаво просимо у розділ Акцій"
    else:
        keyboard = [
            [KeyboardButton("🏢 Company information")],
            [KeyboardButton("📑 Watchlist")],
            [KeyboardButton("📊 Stock Signals")],
            [KeyboardButton("Back")]
        ]
        text = "Welcome to Stock"
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
    update_menu_state('stock')


def crypto_keyboard(update, context):
    context.user_data['menu_stack'] = context.user_data.get('menu_stack', []) + ['crypto']
    keyboard = [
        [KeyboardButton("📈 Crypto Market Overview")],
        [KeyboardButton("🪙 Cryptocurrencies info")],
        [KeyboardButton("📉 Crypto Signals")],
        [KeyboardButton("Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to Crypto", reply_markup=reply_markup)
    update_menu_state('crypto')


def forex_keyboard(update, context):
    context.user_data['menu_stack'] = context.user_data.get('menu_stack', []) + ['forex']
    keyboard = [
        [KeyboardButton("📈 Forex Market Overview")],
        [KeyboardButton("💱 Pairs info")],
        [KeyboardButton("📉 Forex Signals")],
        [KeyboardButton("Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to Forex", reply_markup=reply_markup)
    update_menu_state('forex')


def language_keyboard(update, context):
    context.user_data['menu_stack'] = context.user_data.get('menu_stack', []) + ['settings']
    keyboard = [
        [KeyboardButton("🇺🇦 Ukrainian")],
        [KeyboardButton("🇬🇧 English")],
        [KeyboardButton("Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Виберіть мову/Choose a language',
                             reply_markup=reply_markup)
    update_menu_state('settings')


def show_watchlist(update, context):
    user_id = update.effective_user.id
    tickers = get_user_watchlist(user_id)
    if tickers:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ваш Watchlist:\n" + "\n".join(f"• {t}" for t in tickers)
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ваш Watchlist порожній."
        )
