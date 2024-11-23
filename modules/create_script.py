import asyncio
from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.filters.command import Command

router = Router()

@router.message(F.text)
async def create_script(message: Message):
    await message.answer("Тест!")
