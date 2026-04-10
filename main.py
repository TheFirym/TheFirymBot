import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import requests
import asyncio
import resource

# Установим лимит памяти в 200 МБ
try:
    resource.setrlimit(resource.RLIMIT_AS, (200 * 1024 * 1024, 200 * 1024 * 1024))
except (ValueError, OSError):
    pass

TOKEN = "8534820807:AAGVIIiUghHGu_PX_YiV3FyzJhGquHqU5Ic"
SERVER_IP = "213.152.43.73"
SERVER_PORT = 25620

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()

def log_user(update: Update):
    if update.message:
        user = update.message.from_user
        username = user.username or user.first_name
        logger.info(f"Команда от {username}: {update.message.text}")

def check_server_status():
    try:
        response = requests.get(f"https://api.mcsrvstat.us/2/{SERVER_IP}:{SERVER_PORT}")
        data = response.json()
        if data.get('online'):
            info = f"Игроков: {data['players']['online']}/{data['players']['max']}"
            return f"=================================================\n🟧 {info}\n================================================="
        return "Сервер оффлайн."
    except Exception as e:
        logger.error(f"Ошибка статуса: {e}")
        return "Не удалось получить данные."

def get_player_list():
    try:
        response = requests.get(f"https://api.mcsrvstat.us/2/{SERVER_IP}:{SERVER_PORT}")
        data = response.json()
        if data.get('online') and data['players'].get('online', 0) > 0:
            players = ", ".join(data['players'].get('list', [])) or "Игроки скрыты"
            return f"=================================================\n🟧 Игроки онлайн: {players}\n================================================="
        return "=================================================\n🟧 Никто не играет.\n================================================="
    except Exception as e:
        logger.error(f"Ошибка списка: {e}")
        return "Не удалось получить список."

async def status(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text(check_server_status())

async def players(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text(get_player_list())

async def start_command(update: Update, context: CallbackContext):
    log_user(update)
    msg = (
        "=================================================\n"
        "🟧 Привет! Помощник TheFirym.\n\n"
        "<b>Команды:</b>\n"
        "/status - Статус сервера\n"
        "/online - Онлайн игроки\n"
        "================================================="
    )
    await update.message.reply_text(msg, parse_mode='HTML')

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("online", players))
    app.add_handler(CommandHandler("start", start_command))
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
