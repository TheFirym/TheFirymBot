import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes # Импортируем ContextTypes
import requests
import asyncio
import time
# import resource # Закомментировано из-за проблем с ограничением памяти

# --- Настройки ---
# Рекомендуется использовать переменные окружения: TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TOKEN = "8534820807:AAGVIIiUghHGu_PX_YiV3FyzJhGquHqU5Ic" 
SERVER_IP = "213.152.43.73"
SERVER_PORT = 25620

# --- Настройка логирования ---
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO # или logging.DEBUG для подробного лога
)
logger = logging.getLogger(__name__) # Используем имя модуля для логгера

# --- Функция для логирования пользователей ---
def log_user(update: Update):
    if update.effective_message: # Используем effective_message для универсальности
        user = update.effective_user
        username = user.username or user.first_name or "Unknown" # Обработка случая без имени
        command_text = update.effective_message.text or "No text command"
        logger.info(f"Command from {username} (ID: {user.id}): {command_text}")

# --- Проверка статуса сервера ---
def check_server_status():
    try:
        # Увеличим таймаут для запроса
        response = requests.get(f"https://api.mcsrvstat.us/2/{SERVER_IP}:{SERVER_PORT}", timeout=10)
        response.raise_for_status() # Возбуждает исключение для bad status codes
        data = response.json()
        
        if data.get('online'):
            online_count = data['players']['online']
            max_count = data['players']['max']
            player_info = f"{online_count}/{max_count}"
            # Используем HTML форматирование в строке
            message = f"=================================================\n🟧 <b>Игроков:</b> {player_info}\n================================================="
            return message
        else:
            return "Сервер оффлайн."
    except requests.exceptions.RequestException as e: # Конкретная ошибка запроса
        logger.error(f"Ошибка HTTP при получении статуса сервера: {e}")
        return "Не удалось подключиться к API сервера."
    except ValueError: # Ошибка при разборе JSON
        logger.error("Ошибка при разборе JSON ответа от API сервера.")
        return "Получен некорректный ответ от API сервера."
    except Exception as e: # Обработка любых других исключений
        logger.error(f"Неожиданная ошибка при получении статуса сервера: {e}")
        return "Не удалось получить данные о сервере."

# --- Получение списка игроков ---
def get_player_list():
    try:
        response = requests.get(f"https://api.mcsrvstat.us/2/{SERVER_IP}:{SERVER_PORT}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('online') and 'players' in data and data['players'].get('online', 0) > 0:
            player_list = data['players'].get('list', [])
            if player_list:
                 players_str = ", ".join(player_list)
                 message = f"=================================================\n🟧 <b>Игроки онлайн:</b> {players_str}\n================================================="
            else:
                message = "=================================================\n🟧 <b>Игроки скрыты.</b>\n================================================="
            return message
        else:
            return "=================================================\n🟧 <b>Никто не играет сейчас.</b>\n================================================="
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка HTTP при получении списка игроков: {e}")
        return "Не удалось подключиться к API сервера."
    except ValueError:
        logger.error("Ошибка при разборе JSON ответа от API сервера (список игроков).")
        return "Получен некорректный ответ от API сервера."
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении списка игроков: {e}")
        return "Не удалось получить список игроков."

# --- Команда проверки статуса сервера ---
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE): # Используем ContextTypes
    log_user(update)
    try:
        status_msg = check_server_status()
        await update.effective_message.reply_text(status_msg, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Ошибка при отправке статуса: {e}")
        await update.effective_message.reply_text("Произошла ошибка при обработке запроса.")

# --- Команда получения списка игроков ---
async def players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user(update)
    try:
        players_msg = get_player_list()
        await update.effective_message.reply_text(players_msg, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Ошибка при отправке списка игроков: {e}")
        await update.effective_message.reply_text("Произошла ошибка при обработке запроса.")

# --- Команда старт ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user(update)
    try:
        start_message = (
            "=================================================\n"
            "🟧 Привет! Я помощник Майнкрафт сервера TheFirym.\n\n"
            "<b>Доступные команды:</b>\n"
            "/status - Проверить статус сервера\n"
            "/online - Список игроков онлайн\n"
            "================================================="
        )
        await update.effective_message.reply_text(start_message, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения /start: {e}")
        # Не отправляем сообщение об ошибке пользователю, чтобы не спамить

# --- Основная функция для запуска ---
async def main():
    # Создание приложения бота
    application = Application.builder().token(TOKEN).build()

    # Добавление команд
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("online", players)) # Используем то же имя, что и в start
    application.add_handler(CommandHandler("start", start_command))

    logger.info("Запуск приложения бота...")
    
    # Запуск бота в режиме polling
    # drop_pending_updates=True сбрасывает накопленные обновления при старте
    await application.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # Настройка asyncio event loop
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        logger.info("uvloop установлен и используется.")
    except ImportError:
        logger.info("uvloop не установлен, используется стандартный asyncio loop.")
    
    # Запуск основной асинхронной функции
    asyncio.run(main())
