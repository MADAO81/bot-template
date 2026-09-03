"""
Планировщик для бота.
Отправка утренней и вечерней рассылок.

Автор: MADAO81
Версия: 3.0 — универсальная разбивка длинных сообщений
"""

import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bot.config import Config
from bot.services.ai_service import get_morning_message, get_evening_message

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
DB_PATH = Config.DATA_DIR / "subscriptions.db"


def _get_connection():
    return sqlite3.connect(DB_PATH)


def _init_db():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            chat_id INTEGER PRIMARY KEY,
            subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_chat(chat_id: int):
    _init_db()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO subscriptions (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    conn.close()
    logger.info(f"📋 Чат {chat_id} добавлен для рассылки")


def remove_chat(chat_id: int):
    _init_db()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subscriptions WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()
    logger.info(f"📋 Чат {chat_id} удалён из рассылки")


def get_active_chats():
    _init_db()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM subscriptions")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    add_chat(chat_id)
    await update.message.reply_text(
        "📬 *Ты подписался на ежедневные рассылки!*\n\n"
        "✅ Чтобы отписаться, напиши /unsubscribe",
        parse_mode="Markdown"
    )


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    remove_chat(chat_id)
    await update.message.reply_text(
        "😢 *Ты отписался от рассылок!*\n\n"
        "Если захочешь вернуться — напиши /subscribe",
        parse_mode="Markdown"
    )


async def send_long_message(bot, chat_id: int, text: str, parse_mode: str = "Markdown"):
    """Отправляет длинное сообщение, разбивая на части."""
    if not text:
        return

    if len(text) < 4000:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
        return

    parts = []
    current_part = ""
    for paragraph in text.split('\n'):
        if len(current_part) + len(paragraph) + 1 < 4000:
            current_part += paragraph + '\n'
        else:
            if current_part:
                parts.append(current_part.strip())
            current_part = paragraph + '\n'
    if current_part:
        parts.append(current_part.strip())

    if len(parts) == 1 and len(parts[0]) > 4000:
        words = parts[0].split()
        parts = []
        current_part = ""
        for word in words:
            if len(current_part) + len(word) + 1 < 4000:
                current_part += word + ' '
            else:
                parts.append(current_part.strip())
                current_part = word + ' '
        if current_part:
            parts.append(current_part.strip())

    for i, part in enumerate(parts):
        if i == 0:
            await bot.send_message(chat_id=chat_id, text=part, parse_mode=parse_mode)
        else:
            await bot.send_message(chat_id=chat_id, text=f"*Продолжение:*\n{part}", parse_mode="Markdown")


async def send_morning(app):
    active_chats = get_active_chats()
    if not active_chats:
        logger.info("📭 Нет активных чатов для утренней рассылки")
        return

    logger.info(f"🌅 Отправка утренней рассылки в {len(active_chats)} чатов...")

    message = await get_morning_message()
    if not message:
        message = "🌅 *Доброе утро!* Хорошего дня! 🦄"

    for chat_id in active_chats:
        try:
            await send_long_message(app.bot, chat_id, message, parse_mode="Markdown")
            logger.info(f"✅ Утренняя рассылка отправлена в чат {chat_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в чат {chat_id}: {e}")
            if "bot was blocked" in str(e) or "chat not found" in str(e):
                remove_chat(chat_id)


async def send_evening(app):
    active_chats = get_active_chats()
    if not active_chats:
        logger.info("📭 Нет активных чатов для вечерней рассылки")
        return

    logger.info(f"🌙 Отправка вечерней рассылки в {len(active_chats)} чатов...")

    message = await get_evening_message()
    if not message:
        message = "🌙 *Спокойной ночи!* Пусть тебе приснятся хорошие сны! 🦄"

    for chat_id in active_chats:
        try:
            await send_long_message(app.bot, chat_id, message, parse_mode="Markdown")
            logger.info(f"✅ Вечерняя рассылка отправлена в чат {chat_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в чат {chat_id}: {e}")
            if "bot was blocked" in str(e) or "chat not found" in str(e):
                remove_chat(chat_id)


def start_scheduler(app):
    try:
        _init_db()

        default_chats = getattr(Config, 'DEFAULT_CHATS', "")
        if default_chats:
            for chat_id in default_chats.split(","):
                try:
                    chat_id = int(chat_id.strip())
                    add_chat(chat_id)
                    logger.info(f"✅ Автоматически добавлен чат: {chat_id}")
                except Exception as e:
                    logger.error(f"❌ Ошибка добавления чата {chat_id}: {e}")

        # ===== НАСТРОЙ ВРЕМЯ ПОД СВОЕГО ПЕРСОНАЖА =====
        scheduler.add_job(
            send_morning,
            CronTrigger(hour=9, minute=0),
            args=[app],
            id='morning',
            replace_existing=True
        )

        scheduler.add_job(
            send_evening,
            CronTrigger(hour=21, minute=0),
            args=[app],
            id='evening',
            replace_existing=True
        )

        scheduler.start()
        logger.info(f"✅ Планировщик запущен. Утро в 9:00, вечер в 21:00")

    except Exception as e:
        logger.error(f"❌ Ошибка при запуске планировщика: {e}")


def stop_scheduler():
    try:
        scheduler.shutdown()
        logger.info("⏹️ Планировщик остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка при остановке планировщика: {e}")
