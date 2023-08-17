import logging
from sqlite3 import Date

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, \
    ConversationHandler

import config
import strings
from database.db_operations import db_helper

from test_excursion import Test_Excursion

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""

    if db_helper.get_user_by_id(update.effective_user.id) is None:
        logger.debug("Добавление нового пользователя в базу данных")

        db_helper.add_new_user(
                        user_id=update.effective_user.id,
                        subscription_type=0,
                        subscription_start_date=Date.min,
                        excursions_left=0
        )

        keyboard = [
            [
                InlineKeyboardButton(strings.START_ADVENTURE_BUTTON_TEXT, callback_data=ButtonStates.MAIN_MENU)
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(strings.GREETING_TEXT, reply_markup=reply_markup)
    else:
        logger.debug("Пользователь обнаружен в базе данных")
        await main_menu(update, context)


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


async def stop_excursion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""

    return ConversationHandler.END


async def unknown_comand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await context.bot.send_message(text=strings.UNKNOWN_COMMAND_TEXT,
                                   chat_id=update.effective_chat.id)


def main() -> None:
    """Starts the bot."""

    # Create the Application
    application = Application.builder().token(config.API_TOKEN).build()

    # Adding handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons_manager))

    # Adding test excursion conv_handler
    test_exc_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("testexc", Test_Excursion.description)],
        states={
            Test_Excursion.DESCRIPTION: [MessageHandler(filters.Regex("^Начать экскурсию$"), Test_Excursion.begin)],
            Test_Excursion.PROCESS_EXCURSION: [MessageHandler(filters.ALL, Test_Excursion.begin)],
        },
        fallbacks=[CommandHandler("stop", stop_excursion)],
    )

    application.add_handler(test_exc_conv_handler)

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_comand))

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
