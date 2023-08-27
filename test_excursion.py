import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes

import strings
from button_states import MenuButtonStates, ExcursionButtonStates, ConversationStates
from database.db_operations import db_helper
from waypoint import Waypoint, Text, Audio, Picture

logger = logging.getLogger(__name__)


class Test_Excursion:
    preview_image_src: str = "Excursion1/previewImage.jpg"
    preview_text: str = ("Кто и зачем прорыл подземные ходы под Летним садом, "
                         "какой смысл хотел заложить Петр I в строительство сада, как проходили смотры невест, "
                         "первые признаки феминизма и почему никто не ехал в Петербург? \n"
                         "Ответы на все эти вопросы можно найти прогуливаясь по самой известной зеленой зоне города, "
                         "если знать где и что искать. Сегодня предлагаем раскрыть тайны этого места.\n"
                         "Если хочешь перейти к этой экскурсии, введи команду /testexc!")

    description_text = ("Кто и зачем прорыл подземные ходы под Летним садом? "
                        "Сегодня предлагаем раскрыть тайны этого места.")

    finale_message_text = "Благодарю за это удивительное приключение! Экскурсия окончена. Ещё увидимся!"

    description_image_src: str = "Excursion1/map.jpg"

    waypoints_array = [
        Waypoint(components=[
            Text("Первый этап экскурсии. Описание"),
            Picture("Excursion1/point1.png"),
            Audio("Excursion1/T1.m4a")
        ],
            buttons_names=["Дальше"]
        ),
        Waypoint([
            Text("Второй этап экскурсии. Описание 2"),
            Audio("Excursion1/T2.m4a")
        ],
            buttons_names=["Дальше"]
        ),
        Waypoint(components=[
            Text("Третий этап экскурсии. Описание 3"),
            Audio("Excursion1/T3.m4a")
        ],
            buttons_names=["Поехали!"]
        ),

        Waypoint(components=[
            Text("Приехали")
        ],
            buttons_names=["Спасибо за экскурсию!"]
        )]

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
    async def excursion_buttons_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                else:
                    # TODO: Доработать функцию оплаты
                    await context.bot.send_message(
                        text="А где деньги? плоти",
                        chat_id=update.effective_chat.id,
                    )

    @staticmethod
    async def process_waypoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
        excursion_test = db_helper.get_excursion_test_by_id(update.effective_user.id)

        if excursion_test.progress >= len(Test_Excursion.waypoints_array):
            await context.bot.send_message(
                text=Test_Excursion.finale_message_text,
                chat_id=update.effective_chat.id,
                reply_markup=ReplyKeyboardRemove()
            )
            db_helper.reset_progress_excursion_test(update.effective_user.id)
            await Test_Excursion.main_menu(update, context)
            return ConversationStates.MAIN_MENU

        if excursion_test.progress != 0:
            prev_button_names = Test_Excursion.waypoints_array[excursion_test.progress - 1].buttons_names
            is_input_incorrect = True
            for button_name in prev_button_names:
                if update.message is None or update.message.text == button_name:
                    is_input_incorrect = False
                    break
            if is_input_incorrect:
                return

        button_names = Test_Excursion.waypoints_array[excursion_test.progress].buttons_names

        for component in Test_Excursion.waypoints_array[excursion_test.progress].components:
            match component.__name__:
                case "TEXT":
                    await context.bot.send_message(
                        text=component.text,
                        chat_id=update.effective_chat.id,
                        reply_markup=ReplyKeyboardMarkup([button_names])
                    )
                case "PICTURE":
                    await context.bot.send_photo(
                        photo=component.picture_source,
                        chat_id=update.effective_chat.id,
                        reply_markup=ReplyKeyboardMarkup([button_names])
                    )
                case "AUDIO":
                    await context.bot.send_audio(
                        audio=component.audio_source,
                        chat_id=update.effective_chat.id,
                        reply_markup=ReplyKeyboardMarkup([button_names])
                    )
        db_helper.increase_progress_excursion_test(user_id=update.effective_user.id)

    @staticmethod
    async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # TODO: повторяющаяся функция из метода main. Нужно от неё избавиться
        keyboard = [
            [
                InlineKeyboardButton(strings.CHOOSE_EXCURSION_BUTTON_TEXT,
                                     callback_data=MenuButtonStates.CHOOSE_EXCURSION)
            ],
            [
                InlineKeyboardButton(strings.TARIFFS_BUTTON_TEXT, callback_data=MenuButtonStates.TARIFFS),
                InlineKeyboardButton(strings.MY_STATUS_BUTTON_TEXT, callback_data=MenuButtonStates.GET_STATUS)
            ],
            [
                InlineKeyboardButton(strings.ADDITIONAL_BUTTON_TEXT,
                                     callback_data=MenuButtonStates.ADDITIONAL_INFORMATION)
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(text=strings.MAIN_MENU_TEXT,
                                       chat_id=update.effective_chat.id,
                                       reply_markup=reply_markup)
        return ConversationStates.MAIN_MENU

# TODO: Сделать механику продолжения и приостановки экскурсии
# TODO: Сделать механику квиза
