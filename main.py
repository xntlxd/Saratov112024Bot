import asyncio

from aiogram.client.default import DefaultBotProperties

from database.database import con, cur
from aiogram.filters import Command

from config import TOKEN
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from modules import create_script, start, devices, help

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_routers(start.router, devices.router, help.router)

print('Бот запущен')

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())