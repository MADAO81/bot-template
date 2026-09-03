"""
Парсер напоминаний.
Извлекает дату, время и текст из сообщений пользователя.

Автор: MADAO81
Версия: 1.0
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple


class ReminderParser:
    @staticmethod
    def parse_reminder(text: str) -> Optional[Tuple[str, datetime, bool, Optional[str], bool]]:
        text_for_search = text.lower().strip()

        if not any(word in text_for_search for word in ["напомни", "напоминание", "напомнить", "запомни"]):
            return None

        for word in ["напомни", "напоминание", "напомнить", "запомни"]:
            if text_for_search.startswith(word):
                text_for_search = text_for_search[len(word):].strip()
                break

        is_private = True
        if "групповое" in text_for_search or "в группу" in text_for_search or "для всех" in text_for_search:
            is_private = False
            text_for_search = text_for_search.replace("групповое", "").replace("в группу", "").replace("для всех", "").strip()
        elif "личное" in text_for_search or "в личку" in text_for_search or "только мне" in text_for_search:
            is_private = True
            text_for_search = text_for_search.replace("личное", "").replace("в личку", "").replace("только мне", "").strip()

        text_for_search = text_for_search.replace("пожалуйста", "").strip()
        text_for_search = text_for_search.replace("плиз", "").strip()
        text_for_search = text_for_search.replace("пж", "").strip()
        text_for_search = re.sub(r'[,，、]', ' ', text_for_search).strip()
        text_for_search = re.sub(r'\s+', ' ', text_for_search).strip()

        is_recurring = False
        recurring_type = None
        recurring_day = None

        if "каждый день" in text_for_search or "ежедневно" in text_for_search:
            is_recurring = True
            recurring_type = "daily"
            text_for_search = text_for_search.replace("каждый день", "").replace("ежедневно", "").strip()
        elif "каждую неделю" in text_for_search or "еженедельно" in text_for_search:
            is_recurring = True
            recurring_type = "weekly"
            text_for_search = text_for_search.replace("каждую неделю", "").replace("еженедельно", "").strip()
        elif "каждый месяц" in text_for_search or "ежемесячно" in text_for_search:
            is_recurring = True
            recurring_type = "monthly"
            text_for_search = text_for_search.replace("каждый месяц", "").replace("ежемесячно", "").strip()

        monthly_match = re.search(r'(\d{1,2})[-]?го?\s+числа\s+каждого\s+месяца', text_for_search)
        if monthly_match:
            recurring_day = int(monthly_match.group(1))
            is_recurring = True
            recurring_type = "monthly"
            text_for_search = text_for_search.replace(monthly_match.group(0), "").strip()

        remind_at = None
        matched_text = ""

        match = re.search(r'сегодня\s+в\s+(\d{1,2})\s*[:.-]\s*(\d{2})', text_for_search)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            now = datetime.now()
            remind_at = datetime(now.year, now.month, now.day, hour, minute, 0, 0)
            matched_text = match.group(0)

        if not remind_at:
            match = re.search(r'завтра\s+в\s+(\d{1,2})\s*[:.-]\s*(\d{2})', text_for_search)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
                now = datetime.now() + timedelta(days=1)
                remind_at = datetime(now.year, now.month, now.day, hour, minute, 0, 0)
                matched_text = match.group(0)

        if not remind_at:
            match = re.search(r'(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+в\s+(\d{1,2})\s*[:.-]\s*(\d{2})', text_for_search)
            if match:
                day = int(match.group(1))
                month = ReminderParser._month_to_number(match.group(2))
                hour = int(match.group(3))
                minute = int(match.group(4))
                year = datetime.now().year
                remind_at = datetime(year, month, day, hour, minute, 0, 0)
                matched_text = match.group(0)

        if not remind_at:
            match = re.search(r'(\d{1,2})[-]?го?\s+числа\s+в\s+(\d{1,2})\s*[:.-]\s*(\d{2})', text_for_search)
            if match:
                day = int(match.group(1))
                hour = int(match.group(2))
                minute = int(match.group(3))
                now = datetime.now()
                if is_recurring and recurring_type == "monthly":
                    month = now.month
                    year = now.year
                else:
                    if day < now.day:
                        if now.month == 12:
                            month = 1
                            year = now.year + 1
                        else:
                            month = now.month + 1
                            year = now.year
                    else:
                        month = now.month
                        year = now.year
                remind_at = datetime(year, month, day, hour, minute, 0, 0)
                matched_text = match.group(0)

        if not remind_at:
            match = re.search(r'(\d{1,2})[-./](\d{1,2})[-./](\d{4})\s+в\s+(\d{1,2})\s*[:.-]\s*(\d{2})', text_for_search)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))
                hour = int(match.group(4))
                minute = int(match.group(5))
                remind_at = datetime(year, month, day, hour, minute, 0, 0)
                matched_text = match.group(0)

        if not remind_at:
            match = re.search(r'(\d{1,2})[-./](\d{1,2})\s+в\s+(\d{1,2})\s*[:.-]\s*(\d{2})', text_for_search)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                hour = int(match.group(3))
                minute = int(match.group(4))
                year = datetime.now().year
                remind_at = datetime(year, month, day, hour, minute, 0, 0)
                matched_text = match.group(0)

        if not remind_at:
            match = re.search(r'в\s+(\d{1,2})\s*[:.-]\s*(\d{2})', text_for_search)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
                now = datetime.now()
                remind_at = datetime(now.year, now.month, now.day, hour, minute, 0, 0)
                matched_text = match.group(0)

        if remind_at is None:
            return None

        if recurring_type == "monthly" and recurring_day:
            remind_at = remind_at.replace(day=recurring_day)

        if matched_text:
            text_for_search = text_for_search.replace(matched_text, "").strip()

        text_for_search = re.sub(r'^[,，、\s]+', '', text_for_search)

        if not text_for_search:
            text_for_search = "Напоминание"

        return text_for_search, remind_at, is_recurring, recurring_type, is_private

    @staticmethod
    def _month_to_number(month_name: str) -> int:
        months = {
            "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
            "мая": 5, "июня": 6, "июля": 7, "августа": 8,
            "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
        }
        return months.get(month_name.lower(), 1)
