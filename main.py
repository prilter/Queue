# BASE AIOGRAM
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# CHECKING DAY
from datetime import datetime, time

# FILES WITH VARIABLES
import APIS
from info import *
from logic import *

# MAIN
BOT_TOKEN = APIS.BOT_API
logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)

# START CMD
@dp.message(Command("start"))
async def cmd_start(message: Message):
    uid, uname = message.from_user.id, message.from_user.username
    adduser(uid, uname)
    if users_db: print(users_db)

    # GREETING MESSAGE
    await message.answer(
        f"👋 Привет! Я ответственен за распределение людей на очередь в {group_name}, чтобы не возникало путаниц.\n\nВыбери действие:\n\n"
        f"{commands_list}"
    )

# HELP CMD
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Доступные команды:\n\n"
        f"{commands_list}"
    )

# SRC CMD
@dp.message(Command("src"))
async def cmd_src(message: Message):
    await message.answer(
        f"Контрибьюторы:                 {contributers}\n"
        f"Ссылка на главный репозиторий: {src_rep}"
    )

# RULES CMD
@dp.message(Command("rules"))
async def cmd_rules(message: Message):
    await message.answer( f"{rules}" )

# CHECK QUEUE CMD
@dp.message(Command("queue"))
async def cmd_queue(message: Message):
    arg = message.text[len("/queue"):].strip() or ""
    if arg == "": await message.answer( f"{no_args}" ); return

    if arg.lower() == "история": await message.answer( f"Вот очередь:\n\n{'\n'.join(get_unames_by_list(hist_list))}" if hist_list else "Очереди нет!" )
    elif arg.lower() == "орг":   await message.answer( f"Вот очередь:\n\n{'\n'.join(get_unames_by_list(org_list))}"  if org_list  else "Очереди нет!" )
    else:                        await message.answer( f"{cannot_recognize}" )


# GET POSITION
@dp.message(Command("join"))
async def cmd_join(message: Message):
    arg = message.text[len("/join"):].lower().strip()
    
    # PARSE ARG
    if arg == "":
        await message.answer( f" {no_args} ")
        return

    uid, uname = message.from_user.id, message.from_user.username
    
    # CHECK HAS USER ENTRY
    if (arg == "орг" and uid in org_list) or (arg == "история" and uid in hist_list):
        await message.answer( f"⚠️ Ты ужe в очереди {arg}!" )
        logging.info(f"@{uname} tried to join to queue more than 1 time")
        return
    
    # ADD
    if add_to_list(uid, uname, arg):
        logging.info(f"@{uname} was added to {arg} queue")
        await message.answer(
            f"✅ @{uname} добавлен в очередь {arg}!\n\n"
            f"{get_list_status()}"
        )
    else:
        logging.info(f"Cannot add {uname} to {arg} queue")
        await message.answer("❌ Ошибка добавления :( ")


# SEND NOTIFICATION EVERY SATURDAY
async def send_notification():
    now = datetime.now()

    # HISTORY
    if now.weekday() == 2 and now.hour == 7:
        for uid in list(users_db):
            try:
                await bot.send_message( chat_id=uid, text=history_not )
                logging.info(f"Sended message to {uid}")
            except Exception as e:
                logging.error(f"Cannot send message to {uid}: {e}")
                if "blocked" in str(e).lower() or "not found" in str(e).lower(): # Delete non-active users 
                    users_db.discard(uid)

    # ORG
    if now.weekday() == 3 and now.hour == 11:
        for uid in list(users_db):
            try:
                await bot.send_message( chat_id=uid, text=org_not )
                logging.info(f"Sended message to {uid}")
            except Exception as e:
                logging.error(f"Cannot send message to {uid}: {e}")
                if "blocked" in str(e).lower() or "not found" in str(e).lower(): # Delete non-active users 
                    users_db.discard(uid)

# CHECK EVERY HOUR NOTIFICATION
async def notification_checker():
    while True:
        await send_notification()
        await asyncio.sleep(3600) # WAIT 1H

async def main():
    asyncio.create_task(notification_checker())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

