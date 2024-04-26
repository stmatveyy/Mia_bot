import asyncio
import logging
import sys
import atexit

from aiogram import Bot as bt
from aiogram import Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, Redis

from handlers.start_and_register import start_router
from handlers.settings_menu import settings_router
from handlers.admin import admin_router
from handlers.GPT import gpt_router
from handlers.notes_reminders import notes_router
from handlers.apshced import apsched_router
from handlers.wrong_cmd import wrong_cmd_router

from config_data.config import config
from database.database_func import Database
from middlewares.database import CommonMiddleWare

redis = Redis(host='localhost', port=6379)
database = Database()
storage = RedisStorage(redis=redis)
dp = Dispatcher(storage=storage)
bot = bt(config.tg_bot.token, parse_mode=ParseMode.HTML)
loop = asyncio.get_event_loop()

dp.message.outer_middleware(CommonMiddleWare(database=database, redis=redis))
dp.edited_message.outer_middleware(CommonMiddleWare(database=database, redis=redis))
dp.message_reaction.outer_middleware(CommonMiddleWare(database=database, redis=redis))
dp.callback_query.outer_middleware(CommonMiddleWare(database=database, redis=redis))

dp.include_router(apsched_router)
dp.include_router(start_router)
dp.include_router(settings_router)
dp.include_router(admin_router)
dp.include_router(gpt_router)
dp.include_router(notes_router)
dp.include_router(wrong_cmd_router)

@atexit.register
def a_exit() -> None:
    loop.run_until_complete(database.close())
    loop.close()
    print("[INFO] Бот выключен.")
   

async def main(database: Database):
    await database._ainit_()
    await dp.start_polling(bot)

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    loop.run_until_complete(main(database))
