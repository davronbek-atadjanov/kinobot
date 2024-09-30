from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

KINO = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text='Kino qo\'shish'),
            KeyboardButton(text='Kino o\'chirish')
        ]
    ],
    resize_keyboard=True
)

