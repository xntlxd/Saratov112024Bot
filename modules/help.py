import asyncio
from types import NoneType
from aiogram import Router, F
from aiogram import types
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.database import cur, con

router = Router()

@router.message(Command("help"))
async def show_help(message: Message):
    message_help = '<b>/команда - описание команды</b>\n/start - Регистрация или вывод данных пользователя.\n/delete_account - Удаление аккаунта.\n/help - Список команд и их описание.\n/about - О боте.\n/connect "id" - Добавить устройство.\n/disconnect "id" - Рассоединить устройства.\n/on "id" - Включить устройство.\n/off "id" - Выключить устройство.'
    await message.answer(message_help)

@router.message(Command("about"))
async def show_about(message: Message):
    message_about = "Бот создан для хакатона \"Заряд\", командой WaterTop.\n<a href='tg://user?id=6782009240'>Бехтягин Михаил</a>, <a href='tg://user?id=565066030'>Петрова Валерия</a>, <a href='tg://user?id=1989420942'>Орлова Лилия</a>.\nСпециально для Ростелекома."
    await message.answer(message_about)