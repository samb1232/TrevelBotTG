import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, \
    ConversationHandler

import config
from enumerations import ConversationStates
from menu_functions import start, unknown_callback_handler, buttons_manager
from test_excursion import Test_Excursion

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

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
                CallbackQueryHandler(buttons_manager),
                CommandHandler("testexc", Test_Excursion.description),
                MessageHandler(filters.ALL, start)
            ],
            ConversationStates.TEST_EXCURSION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, Test_Excursion.process_waypoints),
                CallbackQueryHandler(Test_Excursion.excursion_buttons_manager),
                CommandHandler("stop", Test_Excursion.stop_excursion)
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

