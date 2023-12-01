from aiogram import Bot,Router
from aiogram.types import Message
from datetime import datetime
import database.select_schedule
import asyncio
async def schedule():
    return await database.select_schedule.get_todays_schedule()

schedule_for_today = asyncio.run(schedule())

apsched_router = Router(name="apsched_router")
@apsched_router.message()
async def send_message_cron(bot:Bot,msg_id: int):
    await bot.send_message(chat_id=msg_id, text=schedule_for_today) ## расписание, ежедневно
@apsched_router.message()
async def send_message_time(bot:Bot,msg_id: int):

    await bot.send_message(chat_id=msg_id,text="Это сообщение отправится через секунды после старта бота")
@apsched_router.message()
async def send_message_interval(bot:Bot,msg_id: int):
    await bot.send_message(chat_id=msg_id, text="Частые уведы")