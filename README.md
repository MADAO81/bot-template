# 🦄 Pony Bot Template

> Универсальный шаблон для создания Telegram-ботов по образу пони из My Little Pony.

## 📖 О проекте

Этот шаблон содержит всё необходимое для быстрого запуска нового бота:
- ✅ Готовая структура проекта
- ✅ Единый стандарт рассылок (`send_long_message`)
- ✅ Поддержка DeepSeek (через ProxyAPI)
- ✅ Поддержка напоминаний
- ✅ Автозапуск через systemd
- ✅ Сторожевой таймер (watchdog)

## 🚀 Быстрый старт

### 1. Клонируйте шаблон

```bash
git clone https://github.com/MADAO81/bot-template.git
cd bot-template
```

### 2. Создайте виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте `.env`

Скопируйте `.env.example` в `.env` и заполните:

```env
TELEGRAM_TOKEN=ваш_токен
PROXY_API_KEY=ваш_ключ
DEEPSEEK_MODEL=deepseek/deepseek-v4-flash
```

### 5. Запустите бота

```bash
python run.py
```

## 📁 Структура

- `bot/core/` — ядро (константы, контекст, напоминания, планировщик)
- `bot/handlers/` — обработчики команд
- `bot/services/` — AI, погода, рецепты
- `bot/utils/` — утилиты
- `data/` — базы данных
- `logs/` — логи

## 📄 Лицензия

MIT
