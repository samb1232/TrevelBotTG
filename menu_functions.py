import datetime
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

import strings
from enumerations import MenuCallbackButtons, ConversationStates
from database.db_operations import db_helper

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if db_helper.get_user_by_id(update.effective_user.id) is None:
        logger.info(f"Добавление нового пользователя {update.effective_user.name} в базу данных")

        db_helper.add_new_user(
            user_id=update.effective_user.id,
            subscription_type=-1,
            subscription_end_date=datetime.date.min,
            excursions_left=0
        )

        keyboard = [
            [
                InlineKeyboardButton(strings.START_ADVENTURE_BUTTON_TEXT, callback_data=MenuCallbackButtons.MAIN_MENU)
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(strings.GREETING_TEXT, reply_markup=reply_markup)
        return ConversationStates.MAIN_MENU
    else:
        logger.debug("Пользователь обнаружен в базе данных")
        return await main_menu(update, context)


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [
            InlineKeyboardButton(strings.CHOOSE_EXCURSION_BUTTON_TEXT,
                                 callback_data=MenuCallbackButtons.CHOOSE_EXCURSION)
        ],
        [
            InlineKeyboardButton(strings.TARIFFS_BUTTON_TEXT, callback_data=MenuCallbackButtons.TARIFFS),
            InlineKeyboardButton(strings.MY_STATUS_BUTTON_TEXT, callback_data=MenuCallbackButtons.GET_STATUS)
        ],
        [
            InlineKeyboardButton(strings.ADDITIONAL_BUTTON_TEXT,
                                 callback_data=MenuCallbackButtons.ADDITIONAL_INFORMATION)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(text=strings.MAIN_MENU_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)
    return ConversationStates.MAIN_MENU


async def callback_buttons_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery"""
    query = update.callback_query
    await query.answer()
    await query.message.edit_reply_markup(None)
    match query.data:
        case MenuCallbackButtons.MAIN_MENU:
            await main_menu(update, context)
        case MenuCallbackButtons.CHOOSE_EXCURSION:
            await choose_excursion(update, context)
        case MenuCallbackButtons.ADDITIONAL_INFORMATION:
            await additional_information(update, context)
        case MenuCallbackButtons.GET_STATUS:
            await get_tariff_status(update, context)
        case MenuCallbackButtons.TARIFFS:
            await tariffs(update, context)
        case MenuCallbackButtons.TARIFF_LOW:
            await tariff_low(update, context)
        case MenuCallbackButtons.TARIFF_MID:
            await tariff_mid(update, context)
        case MenuCallbackButtons.TARIFF_HIGH:
            await tariff_high(update, context)
        case MenuCallbackButtons.NOT_IMPLEMENTED:
            await context.bot.send_message(text="Данная функция находится в разработке...",
                                           chat_id=update.effective_chat.id)


async def choose_excursion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Сделать выпадающий список экскурсий.
    keyboard = [
        [
            InlineKeyboardButton(strings.CHOOSE_OTHER_EXCURSION_BUTTON_TEXT,
                                 callback_data=MenuCallbackButtons.CHOOSE_EXCURSION)
        ],
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuCallbackButtons.MAIN_MENU)
        ],
    ]
    await context.bot.send_message(text=("Пока что есть две экскурсии. \n"
                                         "Если хочешь перейти к первой экскурсии, введи команду /testexc1!\n"
                                         "Если хочешь перейти ко второй экскурсии, введи команду /testexc2!\n"),
                                   chat_id=update.effective_chat.id,
                                   reply_markup=InlineKeyboardMarkup(keyboard)
                                   )


async def get_tariff_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuCallbackButtons.MAIN_MENU)
        ],
    ])
    user = db_helper.get_user_by_id(update.effective_user.id)
    if user.subscription_type == -1:
        text = strings.NO_TARIFF_TEXT
    elif user.subscription_end_date < datetime.date.today():
        text = strings.TARIFF_EXPIRES_TEXT
    else:
        user_allowed_excursions = db_helper.get_user_allowed_excursions(update.effective_user.id)

        if len(user_allowed_excursions) == 0:
            allowed_excursions = ""
        else:
            allowed_excursions = strings.ALLOWED_EXCURSIONS_TEXT
            for exc_name in user_allowed_excursions:
                allowed_excursions += "  👉 " + exc_name + "\n"
        text = (strings.TARIFF_INFO_TEXT_ARR[0] + strings.TARIFFS_ARR[user.subscription_type] +
                strings.TARIFF_INFO_TEXT_ARR[1] + user.subscription_end_date.strftime('%Y-%m-%d') +
                strings.TARIFF_INFO_TEXT_ARR[2] + str(user.excursions_left) + "\n" + allowed_excursions)

    await context.bot.send_message(text=text,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)


async def tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(strings.TARIFF_LOW_TEXT, callback_data=MenuCallbackButtons.TARIFF_LOW),
            InlineKeyboardButton(strings.TARIFF_MID_TEXT, callback_data=MenuCallbackButtons.TARIFF_MID),
            InlineKeyboardButton(strings.TARIFF_HIGH_TEXT, callback_data=MenuCallbackButtons.TARIFF_HIGH)
        ],
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuCallbackButtons.MAIN_MENU)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo="src/tariffs.png")
    await context.bot.send_message(text=strings.TARIFFS_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)


async def tariff_low(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuCallbackButtons.MAIN_MENU)
        ],
    ])
    db_helper.set_subscription_to_user(user_id=update.effective_user.id,
                                       subscription_type=0,
                                       subscription_end_date=datetime.date.today() + datetime.timedelta(days=30),
                                       excursions_left=1)
    await context.bot.send_message(text=strings.TARIFF_LOW_SUCCESS_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)
    await set_reminder(chat_id=update.effective_chat.id,
                       time_in_days=30,
                       context=context)


async def tariff_mid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuCallbackButtons.MAIN_MENU)
        ],
    ])
    db_helper.set_subscription_to_user(user_id=update.effective_user.id,
                                       subscription_type=1,
                                       subscription_end_date=datetime.date.today() + datetime.timedelta(days=30),
                                       excursions_left=3)

    await context.bot.send_message(text=strings.TARIFF_MID_SUCCESS_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)
    await set_reminder(chat_id=update.effective_chat.id,
                       time_in_days=30,
                       context=context)


async def tariff_high(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuCallbackButtons.MAIN_MENU)
        ],
    ])
    db_helper.set_subscription_to_user(user_id=update.effective_user.id,
                                       subscription_type=2,
                                       subscription_end_date=datetime.date.today() + datetime.timedelta(days=90),
                                       excursions_left=5)
    await context.bot.send_message(text=strings.TARIFF_HIGH_SUCCESS_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)
    await set_reminder(chat_id=update.effective_chat.id,
                       time_in_days=90,
                       context=context)


async def additional_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuCallbackButtons.MAIN_MENU)
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(text=strings.ADDITIONAL_INFO_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)


async def stop_excursion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await main_menu(update, context)
    return ConversationHandler.END


async def unknown_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    return await start(update, context)


async def send_excursion_expired_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=strings.TARIFF_EXPIRED_TEXT)


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return
    for job in current_jobs:
        job.schedule_removal()


async def set_reminder(chat_id: int, time_in_days: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""

    remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(callback=send_excursion_expired_reminder,
                               when=datetime.timedelta(days=time_in_days),
                               chat_id=chat_id, name=str(chat_id))
