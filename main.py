import os
from dotenv import load_dotenv
import asyncio
import logging
import sys

from aiogram import Bot as bt
from aiogram import Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command,StateFilter
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.types.bot_command import BotCommand
from aiogram.types import ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup,CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram import F
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime,timedelta

from handlers.apshced import send_message_cron,send_message_interval,send_message_time,apsched_router
from filters.admin_filter import adm_list
from config_data.config import config


dp = Dispatcher()
bot = bt(config.tg_bot.token, parse_mode=ParseMode.HTML)
dp.include_router(apsched_router)
scheduler = AsyncIOScheduler()

main_r = Router() # ХУЙНЯ какая-то
dp.include_router(main_r)

class FSMnotifications(StatesGroup):
    turned_on = State()
    turned_off = State()

print('[INFO] Bot is working now...')


@dp.message(CommandStart())
async def cmd_start(message: types.Message):

    on_button = InlineKeyboardButton(text='Включить уведомления', callback_data='button_is_on')
    off_button = InlineKeyboardButton(text='Выключить уведомления', callback_data='button_is_off')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[on_button],[off_button]])
    await message.answer(f'Привет, {message.from_user.first_name}!',reply_markup=keyboard)


@dp.message(lambda message: message.from_user.id in adm_list and message.text == 'adm')
async def admin_check(message: types.Message):
    await message.reply("Ты админ!")

@dp.callback_query(StateFilter(default_state),F.data == 'button_is_on')
async def start_notifications(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text='Напоминалки ща будут')

    chat_id = callback.from_user.id
    scheduler.add_job(send_message_time, trigger='date',run_date = datetime.now() + timedelta(seconds=10),
                  kwargs={'bot':bot,'msg_id': chat_id})
    scheduler.add_job(send_message_cron, trigger='cron', hour = datetime.now().hour, 
                    minute = datetime.now().minute + 1, start_date = datetime.now(), kwargs={'bot':bot,'msg_id' : chat_id})
    scheduler.add_job(send_message_interval, trigger='interval', seconds = 5, kwargs={'bot':bot,'msg_id':chat_id})
    scheduler.start()
    scheduler.print_jobs()
    await state.set_state(FSMnotifications.turned_on)

@dp.callback_query(StateFilter(FSMnotifications.turned_on),F.data == 'button_is_off')
async def pause_notifications(callback:CallbackQuery, state: FSMContext):
    scheduler.pause()
    await callback.answer(text='Напоминания приостановлены... ')
    await state.set_state(FSMnotifications.turned_off)

@dp.callback_query(StateFilter(FSMnotifications.turned_off), F.data == 'button_is_on')
async def resume_notification(callback: CallbackQuery, state: FSMContext):
    scheduler.resume()
    await callback.answer('Напоминания возобновлены! ')
    await state.set_state(FSMnotifications.turned_on)


@dp.message()
async def wrong_cmd(message: types.Message):
    await message.reply('Я пока не знаю такой команды :( ')


async def main():
    await dp.start_polling(bot)

try:
    if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
except KeyboardInterrupt:
    scheduler.shutdown()

    pass