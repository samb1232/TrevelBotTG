import datetime
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

import strings
from button_states import MenuButtonStates, ExcursionButtonStates, ConversationStates
from database.db_operations import db_helper
from waypoint import Waypoint

logger = logging.getLogger(__name__)


class Test_Excursion:
    preview_image_src: str = "Excursion1/previewImage.jpg"
    preview_text: str = ("Какой Петербург в ночи? Он сказочный, таинственный и немного романтичный."
                         "Нет ничего от «прежнего», дневного города. "
                         "Именно ночью происходит то самое чудо — развод мостов. "
                         "Каждый, кто приезжает в Петербург, должен увидеть это! "
                         "Но о том, где же в таком огромном городе найти настоящее волшебство белых ночей, "
                         "знают только местные. Мы вам покажем лучшие ночные локации Петербурга. "
                         "Если хочешь перейти к этой экскурсии, введи команду /testexc!")

    description_text = ("Эта экскурсия будет проходить по всему Петерубргу. Бла бла бла. Начала у станции м. Лесная. "
                        "Когда будешь на месте Нажми кнопку \"Начать экскурсию\"")

    description_image_src: str = "Excursion1/descriptionImage.jpg"

    waypoints_array = [
        Waypoint(text="Первый этап экскурсии. Описание",
                 audio_source="Excursion1/T1.m4a"),

        Waypoint(text="Второй этап экскурсии. Описание 2",
                 audio_source="Excursion1/T2.m4a"),

        Waypoint(text="Третий этап экскурсии. Описание 3",
                 audio_source="Excursion1/T3.m4a")
    ]

    PAY_TARIFF: int = 0
    DESCRIPTION: int = 1
    CHECKING_FOR_SUBSCRIPTION: int = 2
    PROCESS_WAYPOINTS: int = 3

    @staticmethod
    async def go_to_test_excursion(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Test_Excursion.description(update, context)
        return ConversationStates.TEST_EXCURSION

    @staticmethod
    async def check_for_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        # TODO: Сделать корректную проверку на подписку. Сейчас стоит заглушка.
        user = db_helper.get_user_by_id(update.effective_user.id)
        excursion_test = db_helper.get_excursion_test_by_id(user_id=user.user_id)
        if excursion_test is None:
            db_helper.add_user_to_excursion_test(user_id=user.user_id, progress=0)
        return True


    @staticmethod
    async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton(strings.CHOOSE_OTHER_EXCURSION_BUTTON_TEXT,
                                     callback_data=MenuButtonStates.CHOOSE_EXCURSION)
            ],
            [
                InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuButtonStates.MAIN_MENU)
            ],
        ]
        await context.bot.send_photo(photo=Test_Excursion.preview_image_src,
                                     chat_id=update.effective_chat.id)
        await context.bot.send_message(text=Test_Excursion.preview_text,
                                       chat_id=update.effective_chat.id,
                                       reply_markup=InlineKeyboardMarkup(keyboard)
                                       )

    @staticmethod
    async def description(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton(strings.BEGIN_BUTTON_TEXT,
                                  callback_data=ExcursionButtonStates.BEGIN_EXCURSION)],
            [InlineKeyboardButton(strings.CHOOSE_OTHER_EXCURSION_BUTTON_TEXT,
                                  callback_data=ExcursionButtonStates.CHOOSE_EXCURSION)],
            [InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT,
                                  callback_data=ExcursionButtonStates.MAIN_MENU)],
        ]
        await context.bot.send_photo(photo=Test_Excursion.description_image_src,
                                     chat_id=update.effective_chat.id)
        await context.bot.send_message(text=Test_Excursion.description_text,
                                       chat_id=update.effective_chat.id,
                                       reply_markup=InlineKeyboardMarkup(keyboard)
                                       )

    @staticmethod
    async def excursion_buttons_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
        """Parses the CallbackQuery"""
        query = update.callback_query
        await query.answer()
        match query.data:
            case ExcursionButtonStates.MAIN_MENU:
                pass
            case ExcursionButtonStates.CHOOSE_EXCURSION:
                pass
            case ExcursionButtonStates.BEGIN_EXCURSION:
                is_allowed_for_excursion = await Test_Excursion.check_for_subscription(update, context)
                if is_allowed_for_excursion:
                    await Test_Excursion.process_waypoints(update, context)
#                    return ConversationStates.
                else:
                    await context.bot.send_message(
                        text="А где деньги? плоти",
                        chat_id=update.effective_chat.id,
                    )

    @staticmethod
    async def process_waypoints(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = db_helper.get_user_by_id(update.effective_user.id)
        await context.bot.send_message(
            text="Поздравляю, ты прошёл процесс проверки на подписку и сейчас находишься в самой экскурсии! УРА!",
            chat_id=update.effective_chat.id,
        )
        return Test_Excursion.PROCESS_WAYPOINTS

    # TODO: Получить прогресс пользователя, отобразить waypoint по этому прогрессу, затем прогресс пользователя++.
