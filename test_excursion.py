from telegram import Update
from telegram.ext import ContextTypes


async def test_excursion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Test ecxursion started")
