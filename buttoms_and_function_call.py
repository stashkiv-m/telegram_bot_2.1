from bot import start, menu
from keyboards import *
from state_update_menu import update_menu_state


# Main menu buttoms

def test_but():
    print('Hello')


def about_bot(update, context):
    context.user_data['menu_stack'] = context.user_data.get('menu_stack', []) + ['about_bot']
    keyboard = [
        [KeyboardButton("⬅️ Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    about_text_ua = (
        "🇺🇦 *Версія 1.0*\n"
        "🔗 [t.me/stashkiv_mykhailo](https://t.me/stashkiv_mykhailo)\n\n"
        "🤖 _Бот використовує оптимізовані індикатори MACD, щоб обирати найкращі моменти для купівлі чи продажу акцій._\n\n"
        "📊 *Що таке MACD?*\n"
        "MACD — простий, але потужний індикатор, який показує, коли найкраще купувати чи продавати актив, аналізуючи рух цін.\n\n"
        "🕰️ *Що таке бектест?*\n"
        "Бектест — це перевірка стратегії на минулих даних. Бот тестує всі свої сигнали на історичних цінах, щоб ти отримував лише перевірені рекомендації.\n\n"
        "🛠️ *Як це працює?*\n"
        "1️⃣ Аналізує акції через MACD\n"
        "2️⃣ Тестує сигнали на історичних даних (бектест)\n"
        "3️⃣ Надсилає тобі результат\n\n"
        "💡 *Для чого це?*\n"
        "Щоб ти міг приймати розумні інвестиційні рішення без зайвого стресу!"
    )

    about_text_en = (
        "🇬🇧 *Version 1.0*\n"
        "🔗 [t.me/stashkiv_mykhailo](https://t.me/stashkiv_mykhailo)\n\n"
        "🤖 _The bot uses optimized MACD indicators to pick the best moments to buy or sell stocks._\n\n"
        "📊 *What is MACD?*\n"
        "MACD is a simple but powerful indicator that shows the best times to buy or sell assets by analyzing price movement.\n\n"
        "🕰️ *What is backtest?*\n"
        "Backtest means testing a strategy on historical data. The bot tests all signals on past prices, so you only get proven recommendations.\n\n"
        "🛠️ *How does it work?*\n"
        "1️⃣ Analyzes stocks with MACD\n"
        "2️⃣ Tests signals on historical data (backtest)\n"
        "3️⃣ Sends you the result\n\n"
        "💡 *Why?*\n"
        "So you can make smart investment decisions without extra stress!"
    )

    # Визначаємо мову незалежно від регістру та пробілів
    lang = language_state().strip().lower()
    print(f"User language is: {lang!r}")  # Для дебагу, потім можна прибрати

    if lang in ('ukrainian', 'ua', 'uk'):
        text = about_text_ua
    else:
        text = about_text_en

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    update_menu_state('about_bot')


def test_button(update, context):
    update.message.reply_text("This is a test response.")


def back_function(update, context):
    menu_stack = context.user_data.get('menu_stack', [])
    if len(menu_stack) > 1:
        menu_stack = list(dict.fromkeys(menu_stack))  # Remove duplicates
        menu_stack.pop()  # Remove current menu
        # Send user back to previous menu
        previous_menu = menu_stack[-1]
        if previous_menu == 'menu':
            menu(update, context)
        elif previous_menu == 'forex':
            test_button(update, context)
        elif previous_menu == 'crypto':
            test_button(update, context)
        else:
            start(update, context)
        # Update menu stack
        context.user_data['menu_stack'] = menu_stack
    else:
        # Send user back to start menu
        start(update, context)
