import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import requests
import asyncio
import resource
import time

# Установим лимит памяти в 200 МБ (можно изменить)
resource.setrlimit(resource.RLIMIT_AS, (200 * 1024 * 1024, 200 * 1024 * 1024))

# Настройки
TOKEN = "8534820807:AAGVIIiUghHGu_PX_YiV3FyzJhGquHqU5Ic"
SERVER_IP = "213.152.43.73"
SERVER_PORT = 25620

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()

# Функция для логирования пользователей
def log_user(update: Update):
    if update.message:
        user = update.message.from_user
        username = user.username if user.username else user.first_name
        logger.info(f"Команда от {username}: {update.message.text}")

# Проверка статуса сервера
def check_server_status():
    try:
        response = requests.get(f"https://api.mcsrvstat.us/2/{SERVER_IP}:{SERVER_PORT}")
        data = response.json()
        if data.get('online'):
            player_info = f"Игроков: {data['players']['online']}/{data['players']['max']}"
            message = f"=================================================\n🟧 {player_info}\n================================================="
            return message
        else:
            return "Сервер оффлайн."
    except Exception as e:
        logger.error(f"Ошибка при получении статуса сервера: {e}")
        return "Не удалось получить данные о сервере."

# Получение списка игроков
def get_player_list():
    try:
        response = requests.get(f"https://api.mcsrvstat.us/2/{SERVER_IP}:{SERVER_PORT}")
        data = response.json()
        if data.get('online') and 'players' in data and data['players'].get('online', 0) > 0:
            players = ", ".join(data['players'].get('list', [])) if 'list' in data['players'] else "Игроки скрыты"
            return f"=================================================\n🟧 Игроки онлайн: {players}\n================================================="
        else:
            return "=================================================\n🟧 Никто не играет сейчас.\n================================================="
    except Exception as e:
        logger.error(f"Ошибка при получении списка игроков: {e}")
        return "Не удалось получить список игроков."

# Команда проверки статуса сервера
async def status(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text(check_server_status())

# Команда получения списка игроков
async def players(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text(get_player_list())

# Команда старт
async def start_command(update: Update, context: CallbackContext):
    log_user(update)
    start_message = (
        "=================================================\n"
        "🟧 Привет! Я помощник Майнкрафт сервера TheFirym.\n\n"
        "<b>Доступные команды:</b>\n"
        "/status - Проверить статус сервера\n"
        "/online - Список игроков онлайн\n"
        "================================================="
    )
    await update.message.reply_text(start_message, parse_mode='HTML')

# Создание приложения бота
app = Application.builder().token(TOKEN).build()

# Добавление команд
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("online", players))
    app.add_handler(CommandHandler("start", start_command))
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    import asyncio
    logger.info("Запуск бота...")
    asyncio.run(main())
