import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.commands import router as commands_router
from handlers.voice import router as voice_router
from handlers.support import router as support_router

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(commands_router)
    dp.include_router(voice_router)
    dp.include_router(support_router)
    print('Bot started. Press Ctrl+C to stop.')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()) 