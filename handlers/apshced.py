from aiogram import Bot,Router
from aiogram.types import Message
from datetime import datetime

apsched_router = Router(name="apsched_router")

@apsched_router.message()
async def send_message_cron(bot:Bot,msg_id: int):
    await bot.send_message(chat_id=msg_id, text=f"Сюда будет отправляться расписание каждый день")
@apsched_router.message()
async def send_message_time(bot:Bot,msg_id: int):

    await bot.send_message(chat_id=msg_id,text="Это сообщение отправится через секунды после старта бота")
@apsched_router.message()
async def send_message_interval(bot:Bot,msg_id: int):
    await bot.send_message(chat_id=msg_id, text=f"Текущее время: {datetime.now()}")