# filter.py yozib olamiz
from aiogram.filters import Filter
from config import Chanel_id
from aiogram import Bot
from aiogram.types import Message, CallbackQuery



class  CheksupChanel(Filter):
    async def __call__(self, message: Message, bot: Bot):
        user_status = await bot.get_chat_member(Chanel_id, message.from_user.id)
        if user_status.status in ['creator', 'administrator', "member"]:
             return False
        return True

class  CheksupChanel1(Filter):
    async def __call__(self, cal:CallbackQuery, bot: Bot):
        user_status = await bot.get_chat_member(Chanel_id, cal.from_user.id)
        if user_status.status in ['creator', 'administrator', "member"]:
             return False
        return True


async def check_subscription(user_id, bot: Bot):
    member = await bot.get_chat_member(chat_id=Chanel_id, user_id=user_id)
    return member.status in ['member', 'administrator', 'creator']