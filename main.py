import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, \
    ConversationHandler

import config
from enumerations import ConversationStates
from menu_functions import start, unknown_callback_handler, callback_buttons_manager
from test_excursion import excursion_test_1, excursion_test_2

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("database.db_operations").setLevel(logging.DEBUG)
logging.getLogger("excursion").setLevel(logging.DEBUG)


logger = logging.getLogger(__name__)


def main() -> None:
    """Starts the bot."""
    # Create the Application
    application = Application.builder().token(config.API_TOKEN).build()

    main_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      MessageHandler(filters.ALL, start),
                      CallbackQueryHandler(unknown_callback_handler)],
        states={
            ConversationStates.MAIN_MENU: [
                CommandHandler("start", start),
                CallbackQueryHandler(callback_buttons_manager),
                CommandHandler("testexc1", excursion_test_1.description),
                CommandHandler("testexc2", excursion_test_2.description),
                MessageHandler(filters.ALL, start)
            ],
            ConversationStates.TEST_EXCURSION_1: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, excursion_test_1.process_waypoints),
                CallbackQueryHandler(excursion_test_1.excursion_callback_buttons_manager),
                CommandHandler("stop", excursion_test_1.stop_excursion)
            ],
            ConversationStates.TEST_EXCURSION_2: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, excursion_test_2.process_waypoints),
                CallbackQueryHandler(excursion_test_2.excursion_callback_buttons_manager),
                CommandHandler("stop", excursion_test_2.stop_excursion)
            ]
        },
        fallbacks=[]
    )

    application.add_handler(main_conversation_handler)

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()


# TODO: Реализовать поиск экскурсий по inlineHandler.
#  Все экскурсии будут высвечиваться, если ввести тег бота в поле ввода.
