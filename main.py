# BASE AIOGRAM
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# FILES WITH VARIABLES
import APIS
from info import *

# MAIN
BOT_TOKEN = APIS.BOT_API
logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)

# START CMD
@dp.message(Command("start"))
async def cmd_start(message: Message):
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

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

