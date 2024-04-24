from database.jobstore import scheduler, add_user_job
from aiogram import Bot, Router
from aiogram import F, types
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from redis import Redis

from datetime import datetime, timedelta
import database.select_schedule
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import keyboards

custom_noti_router = Router(name='custom_noti_router')

@custom_noti_router.message(F.text == 'Напоминания 🕓')
async def noti(message: types.Message, bot: Bot):
    await message.answer(text=f'Все напоминания: {}')