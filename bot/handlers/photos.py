"""
Обработчик фото для бота.

Автор: MADAO81
Версия: 1.0
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.services.ai_service import analyze_image
from bot.utils.time_utils import is_working_hours
from bot.core.context_manager import ContextManager

logger = logging.getLogger(__name__)

context_manager = ContextManager()


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("📸 handle_photo ВЫЗВАНА!")

    if not is_working_hours():
        logger.info("⏰ Не рабочее время, фото игнорируется")
        return

    if update.message.chat.type != "private":
        bot_username = context.bot.username
        caption = update.message.caption or ""
        if f"@{bot_username}" not in caption:
            logger.info("📸 Нет упоминания бота, пропускаем")
            return

    status_message = await update.message.reply_text("🖼️ Смотрю на картинку...")

    try:
        user_id = update.effective_user.id
        user_message = update.message.caption or "Без подписи"

        photo_file = await update.message.photo[-1].get_file()
        image_data = await photo_file.download_as_bytearray()

        logger.info(f"📸 Фото получено, размер: {len(image_data)} байт")

        response = await analyze_image(
            image_data=bytes(image_data),
            user_message=user_message,
            mood_description="happy"
        )

        if not response:
            response = "🖼️ Красивая картинка! 📚"

        await status_message.delete()
        await update.message.reply_text(f"🖼️ {response}")

        context_manager.save_context(user_id, f"[Фото] {user_message}", response)
        logger.info("✅ Фото обработано")

    except Exception as e:
        logger.error(f"❌ Ошибка обработки фото: {e}")
        await status_message.edit_text("🖼️ Ой! Что-то пошло не так! 📚")
