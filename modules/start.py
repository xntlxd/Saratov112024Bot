import asyncio
from types import NoneType
from aiogram import Router, F
from aiogram import types
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.database import cur, con

router = Router()


@router.message(Command("start"))
async def start_point(message: Message):
    finishKey = InlineKeyboardBuilder()
    finishKey.row(types.InlineKeyboardButton(text="Завершить", callback_data="finish_register"))
    id_user = message.from_user.id
    fullname_user = message.from_user.full_name
    cur.execute("SELECT `person`.`id`, `person`.`balance`, `accounts`.`admin` FROM `person` JOIN `accounts` on `person`.`id`=`accounts`.`to_person` WHERE `accounts`.`id_tg` = ?", (id_user, ))
    try:
        fetch_person = cur.fetchone()
        id_person = fetch_person[0]
        balance_person = fetch_person[1]
        admin_status = fetch_person[2]
        message_answer = f'Ваши данные, <b>{fullname_user}</b>:\nIDs: <b>{id_person}</b>\nIDtg: <b>{id_user}</b>\nБаланс: <b>{balance_person}</b>\n\nВаши девайсы: /devices,\nПомощь: /help'
        if admin_status == 1:
            message_answer += f'\n<b>Вы являетесь администратором!</b>'
        await message.answer(message_answer)
    except:
        await message.reply(f"Пользователь <b>{fullname_user}</b>:\nЧтобы завершить регистрацию нажмите на кнопку снизу.", reply_markup=finishKey.as_markup())


@router.callback_query(F.data == "finish_register")
async def finish_register(callback: types.CallbackQuery):
    username_user = callback.from_user.username
    id_user = callback.from_user.id
    cur.execute("INSERT INTO `person` (`username`) VALUES (?)", (username_user, ))
    id_person = cur.lastrowid
    cur.execute("INSERT INTO `accounts` (`id_tg`, `to_person`) VALUES (?, ?)", (id_user, id_person, ))
    con.commit()
    await callback.answer(f"Вы были зарегистрированы")
    await callback.message.answer("Добро пожаловать в систему управления умным домом")
    await callback.message.delete()

@router.message(Command("delete_account"))
async def end_point(message: Message):
    finishKey = InlineKeyboardBuilder()
    finishKey.row(types.InlineKeyboardButton(text="Подтвердить", callback_data="finish_delete"))
    id_user = message.from_user.id
    fullname_user = message.from_user.full_name
    cur.execute(
        "SELECT `person`.`id` FROM `person` JOIN `accounts` on `person`.`id`=`accounts`.`to_person` WHERE `accounts`.`id_tg` = ?",
        (id_user,))
    if type(cur.fetchone()) == NoneType:
        await message.reply(f"Вы не зарегистрированны в системе.")
    else:
        await message.reply(f"Чтобы завершить удаление аккаунта, подтвердите нажав на кнопку снизу", reply_markup=finishKey.as_markup())

@router.callback_query(F.data == "finish_delete")
async def finish_delete(callback: CallbackQuery):
    id_user = callback.from_user.id
    cur.execute("""
        SELECT `person`.`id`
        FROM `person`
        JOIN `accounts` ON `person`.`id` = `accounts`.`to_person`
        WHERE `accounts`.`id_tg` = ?""", (id_user, ))
    id_person = cur.fetchone()[0]
    cur.execute("DELETE FROM `person` WHERE `person`.`id` = ?", (id_person, ))
    cur.execute("DELETE FROM `accounts` WHERE `accounts`.`id_tg` = ?", (id_user, ))
    con.commit()
    await callback.answer(f"{callback.from_user.full_name}, был удален!")
    await callback.message.delete()
