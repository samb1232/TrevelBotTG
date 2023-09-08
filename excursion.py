import datetime
import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes

import menu_functions
import strings
from database.db_operations import db_helper
from enumerations import ExcursionCallbackButtons, ConversationStates

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Excursion:

    def __init__(self, description_text: str, finale_message_text: str, description_image_src: str,
                 waypoints_array: list, excursion_name: str, entry_point: int):
        self.description_text = description_text
        self.finale_message_text = finale_message_text
        self.description_image_src = description_image_src
        self.waypoints_array = waypoints_array
        self.excursion_name = excursion_name
        self.entry_point = entry_point  # Это значение из ConversationStates

    async def check_for_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        user = db_helper.get_user_by_id(update.effective_user.id)
        logger.debug(f"Проверка на валидность подписки у пользователя с id = {user.user_id}")
        user_progress = db_helper.get_user_progress_on_excursion_by_id(user_id=user.user_id,
                                                                       excursion_name=self.excursion_name)
        if user_progress is None:
            if (user.subscription_type != -1
                    and user.excursions_left > 0
                    and user.subscription_end_date > datetime.date.today()):
                db_helper.add_user_to_excursion(user_id=user.user_id, excursion_name=self.excursion_name)
                return True
            else:
                return False
        elif user.subscription_end_date > datetime.date.today():
            return True
        else:
            return False

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
        return self.entry_point

    async def excursion_callback_buttons_manager(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Parses the CallbackQuery"""
        query = update.callback_query
        await query.answer()
        match query.data:
            case ExcursionCallbackButtons.MAIN_MENU:
                await query.message.edit_reply_markup(None)
                await menu_functions.main_menu(update, context)
            case ExcursionCallbackButtons.CHOOSE_EXCURSION:
                await menu_functions.choose_excursion(update, context)
                return ConversationStates.MAIN_MENU
            case ExcursionCallbackButtons.BEGIN_EXCURSION:
                is_allowed_for_excursion = await self.check_for_subscription(update, context)
                if is_allowed_for_excursion:
                    await self.process_waypoints(update, context)
                else:
                    await context.bot.send_message(
                        text=strings.NOT_ALLOWED_FOR_EXCURSION_TEXT,
                        chat_id=update.effective_chat.id,
                    )
                    await menu_functions.main_menu(update, context)
                    return ConversationStates.MAIN_MENU

    async def process_waypoints(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.debug(f"Обработка процесса проведения экскурсии {self.excursion_name}")
        user_progress = db_helper.get_user_progress_on_excursion_by_id(user_id=update.effective_user.id,
                                                                       excursion_name=self.excursion_name)

        # Fix for potential negative progress number
        if user_progress.progress < 0:
            user_progress.progress = 0
            db_helper.reset_user_progress_for_excursion(user_id=update.effective_user.id,
                                                        excursion_name=self.excursion_name)

        if user_progress.progress >= len(self.waypoints_array):
            await context.bot.send_message(
                text=self.finale_message_text,
                chat_id=update.effective_chat.id,
                reply_markup=ReplyKeyboardRemove()
            )
            db_helper.reset_user_progress_for_excursion(user_id=update.effective_user.id,
                                                        excursion_name=self.excursion_name)
            await menu_functions.main_menu(update, context)
            return ConversationStates.MAIN_MENU

        if user_progress.progress != 0:
            prev_waypoint = self.waypoints_array[user_progress.progress - 1]
            if prev_waypoint.quiz_answer is not None:
                if update.message is None:
                    db_helper.decrease_progress_excursion(user_id=update.effective_user.id,
                                                          excursion_name=self.excursion_name)
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

        button_names = self.waypoints_array[user_progress.progress].buttons_names

        for component in self.waypoints_array[user_progress.progress].components:
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
                                              excursion_name=self.excursion_name)

    async def stop_excursion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_progress = db_helper.get_user_progress_on_excursion_by_id(user_id=update.effective_user.id,
                                                                       excursion_name=self.excursion_name)
        if user_progress is not None and user_progress.progress > 0:
            db_helper.decrease_progress_excursion(user_id=update.effective_user.id,
                                                  excursion_name=self.excursion_name)
        await context.bot.send_message(text=strings.STOP_EXCURSION_TEXT,
                                       chat_id=update.effective_chat.id,
                                       reply_markup=ReplyKeyboardRemove())
        await menu_functions.main_menu(update, context)
        return ConversationStates.MAIN_MENU
