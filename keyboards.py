from telegram import KeyboardButton, ReplyKeyboardMarkup
from state_update_menu import update_menu_state


def create_start_keyboard():
    keyboard = [
        [KeyboardButton("📋 Menu")],
        [KeyboardButton("🌐 Language")],
        [KeyboardButton("ℹ️ About Bot")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def create_back_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("Back")]], resize_keyboard=True)


def stock_keyboard(update, context):
    context.user_data['menu_stack'] = context.user_data.get('menu_stack', []) + ['stock']
    keyboard = [
        [KeyboardButton("🏢 Company information")],
        [KeyboardButton("📊 Stock Signals")],
        [KeyboardButton("Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to Stock", reply_markup=reply_markup)
    update_menu_state('stock')


def watchlist_keyboard(update, context):
    context.user_data['watchlist'] = context.user_data.get('watchlist', []) + ['stock']
    keyboard = [
        [KeyboardButton("➕ Add")],
        [KeyboardButton("➖ Remove")],
        [KeyboardButton("Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to Watchlist", reply_markup=reply_markup)
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