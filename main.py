import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.commands import router as commands_router
from handlers.voice import router as voice_router
from handlers.support import router as support_router
from handlers import practice_handler, operator_handler  # ← добавили импорт

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 Запуск бота SpeakSmart...")
    
    try:
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher()
        
        # Подключаем роутеры
        dp.include_router(commands_router)
        dp.include_router(voice_router)
        dp.include_router(support_router)
        dp.include_router(practice_handler.router)
        dp.include_router(operator_handler.router)
        
        logger.info("✅ Все роутеры подключены")
        logger.info("🤖 Бот запущен. Нажмите Ctrl+C для остановки.")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main())
