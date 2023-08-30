import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes

import menu_functions
import strings
from database.db_operations import db_helper
from enumerations import ExcursionCallbackButtons, ConversationStates

logger = logging.getLogger(__name__)


class Excursion:

    def __init__(self, description_text: str, finale_message_text: str, description_image_src: str,
                 waypoints_array: list, excursion_db_class):
        self.description_text = description_text
        self.finale_message_text = finale_message_text
        self.description_image_src = description_image_src
        self.waypoints_array = waypoints_array
        self.excursion_db_class = excursion_db_class

    async def check_for_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        # TODO: Сделать корректную проверку на подписку. Сейчас стоит заглушка.
        user = db_helper.get_user_by_id(update.effective_user.id)
        excursion_test = db_helper.get_excursion_info_by_id(user_id=user.user_id,
                                                            excursion_class=self.excursion_db_class)
        if excursion_test is None:
            db_helper.add_user_to_excursion(user_id=user.user_id, excursion_class=self.excursion_db_class)
        return True

    async def description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton(strings.BEGIN_BUTTON_TEXT,
                                  callback_data=ExcursionCallbackButtons.BEGIN_EXCURSION)],
            [InlineKeyboardButton(strings.CHOOSE_OTHER_EXCURSION_BUTTON_TEXT,
                                  callback_data=ExcursionCallbackButtons.CHOOSE_EXCURSION)],
            [InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT,
                                  callback_data=ExcursionCallbackButtons.MAIN_MENU)],
        ]
        await context.bot.send_photo(photo=self.description_image_src,
                                     chat_id=update.effective_chat.id)
        await context.bot.send_message(text=self.description_text,
                                       chat_id=update.effective_chat.id,
                                       reply_markup=InlineKeyboardMarkup(keyboard)
                                       )
        return ConversationStates.TEST_EXCURSION

    async def excursion_buttons_manager(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Parses the CallbackQuery"""
        query = update.callback_query
        await query.answer()
        match query.data:
            case ExcursionCallbackButtons.MAIN_MENU:
                await query.message.edit_reply_markup(None)
                await menu_functions.main_menu(update, context)
            case ExcursionCallbackButtons.CHOOSE_EXCURSION:
                await context.bot.send_message(
                    text="Других экскурсий пока что нет",
                    chat_id=update.effective_chat.id,
                )
            case ExcursionCallbackButtons.BEGIN_EXCURSION:
                is_allowed_for_excursion = await self.check_for_subscription(update, context)
                if is_allowed_for_excursion:
                    await self.process_waypoints(update, context)
                else:
                    # TODO: Доработать функцию оплаты
                    await context.bot.send_message(
                        text="А где деньги? плоти",
                        chat_id=update.effective_chat.id,
                    )

    async def process_waypoints(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        excursion_test = db_helper.get_excursion_info_by_id(user_id=update.effective_user.id,
                                                            excursion_class=self.excursion_db_class)

        # Fix for potential negative progress number
        if excursion_test.progress < 0:
            excursion_test.progress = 0
            db_helper.reset_progress_excursion(user_id=update.effective_user.id,
                                               excursion_class=self.excursion_db_class)

        if excursion_test.progress >= len(self.waypoints_array):
            await context.bot.send_message(
                text=self.finale_message_text,
                chat_id=update.effective_chat.id,
                reply_markup=ReplyKeyboardRemove()
            )
            db_helper.reset_progress_excursion(user_id=update.effective_user.id,
                                               excursion_class=self.excursion_db_class)
            await menu_functions.main_menu(update, context)
            return ConversationStates.MAIN_MENU

        if excursion_test.progress != 0:
            prev_waypoint = self.waypoints_array[excursion_test.progress - 1]
            if prev_waypoint.quiz_answer is not None:
                if update.message is None:
                    db_helper.decrease_progress_excursion(user_id=update.effective_user.id,
                                                          excursion_class=self.excursion_db_class)
                    return await self.process_waypoints(update, context)  # Restart function
                if update.message.text != prev_waypoint.quiz_answer:
                    await context.bot.send_message(
                        text=strings.WRONG_QUIZ_ANSWER_TEXT,
                        chat_id=update.effective_chat.id,
                        reply_markup=ReplyKeyboardMarkup([prev_waypoint.buttons_names])
                    )
                    return
                else:
                    await context.bot.send_message(
                        text=strings.RIGHT_QUIZ_ANSWER_TEXT,
                        chat_id=update.effective_chat.id,
                        reply_markup=ReplyKeyboardRemove()
                    )
            else:
                is_input_incorrect = True
                for button_name in prev_waypoint.buttons_names:
                    if update.message is None or update.message.text == button_name:
                        is_input_incorrect = False
                        break
                if is_input_incorrect:
                    return

        button_names = self.waypoints_array[excursion_test.progress].buttons_names

        for component in self.waypoints_array[excursion_test.progress].components:
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
        db_helper.increase_progress_excursion(user_id=update.effective_user.id,
                                              excursion_class=self.excursion_db_class)

    async def stop_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        test_excursion = db_helper.get_excursion_info_by_id(user_id=update.effective_user.id,
                                                            excursion_class=self.excursion_db_class)
        if test_excursion is not None and test_excursion.progress > 0:
            db_helper.decrease_progress_excursion(user_id=update.effective_user.id,
                                                  excursion_class=self.excursion_db_class)
        await context.bot.send_message(text=strings.STOP_EXCURSION_TEXT,
                                       chat_id=update.effective_chat.id)
        await menu_functions.main_menu(update, context)
        return ConversationStates.MAIN_MENU
