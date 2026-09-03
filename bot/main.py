"""
Главный модуль бота.
Инициализация, настройка и запуск бота.

Автор: MADAO81
Версия: 1.0
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.config import Config
from bot.handlers.commands import start, help_command, weather_command
from bot.handlers.extra import advice_command, recipe_command
from bot.handlers.messages import handle_message
from bot.handlers.photos import handle_photo
from bot.handlers.voice import handle_voice
from bot.handlers.admin import admin_panel
from bot.core.scheduler import start_scheduler, subscribe_command, unsubscribe_command
from bot.core.reminder_scheduler import start_reminder_scheduler
from bot.core.constants import VERSION

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if Config.DEBUG_MODE:
    logging.getLogger().setLevel(logging.DEBUG)
    logger.info("🐛 DEBUG_MODE включён")

def main():
    logger.info(f"🦄 Запуск бота (v{VERSION})...")
    logger.info(f"👤 Автор: MADAO81")

    if not Config.TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_TOKEN не найден в .env файле!")
        return

    if not Config.PROXY_API_KEY:
        logger.error("❌ PROXY_API_KEY не найден в .env файле!")
        return

    app = Application.builder().token(Config.TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("weather", weather_command))

    app.add_handler(CommandHandler("advice", advice_command))
    app.add_handler(CommandHandler("recipe", recipe_command))

    app.add_handler(CommandHandler("admin", admin_panel))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.AUDIO, handle_voice))

    start_scheduler(app)
    start_reminder_scheduler(app)

    logger.info("✅ Бот успешно запущен и готов к работе!")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
