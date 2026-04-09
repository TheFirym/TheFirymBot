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
            player_info = f"<b>Игроков:</b> {data['players']['online']}/{data['players']['max']}"
            message = f"=================================================\n🟧 {player_info}\n================================================="
            return message
        else:
            offline_message = "<b>Сервер оффлайн.</b>"
            message = f"=================================================\n🟧 {offline_message}\n================================================="
            return message
    except Exception as e:
        logger.error(f"Ошибка при получении статуса сервера: {e}")
        error_message = "<b>Не удалось получить данные о сервере.</b>"
        message = f"=================================================\n🟧 {error_message}\n================================================="
        return message

# Команда проверки статуса сервера
async def status(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text(check_server_status(), parse_mode='HTML')

# Получение списка игроков
def get_player_list():
    try:
        response = requests.get(f"https://api.mcsrvstat.us/2/{SERVER_IP}:{SERVER_PORT}")
        data = response.json()
        if data.get('online') and 'players' in data and data['players'].get('online', 0) > 0:
            players = ", ".join(data['players'].get('list', [])) if 'list' in data['players'] else "Игроки скрыты"
            online_message = f"<b>Игроки онлайн:</b> {players}"
            message = f"=================================================\n🟧 {online_message}\n================================================="
            return message
        else:
            no_players_message = "<b>Никто не играет сейчас.</b>"
            message = f"=================================================\n🟧 {no_players_message}\n================================================="
            return message
    except Exception as e:
        logger.error(f"Ошибка при получении списка игроков: {e}")
        error_message = "<b>Не удалось получить список игроков.</b>"
        message = f"=================================================\n🟧 {error_message}\n================================================="
        return message

# Команда получения списка игроков
async def players_online(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text(get_player_list(), parse_mode='HTML')

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
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("online", players))
app.add_handler(CommandHandler("start", start_command))

if __name__ == "__main__":
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass  # uvloop не установлен

    logger.info("Запуск бота...")

    # Используем бесконечный цикл, чтобы бот автоматически перезапускался при ошибках
    while True:
        try:
            # drop_pending_updates=True сбрасывает накопленные обновления при старте
            app.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Ошибка в polling: {e}")
            # Если произошла ошибка, делаем паузу перед перезапуском
            time.sleep(10)
