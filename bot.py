from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# === НАСТРОЙКИ ===
BOT_TOKEN = '7985540950:AAGs_x79yOybKywqCOfi0Rs4ZjdQukML4NU'
ADMIN_CHAT_ID = 446370284  # например: 123456789

# === ДАННЫЕ ===
services = [
    {"name": "120 минут", "description": "Расслабляющий массаж (120 мин)"},
    {"name": "180 минут", "description": "Глубокий массаж всего тела (2 часа)"},
    {"name": "90 минут", "description": "Премиум массаж (1.5 часа)"},
    {"name": "240 минут", "description": "Премиум массаж (4 часа)"},
    {"name": "Эромассаж в 4 руки", "description": "Премиум массаж от двух мастеров"},
    {"name": "Массаж для жены в присутствии мужа", "description": "Разнообразьте свою сексуальную жизнь"},
]

masters = ["Эдуард Бондаренко", "Сергей Богданов", "Илья Соболев", "Глеб Коуэн", "Майкл Брандт", "Андрей Подольский"]

user_data = {}

# === ОБРАБОТЧИКИ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(s["name"], callback_data=f"service:{s['name']}")] for s in services]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Добро пожаловать в салон Pro Orgazm!\n\nВыберите желаемую продолжительность массажа:",
        reply_markup=reply_markup,
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("service:"):
        service = data.split(":")[1]
        user_data[user_id] = {"service": service}
        keyboard = [[InlineKeyboardButton(m, callback_data=f"master:{m}")] for m in masters]
        await query.edit_message_text(
            f"Вы выбрали массаж на {service}.\nТеперь выберите мастера:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data.startswith("master:"):
        master = data.split(":")[1]
        user_data[user_id]["master"] = master
        await query.edit_message_text(
            f"Отлично! Мастер: {master}.\n\n📞 Пожалуйста, отправьте свой номер телефона для записи:"
        )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_data:
        phone = update.message.text
        info = user_data[user_id]
        name = update.message.from_user.full_name
        lead_text = f"📩 Новый лид от {name}:\n\n" \
                    f"🕒 Услуга: {info['service']}\n" \
                    f"💆 Мастер: {info['master']}\n" \
                    f"📱 Телефон: {phone}"

        await context.bot.send_message(chat_id=446370284, text=lead_text)
        await update.message.reply_text("✅ Спасибо! Мы скоро свяжемся с вами. Также можете написать нам в мессенджер:")
        # Кнопки для мессенджеров
        keyboard = [
            [InlineKeyboardButton("💬 WhatsApp", url="https://wa.me/79999999999")],
            [InlineKeyboardButton("📲 Telegram", url="https://t.me/YOUR_SUPPORT_USERNAME")]
        ]
        await update.message.reply_text("Или нажмите на кнопку ниже:", reply_markup=InlineKeyboardMarkup(keyboard))
        del user_data[user_id]
    else:
        await update.message.reply_text("Пожалуйста, начните с команды /start")

# === ЗАПУСК ===
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

print("✅ Бот запущен...")
app.run_polling()
