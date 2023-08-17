from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from database.db_operations import db_helper
from waypoint import Waypoint


def check_for_subscription() -> bool:
    # TODO: Сделать верификацию подписки
    return True


class Test_Excursion:
    waypoints_array = [
        Waypoint(text="Первый этап экскурсии. Описание",
                 audio_source="Excursion1/T1.m4a"),

        Waypoint(text="Второй этап экскурсии. Описание 2",
                 audio_source="Excursion1/T2.m4a"),

        Waypoint(text="Третий этап экскурсии. Описание 3",
                 audio_source="Excursion1/T3.m4a")
    ]

    DESCRIPTION: int = 0
    BEGIN_EXCURSION: int = 1
    PROCESS_EXCURSION: int = 2

    @staticmethod
    async def description(update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply_keyboard = [["Начать экскурсию"]]
        await context.bot.send_message(text="Описание тестовой экскурсии: В этой экскурсии тебя ждёт не сильно много "
                                            "информации. Вообще ты не должен видеть этот текст, он не для тебя. \n\n"
                                            f"Если хочешь начать экскурсию, нажми кнопку \"{reply_keyboard[0][0]}\"",
                                       chat_id=update.effective_chat.id,
                                       reply_markup=ReplyKeyboardMarkup(
                                           reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
                                       )
        return Test_Excursion.BEGIN_EXCURSION

    @staticmethod
    async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = db_helper.get_user_by_id(update.effective_user.id)
        is_allowed_for_excursion = check_for_subscription()
        if is_allowed_for_excursion:
            # TODO: Сделать начало экскурсии
            pass
        return Test_Excursion.PROCESS_EXCURSION
