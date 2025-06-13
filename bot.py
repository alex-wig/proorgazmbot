# bot.py — минимальный webhook-пример
import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = FastAPI()
tg_app = Application.builder().token(BOT_TOKEN).build()

@tg_app.command("start")
async def start_cmd(update: Update, context):
    await update.message.reply_text("✅ Бот работает")

@app.on_event("startup")
async def set_webhook():
    await tg_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)
    return {"ok": True}
