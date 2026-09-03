"""
Дополнительные команды для бота.
Команды: /advice, /recipe

Автор: MADAO81
Версия: 1.0
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.services.ai_service import get_bot_response
from bot.utils.time_utils import is_working_hours, get_working_status_message

logger = logging.getLogger(__name__)


async def advice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    args = context.args
    query = " ".join(args) if args else "жизненную ситуацию"

    status_message = await update.message.reply_text("💭 Дай-ка подумать...")

    try:
        response = await get_bot_response(
            user_message=f"Пользователь просит совет: {query}. Дай добрый и практичный совет.",
            mood_description="happy"
        )

        await status_message.delete()
        if response:
            await update.message.reply_text(f"💡 *Совет:*\n\n{response}", parse_mode="Markdown")
        else:
            await update.message.reply_text("😅 Не смогла придумать совет... Попробуй ещё раз! 🦄")
    except Exception as e:
        logger.error(f"❌ Advice error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")


async def recipe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    args = context.args
    query = " ".join(args) if args else "простой рецепт"

    status_message = await update.message.reply_text("🍳 Сейчас поищу рецепт...")

    try:
        response = await get_bot_response(
            user_message=f"Пользователь просит рецепт: {query}. Дай простой и вкусный рецепт.",
            mood_description="happy"
        )

        await status_message.delete()
        if response:
            await update.message.reply_text(f"🍳 *Рецепт:*\n\n{response}", parse_mode="Markdown")
        else:
            await update.message.reply_text("😅 Не нашла рецепт... Попробуй ещё раз! 🦄")
    except Exception as e:
        logger.error(f"❌ Recipe error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")
