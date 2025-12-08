# BASE AIOGRAM
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# REPLY BUTTON
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F

# INLINE BUTTON
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

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
    # UID
    uid, uname = message.from_user.id, message.from_user.username
    adduser(uid, uname, None)
    if users_db: print(users_db)

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
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 Орг",     callback_data="org")],
        [InlineKeyboardButton(text="📖 История", callback_data="hist")],
    ])
    await message.answer("📚 Выбери:", reply_markup=inline_kb)

@dp.callback_query(F.data == "org")
async def org_selected(callback: CallbackQuery):
    uid, uname = callback.from_user.id, callback.from_user.username

    adduser(uid, uname, org_name)
    await callback.message.edit_text(f"✅Выбрано {org_name}")
    await callback.answer(f"{org_name} выбран!")

    print(users_db)

@dp.callback_query(F.data == "hist") 
async def hist_selected(callback: CallbackQuery):
    uid, uname = callback.from_user.id, callback.from_user.username

    adduser(uid, uname, hist_name)
    await callback.message.edit_text(f"✅ Выбрана {hist_name}")
    await callback.answer(f"{hist_name} выбрана!")

    print(users_db)


# CHECK QUEUE CMD
@dp.message(F.text == check_button_text)
async def cmd_queue(message: Message):
    uid = message.from_user.id
    if users_db[uid]["subject"]   == hist_name: await message.answer( f"Вот очередь:\n\n{'\n'.join(get_unames_by_list(hist_list))}" if hist_list else "Очереди нет!" )
    elif users_db[uid]["subject"] == org_name:  await message.answer( f"Вот очередь:\n\n{'\n'.join(get_unames_by_list(org_list))}"  if org_list  else "Очереди нет!" )
    else:                                       await message.answer( f"{no_sub}" )


# GET POSITION
@dp.message(F.text == join_button_text)
async def cmd_join(message: Message):
    now = datetime.now()
    uid, uname = message.from_user.id, message.from_user.username

    # CHECK SUB
    if not users_db[uid]["subject"]:
        await message.answer( f" {no_sub} ")
        return
    
    # CHECK HAS USER ENTRY
    if (users_db[uid]["subject"] == org_name and uid in org_list) or (users_db[uid]["subject"] == hist_name and uid in hist_list):
        await message.answer( f"⚠️ Ты ужe в очереди на предмет {users_db[uid]['subject']}!" )
        logging.info(f"@{uname}: {entries_limit_log}")
        return

    # CHECK IS PERMITTED JOINING(TIME OF REGISTRATION)
    if not is_kill_time_limit:
        if (users_db[uid]["subject"] == hist_name and not(now.weekday() == 2 and 9  <= now.hour <= 12)):
            await message.answer( f"{locked_auth}" ); logging.info( f"@{uname}: {time_limit_log}" ); return
        if (users_db[uid]["subject"] == org_name  and not(now.weekday() == 3 and 11 <= now.hour <= 18)):
            await message.answer( f"{locked_auth}" ); logging.info( f"@{uname}: {time_limit_log}" ); return
    
    # ADD
    if add_to_list(uid, uname, users_db[uid]["subject"]):
        logging.info(f"@{uname}: {adding_user_log} {users_db[uid]['subject']}")
        await message.answer(
            f"✅ @{uname} добавлен в очередь {users_db[uid]['subject']}!\n\n"
            f"{get_list_status()}"
        )
    else:
        logging.info(f"@{uname}: {adding_user_err_log} {users_db[uid]['subject']}")
        await message.answer("❌ Ошибка добавления :( ")

# DONE CMD
@dp.message(F.text == done_button_text)
async def cmd_done(message: Message):
    uid, uname = message.from_user.id, message.from_user.username

    if   users_db[uid]["subject"] == org_name:   delete(org_list, uid) ; logging.info( f"@{uname}: {del_user_from_queue_log}" )
    elif users_db[uid]["subject"] == hist_name:  delete(hist_list, uid); logging.info( f"@{uname}: {del_user_from_queue_log}" )
    else:                                        await message.answer(no_sub)

# ADMIN: LIMITS
@dp.message(Command("limits"))
async def cmd_limits(message: Message):
    global is_kill_time_limit
    if message.text[len("/limits"):].strip() == APIS.kill_limits_pass:
        is_kill_time_limit = not is_kill_time_limit
        await message.answer( f"Админ изменил параметр is_kill_time_limit: {is_kill_time_limit}" )
    else:
        await message.answer( f"Неверный пароль администратора" )

# SEND NOTIFICATION EVERY SATURDAY
async def send_notification():
    now = datetime.now()

    # HISTORY
    if now.weekday() == 2 and now.hour == 9:
        for uid in list(users_db):
            try:
                await bot.send_message( chat_id=uid, text=history_not )
                logging.info(f"@{users_db.get(uid, {}).get('username', 'Unknown')}: {sending_mes_log}")
            except Exception as e:
                logging.error(f"@{users_db.get(uid, {}).get('username', 'Unknown')}: {sending_mes_err_log} ({e})")
                if "blocked" in str(e).lower() or "not found" in str(e).lower(): # Delete non-active users 
                    users_db.discard(uid)

    # ORG
    if now.weekday() == 3 and now.hour == 11:
        for uid in list(users_db):
            try:
                await bot.send_message( chat_id=uid, text=org_not )
                logging.info(f"@{users_db.get(uid, {}).get('username', 'Unknown')}: {sending_mes_log}")
            except Exception as e:
                logging.error(f"@{users_db.get(uid, {}).get('username', 'Unknown')}: {sending_mes_err_log} ({e})")
                if "blocked" in str(e).lower() or "not found" in str(e).lower(): # Delete non-active users 
                    users_db.discard(uid)

# CHECK EVERY HOUR NOTIFICATION
async def notification_checker():
    while True:
        await send_notification()
        await asyncio.sleep(1800) # WAIT 1H

async def main():
    asyncio.create_task(notification_checker())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
