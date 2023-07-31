import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

import config
import strings
from test_excursion import test_excursion

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    # TODO: Сделать так, чтобы приветственное сообщение вызывалось только первый раз.
    keyboard = [
        [
            InlineKeyboardButton(strings.START_ADVENTURE_BUTTON_TEXT, callback_data=ButtonStates.MAIN_MENU)
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(strings.GREETING_TEXT, reply_markup=reply_markup)


class ButtonStates:
    MAIN_MENU = "main_menu"
    CHOOSE_EXCURSION = "choose_excursion"
    ADDITIONAL_INFORMATION = "additional_information"
    TARIFFS = "tariffs"
    NONE = "_"


async def buttons_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery"""
    query = update.callback_query
    await query.answer()
    match query.data:
        case ButtonStates.MAIN_MENU:
            await main_menu(update, context)
        case ButtonStates.CHOOSE_EXCURSION:
            await choose_excursion(update, context)
        case ButtonStates.ADDITIONAL_INFORMATION:
            await additional_information(update, context)
        case ButtonStates.TARIFFS:
            await tariffs(update, context)
        case ButtonStates.NONE:
            pass


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(strings.CHOOSE_EXCURSION_BUTTON_TEXT, callback_data=ButtonStates.CHOOSE_EXCURSION)
        ],
        [
            InlineKeyboardButton(strings.TARIFFS_BUTTON_TEXT, callback_data=ButtonStates.TARIFFS),
        ],
        [
            InlineKeyboardButton(strings.ADDITIONAL_BUTTON_TEXT, callback_data=ButtonStates.ADDITIONAL_INFORMATION)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(text=strings.MAIN_MENU_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)


async def choose_excursion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(text=strings.CHOOSE_EXCURSION_TEXT,
                                   chat_id=update.effective_chat.id)


async def additional_information(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=ButtonStates.MAIN_MENU)
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(text=strings.ADDITIONAL_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)


async def tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(strings.TARIFF_ONE_BUTTON_TEXT, callback_data=ButtonStates.NONE),
            InlineKeyboardButton(strings.TARIFF_TWO_BUTTON_TEXT, callback_data=ButtonStates.NONE),
            InlineKeyboardButton(strings.TARIFF_THREE_BUTTON_TEXT, callback_data=ButtonStates.NONE)
        ],
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=ButtonStates.MAIN_MENU)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo="tariffs.png")
    await context.bot.send_message(text=strings.TARIFFS_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)


def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(config.API_TOKEN).build()

    # Adding handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("testexc", test_excursion))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    application.add_handler(CallbackQueryHandler(buttons_manager))

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

# TODO: Сделать выпадающий список со всеми экскурсиями, сделать саму экскурсию, сделать тарифы.
