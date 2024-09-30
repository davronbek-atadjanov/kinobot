from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import Chanel_id
from aiogram import Bot

KANALLAR = InlineKeyboardMarkup(
    inline_keyboard= [
        [InlineKeyboardButton(text='1-kanal', url='https://t.me/davronbekatadjanov')],

        [InlineKeyboardButton(text='✅Tasdiqlash', callback_data='tasdiqlash')],
    ],  
    resize_keyboard=True
)

