from telegram import KeyboardButton, ReplyKeyboardMarkup
from state_update_menu import update_menu_state


def create_start_keyboard():
    keyboard = [
        [KeyboardButton("About Bot")],
        [KeyboardButton("Help")],
        [KeyboardButton("Menu")]
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)


def menu(update, context):
    context.user_data['menu_stack'] = ['menu']
    keyboard = [
        [KeyboardButton("Stock")],
        [KeyboardButton("Forex")],
        [KeyboardButton("Crypto")],
        [KeyboardButton("Back")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Меню:', reply_markup=reply_markup)
    update_menu_state('menu')


def stock_keyboard(update, context):
    # Оновлюємо стек меню
    context.user_data['menu_stack'] = context.user_data.get('menu_stack', []) + ['stock']

    # Створюємо клавіатуру
    keyboard = [
        [KeyboardButton("Stocks Market Overview")],
        [KeyboardButton("Company information")],
        [KeyboardButton("Stock Signals")],
        [KeyboardButton("Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    # Надсилаємо повідомлення з інформацією про акції
    context.bot.send_message(chat_id=update.effective_chat.id,  text="Welcome to Stock",
                             reply_markup=reply_markup)
    # Оновлення стану меню
    update_menu_state('stock')


def crypto_keyboard(update, context):
    # Оновлюємо стек меню
    context.user_data['menu_stack'] = context.user_data.get('menu_stack', []) + ['crypto']

    # Створюємо клавіатуру
    keyboard = [
        [KeyboardButton("Crypto Market Overview")],
        [KeyboardButton("Cryptocurrencies info")],
        [KeyboardButton("Crypto Signals")],
        [KeyboardButton("Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    # Надсилаємо повідомлення з інформацією про акції
    context.bot.send_message(chat_id=update.effective_chat.id,  text="Welcome to Crypto",
                             reply_markup=reply_markup)

    # Оновлення стану меню
    update_menu_state('crypto')


def forex_keyboard(update, context):
    # Оновлюємо стек меню
    context.user_data['menu_stack'] = context.user_data.get('menu_stack', []) + ['forex']

    # Створюємо клавіатуру
    keyboard = [
        [KeyboardButton("Forex Market Overview")],
        [KeyboardButton("Pairs info")],
        [KeyboardButton("Forex Signals")],
        [KeyboardButton("Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    # Надсилаємо повідомлення з інформацією про акції
    context.bot.send_message(chat_id=update.effective_chat.id,  text="Welcome to Forex",
                             reply_markup=reply_markup)
    # Оновлення стану меню
    update_menu_state('forex')
