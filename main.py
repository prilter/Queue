# BASE AIOGRAM
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# SECRET VARIABLES
from dotenv import load_dotenv
from os import getenv

# REPLY BUTTON
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F

# INLINE BUTTON
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# CHECKING DAY
from datetime import datetime, time

# FILES WITH VARIABLES
from info import *
from db   import *

# MAIN
load_dotenv() # LOAD .env
BOT_TOKEN = getenv("BOT_API")
logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)

# START CMD
@dp.message(Command("start"))
async def cmd_start(message: Message):
    # UID
    uid, uname = message.from_user.id, message.from_user.username
    adduser(uid, uname, None)
    print(get_all_users())

    # REPLY BUTTONS
    kb = [
        [types.KeyboardButton(text=help_button_text),  types.KeyboardButton(text=rules_button_text), types.KeyboardButton(text=choose_subject_text)],
        [types.KeyboardButton(text=check_button_text), types.KeyboardButton(text=join_button_text), types.KeyboardButton(text=done_button_text)]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    # GREETING MESSAGE
    await message.answer(
        f"👋 Привет! Я ответственен за распределение людей на очередь в {group_name}, чтобы не возникало путаниц.\n\nВыбери действие:\n\n"
        f"{commands_list}",
        reply_markup=keyboard
    )

# HELP CMD
@dp.message(F.text == help_button_text)
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
@dp.message(F.text == rules_button_text)
async def cmd_rules(message: Message):
    await message.answer( f"{rules}" )

# CHOOSE SUBJECT
@dp.message(F.text == choose_subject_text)
async def cmd_select_sub(message: Message):
    # CHECK USERNAME
    uid, uname = message.from_user.id, message.from_user.username

    # INLINE BUTTONS
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📂 {org_name}",  callback_data="org")],
        [InlineKeyboardButton(text=f"📖 {hist_name}", callback_data="hist")],
    ])
    await message.answer("📚 Выбери:", reply_markup=inline_kb)


@dp.callback_query(F.data == "org") 
async def hist_selected(callback: CallbackQuery):
    uid, uname = callback.from_user.id, callback.from_user.username
    user = get_user(uid)
    
    adduser(uid, uname, org_name)
    logging.info(f"@{uname} choosed {org_name}")
    await callback.message.edit_text(f"✅ Выбраны {org_name}")

@dp.callback_query(F.data == "hist")
async def hist_selected(callback: CallbackQuery):
    uid, uname = callback.from_user.id, callback.from_user.username
    user = get_user(uid)
    
    adduser(uid, uname, hist_name)
    logging.info(f"@{uname} choosed {hist_name}")
    await callback.message.edit_text(f"✅ Выбрана {hist_name}")
    
# CHECK QUEUE CMD
@dp.message(F.text == check_button_text)
async def cmd_queue(message: Message):
    uid, uname = message.from_user.id, message.from_user.username
    
    user = get_user(uid)
    
    if   user["sub"] == hist_name: queue = get_queue_by_sub(hist_name); await message.answer(f"Вот очередь на предмет {user['sub']}:\n\n{'\n'.join(queue)}" if queue else no_queue)
    elif user["sub"] == org_name:  queue = get_queue_by_sub(org_name);  await message.answer(f"Вот очередь на предмет {user['sub']}:\n\n{'\n'.join(queue)}" if queue else no_queue)
    else:                          await message.answer(f"{no_sub}")

    logging.info(f"@{uname}: {check_queue_log}({user['sub']})")

# GET POSITION
@dp.message(F.text == join_button_text)
async def cmd_join(message: Message):
    now = datetime.now()
    uid, uname = message.from_user.id, message.from_user.username

    # CHECK USER
    user = get_user(uid)
    if not user or not user["sub"]:
        await message.answer(f" {no_sub} ")
        return

    # CHECK HAS USER ENTRY
    if get_user_position(uid, user["sub"]) > 0:
        await message.answer(f"⚠️ Ты уже в очереди на {user['sub']}!")
        logging.info(f"@{uname}: {entries_limit_log}")
        return
    
    # CHECK IS PERMITTED JOINING(TIME OF REGISTRATION)
    if not is_kill_time_limit:
        if (user["sub"] == hist_name and not(now.weekday() == 2 and 9  <= now.hour <= 12)): await message.answer(f"{locked_auth}"); logging.info(f"@{uname}: {time_limit_log}"); return
        if (user["sub"] == org_name  and not(now.weekday() == 3 and 11 <= now.hour <= 18)): await message.answer(f"{locked_auth}"); logging.info(f"@{uname}: {time_limit_log}"); return
    
    # ADD
    if add_to_list(uid, uname, user["sub"]):
        pos = get_user_position(uid, user["sub"])
        logging.info(f"@{uname}: {adding_user_log} {user['sub']} ({pos} position)")
        logging.info(f"{get_all_users()}")
        await message.answer( f"✅ @{uname} добавлен в очередь {user['sub']}!\n📋 Твоя позиция: {pos}")
    else:
        logging.info(f"@{uname}: {adding_user_err_log} {user['sub']}")
        await message.answer(f"{cannot_add}")

@dp.message(F.text == done_button_text)
async def cmd_done(message: Message):
    uid, uname = message.from_user.id, message.from_user.username
    user = get_user(uid)
        
    if user["sub"] == org_name or user["sub"] == hist_name:
        mark_done(uid, user["sub"])
        logging.info(f"@{uname}: {del_user_from_queue_log}")
    else:                                        
        await message.answer(no_sub)

# ADMIN: LIMITS
@dp.message(Command("limits"))
async def cmd_limits(message: Message):
    global is_kill_time_limit
    if message.text[len("/limits"):].strip() == getenv("kill_limits_pass"):
        is_kill_time_limit = not is_kill_time_limit
        await message.answer( f"Админ изменил параметр is_kill_time_limit: {is_kill_time_limit}" )
    else:
        await message.answer( f"Неверный пароль администратора" )
    logging.info(f"@{message.from_user.username}: {superuser_operation_log}")

# SEND NOTIFICATION EVERY SATURDAY
async def send_notification():
    users_db, now = get_all_users(), datetime.now()
    
    # HISTORY
    if now.weekday() == 2 and now.hour == 9:
        for uid, data in users_db.items():
            try:
                await bot.send_message(chat_id=uid, text=history_not)
                logging.info(f"@{data.get('uname', 'Unknown')}: {sending_mes_log}")
            except Exception as e:
                logging.error(f"@{data.get('uname', 'Unknown')}: {sending_mes_err_log} ({e})")
                if "blocked" in str(e).lower() or "not found" in str(e).lower():
                    delete_user(uid)

    # ORG
    if now.weekday() == 3 and now.hour == 11:
        for uid, data in users_db.items():
            try:
                await bot.send_message(chat_id=uid, text=org_not)
                logging.info(f"@{data.get('username', 'Unknown')}: {sending_mes_log}")
            except Exception as e:
                logging.error(f"@{data.get('username', 'Unknown')}: {sending_mes_err_log} ({e})")
                if "blocked" in str(e).lower() or "not found" in str(e).lower(): # Delete non-active users 
                    delete_user(uid)

# CHECK EVERY HOUR NOTIFICATION
async def notification_checker():
    while True:
        await send_notification()
        await asyncio.sleep(1800) # WAIT 1H

async def main():
    init_db()
    asyncio.create_task(notification_checker())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
