import datetime
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, \
    ConversationHandler

import config
import strings
from button_states import MenuButtonStates, ConversationStates
from database.db_operations import db_helper

from test_excursion import Test_Excursion

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""

    if db_helper.get_user_by_id(update.effective_user.id) is None:
        logger.info("Добавление нового пользователя в базу данных")

        db_helper.add_new_user(
            user_id=update.effective_user.id,
            subscription_type=-1,
            subscription_end_date=datetime.date.min,
            excursions_left=0
        )

        keyboard = [
            [
                InlineKeyboardButton(strings.START_ADVENTURE_BUTTON_TEXT, callback_data=MenuButtonStates.MAIN_MENU)
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(strings.GREETING_TEXT, reply_markup=reply_markup)
        return ConversationStates.MAIN_MENU
    else:
        logger.info("Пользователь обнаружен в базе данных")
        return await main_menu(update, context)


async def buttons_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery"""
    query = update.callback_query
    await query.answer()
    match query.data:
        case MenuButtonStates.MAIN_MENU:
            await main_menu(update, context)
        case MenuButtonStates.CHOOSE_EXCURSION:
            await choose_excursion(update, context)
        case MenuButtonStates.ADDITIONAL_INFORMATION:
            await additional_information(update, context)
        case MenuButtonStates.TARIFFS:
            await tariffs(update, context)
        case MenuButtonStates.GET_STATUS:
            await get_tariff_status(update, context)
        case MenuButtonStates.NOT_IMPLEMENTED:
            await context.bot.send_message(text="Данная функция находится в разработке...",
                                           chat_id=update.effective_chat.id)


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [
            InlineKeyboardButton(strings.CHOOSE_EXCURSION_BUTTON_TEXT, callback_data=MenuButtonStates.CHOOSE_EXCURSION)
        ],
        [
            InlineKeyboardButton(strings.TARIFFS_BUTTON_TEXT, callback_data=MenuButtonStates.TARIFFS),
            InlineKeyboardButton(strings.MY_STATUS_BUTTON_TEXT, callback_data=MenuButtonStates.GET_STATUS)
        ],
        [
            InlineKeyboardButton(strings.ADDITIONAL_BUTTON_TEXT, callback_data=MenuButtonStates.ADDITIONAL_INFORMATION)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(text=strings.MAIN_MENU_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)
    return ConversationStates.MAIN_MENU


async def get_tariff_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuButtonStates.MAIN_MENU)
        ],
    ])
    user = db_helper.get_user_by_id(update.effective_user.id)
    if user.subscription_type == -1:
        text = strings.NO_TARIFF_TEXT
    elif user.subscription_end_date < datetime.date.today():
        text = strings.TARIFF_EXPIRES_TEXT
    else:
        text = (strings.TARIFF_INFO_TEXT_ARR[0] + strings.TARIFFS_ARR[user.subscription_type] +
                strings.TARIFF_INFO_TEXT_ARR[1] + user.subscription_end_date.strftime('%Y-%m-%d') +
                strings.TARIFF_INFO_TEXT_ARR[2] + str(user.excursions_left))
    await context.bot.send_message(text=text,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)


async def choose_excursion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Сделать выпадающий список экскурсий.
    await Test_Excursion.preview(update, context)


async def additional_information(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuButtonStates.MAIN_MENU)
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(text=strings.ADDITIONAL_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)


async def tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Реализовать систему тарифов (после оплаты)
    keyboard = [
        [
            InlineKeyboardButton(strings.TARIFF_ONE_TEXT, callback_data=MenuButtonStates.NOT_IMPLEMENTED),
            InlineKeyboardButton(strings.TARIFF_TWO_TEXT, callback_data=MenuButtonStates.NOT_IMPLEMENTED),
            InlineKeyboardButton(strings.TARIFF_THREE_TEXT, callback_data=MenuButtonStates.NOT_IMPLEMENTED)
        ],
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuButtonStates.MAIN_MENU)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo="tariffs.png")
    await context.bot.send_message(text=strings.TARIFFS_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)


async def stop_excursion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await main_menu(update, context)
    return ConversationHandler.END


async def unknown_comand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancels and ends the conversation."""
    await context.bot.send_message(text=strings.UNKNOWN_COMMAND_TEXT,
                                   chat_id=update.effective_chat.id)


def main() -> None:
    """Starts the bot."""
    # Create the Application
    application = Application.builder().token(config.API_TOKEN).build()

    main_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), MessageHandler(filters.ALL, start)],
        states={
            ConversationStates.MAIN_MENU: [
                CommandHandler("start", start),
                CallbackQueryHandler(buttons_manager),
                CommandHandler("testexc", Test_Excursion.go_to_test_excursion),
                MessageHandler(filters.ALL, start)
            ],
            ConversationStates.TEST_EXCURSION: [
                MessageHandler(filters.TEXT, Test_Excursion.process_waypoints),
                CallbackQueryHandler(Test_Excursion.excursion_buttons_manager),

            ]
        },
        fallbacks=[]
    )

    application.add_handler(main_conversation_handler)

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

# TODO: Сделать систему оповещений о продлении тарифа
