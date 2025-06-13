import os
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # например: https://your-service.onrender.com
ADMIN_CHAT_ID = 446370284

services = [
    {"id": "s1", "name": "120 минут"},
    {"id": "s2", "name": "180 минут"},
    {"id": "s3", "name": "90 минут"},
    {"id": "s4", "name": "240 минут"},
    {"id": "s5", "name": "Эромассаж в 4 руки"},
    {"id": "s6", "name": "Массаж для жены в присутствии мужа"},
]

masters = [
    {"id": "m1", "name": "Эдуард Бондаренко"},
    {"id": "m2", "name": "Сергей Богданов"},
    {"id": "m3", "name": "Илья Соболев"},
    {"id": "m4", "name": "Глеб Коуэн"},
    {"id": "m5", "name": "Майкл Брандт"},
    {"id": "m6", "name": "Андрей Подольский"},
]

user_data = {}

# Создаем FastAPI-приложение
fastapi_app = FastAPI()

# Создаем Telegram Application (бота)
telegram_app = Application.builder().token(BOT_TOKEN).build()


# === Telegram Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(s["name"], callback_data=f"service:{s['id']}")]
        for s in services
    ]
    await update.message.reply_text(
        "👋 Добро пожаловать в салон Pro Orgazm!\n\nВыберите продолжительность массажа:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("service:"):
        service_id = data.split(":")[1]
        service = next((s["name"] for s in services if s["id"] == service_id), "Неизвестно")
        user_data[user_id] = {"service": service}
        keyboard = [
            [InlineKeyboardButton(m["name"], callback_data=f"master:{m['id']}")]
            for m in masters
        ]
        await query.edit_message_text(
            f"Вы выбрали: {service}\nВыберите мастера:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data.startswith("master:"):
        master_id = data.split(":")[1]
        master = next((m["name"] for m in masters if m["id"] == master_id), "Неизвестно")
        user_data[user_id]["master"] = master
        await query.edit_message_text(
            f"Отлично! Мастер: {master}.\n\n📞 Пожалуйста, отправьте свой номер телефона:"
        )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_data:
        phone = update.message.text
        info = user_data[user_id]
        name = update.message.from_user.full_name
        text = (
            f"📩 Новый лид от {name}:\n\n"
            f"🕒 Услуга: {info['service']}\n"
            f"💆 Мастер: {info['master']}\n"
            f"📱 Телефон: {phone}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)

        await update.message.reply_text("✅ Спасибо! Мы скоро свяжемся с вами. Также можете написать нам в мессенджер:")
        keyboard = [
            [InlineKeyboardButton("💬 WhatsApp", url="https://wa.me/79999999999")],
            [InlineKeyboardButton("📲 Telegram", url="https://t.me/YOUR_SUPPORT_USERNAME")]
        ]
        await update.message.reply_text("Или нажмите на кнопку ниже:", reply_markup=InlineKeyboardMarkup(keyboard))
        del user_data[user_id]
    else:
        await update.message.reply_text("Пожалуйста, начните с /start")


# === Добавление хендлеров ===
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))


# === Webhook эндпоинт ===
@fastapi_app.on_event("startup")
async def on_startup():
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")


@fastapi_app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


# === Запуск через uvicorn (Render делает это автоматически) ===
# uvicorn bot:fastapi_app --host 0.0.0.0 --port $PORT
