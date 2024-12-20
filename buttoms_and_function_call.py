from bot import start, menu
from keyboards import *
from state_update_menu import update_menu_state


# Main menu buttoms

def test_but():
    print('Hello')


def about_bot(update, context):
    context.user_data['menu_stack'] = context.user_data.get('menu_stack', []) + ['about_bot']
    keyboard = [
        [KeyboardButton("/start")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Version 1.0 '
                                                                    'https://t.me/stashkiv_mykhailo.',
                             reply_markup=reply_markup)
    update_menu_state('about_bot')


def test_button(update, context):
    update.message.reply_text("This is a test response.")


def back_function(update, context):
    menu_stack = context.user_data.get('menu_stack', [])
    print(menu_stack)
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
