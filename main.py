import asyncio
import logging
import sys
import asyncpg

from aiogram import Bot as bt
from aiogram import Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, Redis
from handlers.start_and_register import start_router
from handlers.settings_menu import settings_router
from handlers.admin import admin_router
from handlers.GPT import gpt_router
from handlers.notes import notes_router
from handlers.apshced import apsched_router,shut_down
from handlers.wrong_cmd import wrong_cmd_router

from config_data.config import config
from database.database_func import Database

from middlewares.database import CommonMiddleWare

HOST = config.db.host
USER = config.db.user
PASSWORD = config.db.password
DB_NAME = config.db.db_name

redis = Redis(host='localhost')
storage = RedisStorage(redis=redis)
dp = Dispatcher(storage=storage)
bot = bt(config.tg_bot.token, parse_mode=ParseMode.HTML)
database = Database()
loop = asyncio.get_event_loop()
dp.update.outer_middleware(CommonMiddleWare(database=database))

dp.include_router(apsched_router)
dp.include_router(start_router)
dp.include_router(settings_router)
dp.include_router(admin_router)
dp.include_router(gpt_router)
dp.include_router(notes_router)
dp.include_router(wrong_cmd_router)

class Settings():
    def __init__(self,notification:bool,first_time:bool) -> None:
        self.notification = notification
        self.first_time = first_time

settings = Settings(False,True)

async def main(database:Database):
    
    await database._ainit_()
    await dp.start_polling(bot)

try:
    if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        loop.run_until_complete(main(database))

except KeyboardInterrupt:
    loop.run_until_complete(database.close())
    
    #asyncio.create_task(shut_down())
    print("[INFO] Бот выключен.")
    loop.close()
    


#TODO: state изменяется на дефолтный при заходе в режим GPT, изучить MagicData + написать Middleware
# Ссыль: https://mastergroosha.github.io/aiogram-3-guide/filters-and-middlewares/

#TODO: сделать lexicon.py со всеми текстами для работы бота. Можно потом перевести все на английский.