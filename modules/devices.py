from types import NoneType
from aiogram import Router, F, html
from aiogram.types import Message
from aiogram.filters.command import Command
from database.database import cur, con

router = Router()

@router.message(Command("devices"))
async def show_device(message: Message):
    id_user = message.from_user.id
    cur.execute("SELECT `user_devices`.`id` as uid, `user_devices`.`local_name` as lname, `user_devices`.`status` FROM `accounts` JOIN `person` on `accounts`.`to_person` = `person`.`id` JOIN `user_devices` on `person`.`id` = `user_devices`.`to_person` JOIN `devices` on `user_devices`.`id_device` = `devices`.`id` JOIN `GLOBAL` on `devices`.`global_info` = `GLOBAL`.`id` JOIN `manufacturer` ON `GLOBAL`.`manufacturer` = `manufacturer`.`id` WHERE `accounts`.`id_tg` = ?", (id_user, ))
    devices = cur.fetchall()
    devices_msg = 'Список ваших устройств: (ID | Название | Состояние)'
    for device in devices:
        if device[2] == 0:
            status = 'Выключен'
        else:
            status = 'Включен'
        devices_msg += f'\n{device[0]}: {device[1]} - {status}'

    devices_msg += '\n\nДля подключения новых устройств, введите /connect'

    await message.answer(devices_msg)

@router.message(Command("connect"))
async def go_connect(message: Message, command: Command):
    try:
        command_args: str = command.args
        print(1)
        cur.execute("SELECT `devices`.`id`, `GLOBAL`.`global_name` FROM `devices` JOIN `GLOBAL` on `devices`.`global_info` = `GLOBAL`.`id` WHERE `GLOBAL`.`id` = ?", (command_args, ))
        selector = cur.fetchone()
        print(selector)
        id_device = selector[0]
        name_device = selector[1]
        id_user = message.from_user.id
        cur.execute("SELECT `person`.`id` FROM `person` JOIN `accounts` on `person`.`id` = `accounts`.`to_person` WHERE `accounts`.`id_tg` = ?", (id_user, ))
        print(1)
        id_person = cur.fetchone()[0]
        cur.execute("INSERT INTO `user_devices` (`to_person`, `id_device`, `local_name`) VALUES (?, ?, ?)", (id_person, id_device, name_device))
        print(1)
        con.commit()
        await message.answer(f"Устройство: {html.bold(html.quote(name_device))} - было подключено!")

    except:
        cur.execute(
            "SELECT `GLOBAL`.`id`, `GLOBAL`.`global_name`, `manufacturer`.`name`, `GLOBAL`.`type` FROM `GLOBAL` JOIN `manufacturer` on `GLOBAL`.`manufacturer` = `manufacturer`.`id`")
        devices = cur.fetchall()
        devices_msg = f'ID | Производитель - Название | Тип устройства\nДля подключения напишите <code>/connect</code> "ID устройства"'
        for device in devices:
            devices_msg += f'\n{device[0]}: {device[2]} - {device[1]} | {device[3]}'
        await message.answer(devices_msg)

@router.message(Command("disconnect"))
async def disconnect_device(message: Message, command: Command):
    try:
        command_args: str = command.args
        id_user = message.from_user.id
        cur.execute("SELECT `person`.`id` FROM `person` JOIN `accounts` ON `person`.`id`=`accounts`.`to_person` WHERE `accounts`.`id_tg` = ?", (id_user, ))
        id_person = cur.fetchone()[0]
        cur.execute("SELECT `user_devices`.`id`, `user_devices`.`local_name` FROM `user_devices` WHERE `user_devices`.`id` = ? AND `user_devices`.`to_person` = ?", (command_args, id_person, ))
        device_data = cur.fetchone()
        print(device_data)
        if type(device_data) == NoneType:
            await message.answer(f"Вы попытались рассоединить не ваше устройство!")
        else:
            cur.execute("DELETE FROM `user_devices` WHERE `user_devices`.`id` = ? AND `user_devices`.`to_person` = ?",
                        (command_args, id_person,))
            con.commit()
            await message.answer(f"Вы отключились от устройства: {html.bold(device_data[1])}")
    except:
        await message.answer(f'Произошла ошибка!')

@router.message(Command("on"))
async def device_on(message: Message, command: Command):
    try:
        command_args: str = command.args
        id_user = message.from_user.id
        cur.execute(
            "SELECT `person`.`id` FROM `person` JOIN `accounts` ON `person`.`id`=`accounts`.`to_person` WHERE `accounts`.`id_tg` = ?",
            (id_user,))
        id_person = cur.fetchone()[0]
        cur.execute(
            "SELECT `user_devices`.`id`, `user_devices`.`local_name` FROM `user_devices` WHERE `user_devices`.`id` = ? AND `user_devices`.`to_person` = ?",
            (command_args, id_person,))
        device_data = cur.fetchone()
        if type(device_data) == NoneType:
            await message.answer(f"Вы попытались включить не ваше устройство!")
        else:
            cur.execute("UPDATE `user_devices` SET `status` = '1' WHERE `user_devices`.`id` = ? AND `user_devices`.`to_person` = ?",
                        (command_args, id_person,))
            con.commit()
            await message.answer(f"Вы включили устройство: {html.bold(device_data[1])}")

    except:
        await message.answer(f'Произошла ошибка!')

@router.message(Command("off"))
async def device_off(message: Message, command: Command):
    try:
        command_args: str = command.args
        id_user = message.from_user.id
        cur.execute(
            "SELECT `person`.`id` FROM `person` JOIN `accounts` ON `person`.`id`=`accounts`.`to_person` WHERE `accounts`.`id_tg` = ?",
            (id_user,))
        id_person = cur.fetchone()[0]
        cur.execute(
            "SELECT `user_devices`.`id`, `user_devices`.`local_name` FROM `user_devices` WHERE `user_devices`.`id` = ? AND `user_devices`.`to_person` = ?",
            (command_args, id_person,))
        device_data = cur.fetchone()
        if type(device_data) == NoneType:
            await message.answer(f"Вы попытались выключить не ваше устройство!")
        else:
            cur.execute("UPDATE `user_devices` SET `status` = '0' WHERE `user_devices`.`id` = ? AND `user_devices`.`to_person` = ?",
                        (command_args, id_person,))
            con.commit()
            await message.answer(f"Вы выключили устройство: {html.bold(device_data[1])}")

    except:
        await message.answer(f'Произошла ошибка!')

@router.message(Command("rename"))
async def rename_device(message: Message, command: Command):
    try:
        command_args: str = command.args
        id_device = command_args.split()[0]
        name_device = command_args.split()[1]
        id_user = message.from_user.id
        cur.execute(
            "SELECT `person`.`id` FROM `person` JOIN `accounts` ON `person`.`id`=`accounts`.`to_person` WHERE `accounts`.`id_tg` = ?",
            (id_user, ))
        id_person = cur.fetchone()[0]
        cur.execute(
            "SELECT `user_devices`.`id`, `user_devices`.`local_name` FROM `user_devices` WHERE `user_devices`.`id` = ? AND `user_devices`.`to_person` = ?",
            (id_device, id_person,))
        device_data = cur.fetchone()
        if type(device_data) == NoneType:
            await message.answer(f"Вы попытались изменить не ваше устройство!")
        else:
            cur.execute("UPDATE `user_devices` SET `local_name` = ? WHERE `user_devices`.`id` = ? AND `user_devices`.`to_person` = ?",
                        (name_device, id_device, id_person, ))
            con.commit()
            await message.answer(f"Вы изменили имя устройства на: {html.bold(name_device)}")

    except:
        await message.answer(f'Произошла ошибка!')


    
