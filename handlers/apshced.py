from aiogram import Bot,Router
from aiogram.types import Message
from datetime import datetime
import database.select_schedule

schedule_for_today = database.select_schedule.get_todays_schedule()

apsched_router = Router(name="apsched_router")
print(f"thats apsched. sched is {schedule_for_today}")
@apsched_router.message()
async def send_message_cron(bot:Bot,msg_id: int):
    await bot.send_message(chat_id=msg_id, text=schedule_for_today) ## расписание, ежедневно
@apsched_router.message()
async def send_message_time(bot:Bot,msg_id: int):

    await bot.send_message(chat_id=msg_id,text="Это сообщение отправится через секунды после старта бота")
@apsched_router.message()
async def send_message_interval(bot:Bot,msg_id: int):
    await bot.send_message(chat_id=msg_id, text="Частые уведы")