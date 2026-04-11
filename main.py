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
            return f"Сервер онлайн! Игроков: {data['players']['online']}/{data['players']['max']}"
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
            return f"Огузки онлайн: {players}"
        else:
            return "Никто не играет сейчас."
    except Exception as e:
        logger.error(f"Ошибка при получении списка игроков: {e}")
        return "Не удалось получить список игроков."

# Получение версии сервера
def get_server_version():
    try:
        response = requests.get(f"https://api.mcsrvstat.us/2/{SERVER_IP}:{SERVER_PORT}")
        data = response.json()
        if data.get('online'):
            return f"Версия сервера: {data.get('version', 'неизвестно')}"
        else:
            return "Не удалось получить версию сервера."
    except Exception as e:
        logger.error(f"Ошибка при получении версии сервера: {e}")
        return "Не удалось получить версию сервера."

# Команда проверки статуса сервера
async def status(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text(check_server_status())

# Команда получения списка игроков
async def players(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text(get_player_list())

# Команда получения версии сервера
async def server_version(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text(get_server_version())

# Команда старт
async def start_command(update: Update, context: CallbackContext):
    log_user(update)
    start_message = (
        "Ку! Я помощник майнкрафт сервера TheFirym\n\n"
        "Доступные команды:\n"
        "/status - Проверить статус сервера\n"
        "/online - Список игроков онлайн\n"
        "/players - Состав сервера\n"
        "/ip - Показать IP сервера\n"
        "/version - Показать версию сервера\n"
        "/join - Присоединиться к нашему серверу Minecraft\n"
        "/rules - Правила сервера"
    )
    await update.message.reply_text(start_message)

# Команда получения списка админов и модераторов
async def staff(update: Update, context: CallbackContext):
    log_user(update)
    staff_list = {
        "Админ": ["Cymniki(@CKirilll)"],
         "Не Модер": ["KILLAH"]
       }
    response = "\n".join([f"{role}: {', '.join(names)}" for role, names in staff_list.items()])
    await update.message.reply_text(f"Состав сервера:\n{response}")

# Команда получения IP сервера
async def server_ip(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text("IP сервера: thefirym.gomc.fun")

# Команда для присоединения
async def join(update: Update, context: CallbackContext):
    log_user(update)
    join_message = "КАНАЛ ДЛЯ ЗАЯВКИ: https://t.me/+CpN-PsMRvuExMzRi"
    await update.message.reply_text(join_message)

# Команда для правил
async def rules(update: Update, context: CallbackContext):
    log_user(update)
    rules_message = (
        "Правила сервера:\n"
        "1. Не ломать чужие постройки\n"
        "2. Не грабить игроков\n"
        "3. Не убивать домашних животных, которые принадлежат не вам\n"
        "4. Запрещается быть без мода Emotecraft и Simple Voice Chat 💬\n"
        "5. Уважать остальных участников сервера\n"
        "6. У каждого игрока должен быть свой скин"
    )
    await update.message.reply_text(rules_message)

# Создание приложения бота
app = Application.builder().token(TOKEN).build()

# Добавление команд
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("online", players))
app.add_handler(CommandHandler("players", staff))
app.add_handler(CommandHandler("ip", server_ip))
app.add_handler(CommandHandler("version", server_version))
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("join", join))
app.add_handler(CommandHandler("rules", rules))

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
