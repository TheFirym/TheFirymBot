import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import aiohttp  # ✅ Асинхронные запросы

# Настройки
TOKEN = os.getenv("BOT_TOKEN", "8534820807:AAGVIIiUghHGu_PX_YiV3FyzJhGquHqU5Ic")  # ✅ Токен из ENV
SERVER_IP = "213.152.43.73"
SERVER_PORT = 25620
API_URL = f"https://api.mcsrvstat.us/2/{SERVER_IP}:{SERVER_PORT}"

# Логирование
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Кэш для данных сервера (на 60 секунд)
_server_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 60

def log_user(update: Update):
    if update.effective_user:
        user = update.effective_user
        username = user.username or user.first_name or "Unknown"
        logger.info(f"Команда от {username}: {update.message.text if update.message else 'No message'}")

# ✅ Асинхронный запрос с кэшированием
async def fetch_server_data():
    import time
    now = time.time()
    if _server_cache["data"] and (now - _server_cache["timestamp"]) < CACHE_TTL:
        return _server_cache["data"]
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, timeout=10) as resp:
                data = await resp.json()
                _server_cache["data"] = data
                _server_cache["timestamp"] = now
                return data
    except Exception as e:
        logger.error(f"Ошибка API: {e}")
        return None

# ✅ Команды
async def status(update: Update, context: CallbackContext):
    log_user(update)
    data = await fetch_server_data()
    if data and data.get('online'):
        text = f"✅ Сервер онлайн! Игроков: {data['players']['online']}/{data['players']['max']}"
    elif data:
        text = "❌ Сервер оффлайн."
    else:
        text = "⚠️ Не удалось получить данные."
    await update.message.reply_text(text)

async def players(update: Update, context: CallbackContext):
    log_user(update)
    data = await fetch_server_data()
    if data and data.get('online') and data['players'].get('online', 0) > 0:
        players_list = data['players'].get('list', [])
        text = f"🎮 Онлайн ({len(players_list)}): " + (", ".join(players_list) if players_list else "Игроки скрыты")
    else:
        text = "😴 Никто не играет сейчас."
    await update.message.reply_text(text)

async def server_version(update: Update, context: CallbackContext):
    log_user(update)
    data = await fetch_server_data()
    if data and data.get('online'):
        text = f"📦 Версия: {data.get('version', 'неизвестно')}"
    else:
        text = "⚠️ Не удалось получить версию."
    await update.message.reply_text(text)

async def start_command(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text(
        "Ку! Я помощник сервера TheFirym ⛏️\n\n"
        "Команды:\n"
        "/status — Статус сервера\n"
        "/online — Игроки онлайн\n"
        "/staff — Админы и модераторы\n"
        "/ip — IP сервера\n"
        "/version — Версия сервера\n"
        "/join — Как присоединиться\n"
        "/rules — Правила"
    )

async def staff(update: Update, context: CallbackContext):
    log_user(update)
    staff_list = {
        "👑 Админ": ["Cymniki (@CKirilll)"],
        "🛡️ Модер": ["KILLAH"]
    }
    response = "\n".join([f"{role}: {', '.join(names)}" for role, names in staff_list.items()])
    await update.message.reply_text(f"👥 Состав команды:\n{response}")

async def server_ip(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text("🌐 IP: `thefirym.gomc.fun`", parse_mode='Markdown')

async def join(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text(
        "📝 Подать заявку: https://t.me/+CpN-PsMRvuExMzRi",
        disable_web_page_preview=True
    )

async def rules(update: Update, context: CallbackContext):
    log_user(update)
    await update.message.reply_text(
        "📜 Правила сервера:\n"
        "1. Не ломать чужие постройки\n"
        "2. Не грабить игроков\n"
        "3. Не убивать чужих питомцев\n"
        "4. Обязательны моды: Emotecraft + Simple Voice Chat 💬\n"
        "5. Уважать других игроков\n"
        "6. Уникальный скин обязателен"
    )

# ✅ Запуск
def main():
    # ✅ Безопасная установка лимита памяти (только Unix)
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (200 * 1024 * 1024, 200 * 1024 * 1024))
    except (ImportError, ValueError, OSError) as e:
        logger.warning(f"Не удалось установить лимит памяти: {e}")

    app = Application.builder().token(TOKEN).build()
    
    # ✅ Исправленные хэндлеры
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("online", players))    # список игроков
    app.add_handler(CommandHandler("players", players))    # дублирует /online (или уберите)
    app.add_handler(CommandHandler("staff", staff))        # ✅ отдельная команда для стаффа
    app.add_handler(CommandHandler("ip", server_ip))
    app.add_handler(CommandHandler("version", server_version))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("rules", rules))

    logger.info("🤖 Бот запущен...")
    
    # ✅ Без while True — run_polling() сам обрабатывает перезапуски
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    # ✅ Оптимизация event loop
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        logger.info("🚀 uvloop активирован")
    except ImportError:
        pass
    main()
