import os
from dotenv import load_dotenv
from aiogram import bot, Dispatcher, types, executor

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = bot.Bot(TOKEN)
dp = Dispatcher(bot=bot)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer('Салам Алейкум братья')

if __name__ == '__main__':
    executor.start_polling(dp)
