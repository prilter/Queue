# BASE AIOGRAM
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# ARGUMENTS FOR COMMANDS
from aiogram import F

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
    # ADD NEW USER TO DATASET
    uid = message.from_user.id
    if uid not in users_db:
        users_db.add(uid)
    #logging.info(" ".join(users_db))
    #print(users_db)

    # "HELLO" MESSAGE
    await message.answer(
        "👋 Привет! Я ответственен за распределение людей на очередь в БСБО-51-25, чтобы не возникало путаниц.\n\n!!!Важно!!!: пока я работаю только с очередью на историю\n\nВыбери действие:\n\n"
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
    await message.answer( f"{rules}")

# CHECK QUEUE CMD
@dp.message(Command("queue"))
async def cmd_queue(message: Message):
    arg = message.text[len("/queue"):].strip() or ""
    if arg == "": await message.answer( f"{no_args}" ); return

    if arg.lower() == "история": await message.answer( f"Вот очередь:\n\n{'\n'.join(hist_list)}" if hist_list else "Очереди нет!" )
    elif arg.lower() == "орг":   await message.answer( f"Вот очередь:\n\n{'\n'.join(org_list)}"  if org_list  else "Очереди нет!" )
    else:                        await message.answer( f"{cannot_recognize}" )


# SEND NOTIFICATION EVERY SATURDAY
async def send_notification():
    now = datetime.now()

    # HISTORY
    if now.weekday() == 2 and now.hour == 7:
        for user_id in list(users_db):
            try:
                await bot.send_message( chat_id=user_id, text=history_not, parse_mode="Markdown")
                logging.info(f"Sended message to {user_id}")
            except Exception as e:
                logging.error(f"Cannot send message to {user_id}: {e}")
                if "blocked" in str(e).lower() or "not found" in str(e).lower(): # Delete non-active users 
                    users_db.discard(user_id)

    # ORG
    if now.weekday() == 3 and now.hour == 11:
        for user_id in list(users_db):
            try:
                await bot.send_message( chat_id=user_id, text=org_not, parse_mode="Markdown")
                logging.info(f"Sended message to {user_id}")
            except Exception as e:
                logging.error(f"Cannot send message to {user_id}: {e}")
                if "blocked" in str(e).lower() or "not found" in str(e).lower(): # Delete non-active users 
                    users_db.discard(user_id)

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

