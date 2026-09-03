"""
Административные команды для бота.

Автор: MADAO81
Версия: 1.0
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.config import Config

logger = logging.getLogger(__name__)
ADMIN_ID = int(Config.ADMIN_ID) if Config.ADMIN_ID else None


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADMIN_ID or update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    await update.message.reply_text("🦄 *Админ-панель*\n\n🚧 В разработке...", parse_mode="Markdown")
