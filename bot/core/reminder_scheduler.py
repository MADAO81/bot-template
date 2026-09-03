"""
Планировщик напоминаний.
Проверяет каждую минуту, не пора ли отправить напоминание.

Автор: MADAO81
Версия: 1.0
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from bot.core.reminder_manager import ReminderManager

logger = logging.getLogger(__name__)

reminder_manager = ReminderManager()
scheduler = AsyncIOScheduler()


async def check_reminders(app):
    try:
        due_reminders = reminder_manager.get_due_reminders()
        if not due_reminders:
            return

        logger.info(f"⏰ Найдено {len(due_reminders)} напоминаний для отправки")

        for reminder in due_reminders:
            try:
                user_id = reminder['user_id']
                chat_id = reminder['chat_id']
                text = reminder['text']
                reminder_id = reminder['id']
                is_private = reminder['is_private']
                is_recurring = reminder['is_recurring']
                recurring_type = reminder.get('recurring_type')

                clean_text = text.replace("@bot_username", "").strip()

                response = (
                    f"📚 *Напоминание!*\n\n"
                    f"⏰ Ты просил(а) напомнить:\n"
                    f"{clean_text}\n\n"
                    f"💪 Не забудь! 🦄"
                )

                if is_private:
                    try:
                        await app.bot.send_message(chat_id=user_id, text=response, parse_mode="Markdown")
                        logger.info(f"✅ Личное напоминание #{reminder_id} отправлено пользователю {user_id}")
                    except Exception as e:
                        logger.warning(f"⚠️ Не удалось отправить в личку #{reminder_id}: {e}")
                        await app.bot.send_message(chat_id=chat_id, text=response, parse_mode="Markdown")
                        logger.info(f"✅ Напоминание #{reminder_id} отправлено в чат {chat_id}")
                else:
                    await app.bot.send_message(chat_id=chat_id, text=response, parse_mode="Markdown")
                    logger.info(f"✅ Групповое напоминание #{reminder_id} отправлено в чат {chat_id}")

                if is_recurring and recurring_type:
                    success = reminder_manager.reschedule_recurring(reminder_id, recurring_type)
                    if success:
                        logger.info(f"🔄 Напоминание #{reminder_id} перенесено ({recurring_type})")
                    else:
                        reminder_manager.mark_sent(reminder_id)
                        logger.warning(f"⚠️ Не удалось перенести #{reminder_id}, деактивируем")
                else:
                    reminder_manager.mark_sent(reminder_id)
                    logger.info(f"🗑️ Напоминание #{reminder_id} деактивировано")

            except Exception as e:
                logger.error(f"❌ Ошибка отправки напоминания #{reminder_id}: {e}")

    except Exception as e:
        logger.error(f"❌ Ошибка при проверке напоминаний: {e}")


def start_reminder_scheduler(app):
    try:
        scheduler.add_job(
            check_reminders,
            IntervalTrigger(minutes=1),
            args=[app],
            id='reminder_check',
            replace_existing=True
        )
        scheduler.start()
        logger.info("✅ Планировщик напоминаний запущен (проверка каждую минуту)")
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске планировщика: {e}")


def stop_reminder_scheduler():
    try:
        scheduler.shutdown()
        logger.info("⏹️ Планировщик напоминаний остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка при остановке планировщика: {e}")
