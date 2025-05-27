import asyncio
from aiogram import Dispatcher, Bot
from config import TOKEN
from bot.handlers.user import user
from bot.handlers.user_settings import user as user_settings
from datetime import datetime
from database.models import async_main
from bot.functions.requests import Database

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_routers(user,user_settings)
    dp.startup.register(on_startup)

    await dp.start_polling(bot)

async def on_startup(bot:Bot):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[INFO] {now} - ✅ Бот успешно запущен.")
    await async_main()
    await Database.create_config()
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


