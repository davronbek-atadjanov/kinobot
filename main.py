import asyncio
import logging
import sys
import sqlite3
from aiogram.types import Message, ContentType
from aiogram.types import  CallbackQuery
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from config import TOKEN, Chanel_id
from states.statets import next_step
from buttons.reply import KINO
from buttons.chanel import KANALLAR
from da_base.sql import read_db, add_movie, delete_movie
from filters import CheksupChanel, CheksupChanel1
from aiogram import Dispatcher, Bot, F, types

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def check_subscription(user_id):
    member = await bot.get_chat_member(chat_id=Chanel_id, user_id=user_id)
    return member.status in ['member', 'administrator', 'creator']


@dp.message(CheksupChanel())
async def check_handler(message: Message):
    user_id = message.from_user.id
    if await check_subscription(user_id):
        await message.reply(f"Salom! Botdan foydalanishingiz mumkin:\nKino kodini kiriting!")
    else:
        await message.reply("❌ Kechirasiz botimizdan foydalanishdan oldin ushbu kanallarga a'zo bo'lishingiz kerak.", reply_markup=KANALLAR)

@dp.callback_query(CheksupChanel1())
async def check_handler(cal: CallbackQuery):
    user_id = cal.from_user.id
    if await check_subscription(user_id):
        await cal.message.reply(f"Salom! Botdan foydalanishingiz mumkin:\nKino kodini kiriting!")
    else:
        await cal.message.reply("❌ Kechirasiz botimizdan foydalanishdan oldin ushbu kanallarga a'zo bo'lishingiz kerak.", reply_markup=KANALLAR)




def add_user_to_db(user_id):
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
        cur.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
        con.commit()

def get_all_user_ids():
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        cur.execute('SELECT user_id FROM users')
        user_ids = [row[0] for row in cur.fetchall()]
    return user_ids

def get_user_count():
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM users')
        user_count = cur.fetchone()[0]
    return user_count

async def send_advertisement(message_text: str, media_type: str = None, media_id: str = None):
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        try:
            if media_type == 'photo':
                await bot.send_photo(chat_id=user_id, photo=media_id, caption=message_text)
            elif media_type == 'video':
                await bot.send_video(chat_id=user_id, video=media_id, caption=message_text)
            else:
                await bot.send_message(chat_id=user_id, text=message_text)
        except Exception as e:
            logging.error(f"User {user_id} uchun reklama yuborishda xatolik: {e}")

@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    add_user_to_db(user_id)
    first_name = message.from_user.first_name
    await message.answer(f"Assalomu aleykum {first_name}!  Botdan foydalanishingiz mumkin.")

# Avvalgi "confirm_subscription" funksiyasini o'chiramiz
@dp.callback_query(lambda callback_query: callback_query.data == "tasdiqlash")
async def confirm_subscription(callback_query: types.CallbackQuery, message: Message):
    user_id = callback_query.from_user.id
    first_name = message.from_user.first_name
    await bot.send_message(user_id, f"Assalomu aleykum {first_name}!  Botdan foydalanishingiz mumkin.")
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)



@dp.message(Command('send_ad'))
async def send_advertisement_command(message: Message, state: FSMContext):
    if message.from_user.id == 1064391346:  # Admin ID
        await message.answer('Iltimos, reklama turini tanlang: text, photo, yoki video.')
        await state.set_state(next_step.waiting_for_ad_type)
    else:
        await message.answer("Sizda ushbu komandani bajarish huquqi yo'q.")

@dp.message(Command(commands=['user_count']))
async def user_count_command(message: Message):
    if message.from_user.id == 1064391346:  # Admin ID
        user_count = get_user_count()
        await message.answer(f"Botdagi foydalanuvchilar soni: {user_count}")
    else:
        await message.answer("Sizda ushbu komandani bajarish huquqi yo'q.")


@dp.message(next_step.waiting_for_ad_type)
async def select_ad_type(message: Message, state: FSMContext):
    ad_type = message.text
    if ad_type is None:
        await message.answer("Iltimos, reklama turi matnini kiriting.")
        return

    ad_type = ad_type.lower()
    if ad_type not in ['text', 'photo', 'video']:
        await message.answer("Noto'g'ri reklama turi. Iltimos, 'text', 'photo', yoki 'video' tanlang.")
        return

    await state.update_data({'ad_type': ad_type})

    if ad_type == 'text':
        await message.answer("Iltimos, reklama matnini kiriting:")
        await state.set_state(next_step.waiting_for_ad_text)
    elif ad_type == 'photo':
        await message.answer("Iltimos, reklama rasmni yuboring:")
        await state.set_state(next_step.waiting_for_photo)
    elif ad_type == 'video':
        await message.answer("Iltimos, reklama video yuboring:")
        await state.set_state(next_step.waiting_for_video)

@dp.message(next_step.waiting_for_text)
async def process_ad_text(message: Message, state: FSMContext):
    ad_text = message.text
    await send_advertisement(ad_text)
    await message.answer("Reklama yuborildi!")
    await state.clear()

@dp.message(next_step.waiting_for_photo)
async def process_ad_photo(message: Message, state: FSMContext):
    ad_data = await state.get_data()
    ad_text = ad_data.get('ad_text')
    photo_id = message.photo[-1].file_id  # last photo size
    await send_advertisement(ad_text, media_type='photo', media_id=photo_id)
    await message.answer("Reklama rasm yuborildi!")
    await state.clear()

@dp.message(next_step.waiting_for_video)
async def process_ad_video(message: Message, state: FSMContext):
    ad_data = await state.get_data()
    ad_text = ad_data.get('ad_text')
    video_id = message.video.file_id
    await send_advertisement(ad_text, media_type='video', media_id=video_id)
    await message.answer("Reklama video yuborildi!")
    await state.clear()

@dp.message(Command('admin'), F.from_user.id == 1064391346)
async def admin_cmd(message: Message, state: FSMContext):
    await message.answer('Glad to see you, Boss😎', reply_markup=KINO)
    await state.set_state(next_step.admin)

@dp.message(next_step.admin, F.text == 'Kino qo\'shish')
async def add_movie_handler(message: Message, state: FSMContext):
    await message.answer('Kino kodini kiriting')
    await state.set_state(next_step.kino_id)

@dp.message(F.text, next_step.kino_id)
async def get_kino_id(message: Message, state: FSMContext):
    kod = int(message.text)
    await state.update_data({'kod': kod})
    await message.answer('Kino nomini kiriting')
    await state.set_state(next_step.name)

@dp.message(F.text, next_step.name)
async def get_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data({'name': name})
    await message.answer('Kino haqida: ')
    await state.set_state(next_step.des)

@dp.message(F.text, next_step.des)
async def get_description(message: Message, state: FSMContext):
    des = message.text
    await state.update_data({'des': des})
    await message.answer('Kino urlini kiriting')
    await state.set_state(next_step.url)

@dp.message(F.text, next_step.url)
async def get_url(message: Message, state: FSMContext):
    data = await state.get_data()
    id = data.get('kod')
    name = data.get('name')
    des = data.get('des')
    url = message.text
    add_movie(id, name, des, url)
    await message.answer('db_base saved🤗')
    await state.clear()

@dp.message(next_step.admin, F.text == 'Kino o\'chirish')
async def delete_handler(message: Message, state: FSMContext):
    await message.answer('O\'chirmoqchi bo\'lgan kino kodini kiriting:')
    await state.set_state(next_step.delete_kino)

@dp.message(F.text, next_step.delete_kino)
async def delete_movie_by_id(message: Message, state: FSMContext):
    kod = message.text
    if kod.isdigit():
        delete_movie(int(kod))
        await message.answer(f"Kino kodi {kod} bo'lgan kino o'chirildi.")
        await state.clear()
    else:
        await message.answer("Kechirasiz, kino kodini son shaklida kiriting.")

@dp.message(F.text)
async def kodkino(message: Message):
    user_id = message.from_user.id
    kod = message.text
    if kod.isdigit():
        if await check_subscription(user_id):
            for i in read_db():
                if i[0] == int(kod):
                    await message.answer_video(video=f"{i[3]}", caption=f"Kino kodi: #{i[0]}\n{i[1]}\n\n{i[2]}")
                    print(i[3])
                    break
            else:
                await message.answer("Bu kodda kino mavjud emas😌")
        else:
            await message.answer("Botdan foydalanish uchun avval kanallarga obuna bo'lishingiz kerak.")
    else:
        await message.answer("Kechirasiz, kodni faqat son shaklida kiriting.")



async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
