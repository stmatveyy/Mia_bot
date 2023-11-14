import os
from dotenv import load_dotenv
import asyncio
import logging
import sys

from aiogram import Bot as bt
from aiogram import Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.types.bot_command import BotCommand
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram import F
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from aiogram.enums.chat_action import ChatAction

from handlers.apshced import send_message_cron, send_message_interval
from handlers.apshced import send_message_time, apsched_router

from filters.admin_filter import adm_list
from config_data.config import config
import keyboards.inline
import keyboards.reply
from gpt.answer_gen import ask_gpt


dp = Dispatcher()
bot = bt(config.tg_bot.token, parse_mode=ParseMode.HTML)
dp.include_router(apsched_router)
scheduler = AsyncIOScheduler()

main_r = Router()  # ХУЙНЯ какая-то
dp.include_router(main_r)


class FSMnotifications(StatesGroup):
    turned_on = State()
    turned_off = State()
    default_for_noti = State()


class FSMcustom_notifications(StatesGroup):
    fill_notification = State()
    fill_exec_time = State()
    default_for_custom_noti = State()


class FSMgpt_states(StatesGroup):
    gpt_mode_on = State()
    default_for_gpt = State()


print('[INFO] Bot is working now...')


@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):

    await message.answer(f'Привет, {message.from_user.first_name}!', reply_markup=keyboards.reply.home_keyboard)


@dp.message(Command(commands='settings'))
async def open_settings(message: types.Message, state: FSMContext):
    curr_state = await state.get_state()
    if curr_state == FSMnotifications.turned_on:
        await message.answer(text="<b>⚙️ Настройки</b>",
                             reply_markup=InlineKeyboardMarkup(
                                    inline_keyboard=[[keyboards.inline.noti_off_button],
                                                     [keyboards.inline.settings_exit_button]]))
    else:
        await message.answer(text="<i>⚙️ Настройки</i>", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[keyboards.inline.noti_on_button], [keyboards.inline.settings_exit_button]]))


@dp.message(lambda message: message.from_user.id in adm_list and message.text == 'adm')
async def admin_check(message: types.Message):
    await message.reply("Ты админ!")


@dp.message(lambda message: message.text == "GPT 📡")
async def gpt_turn_on(message: types.Message, state: FSMContext):
    await message.answer(text="Привет! Я GPT. Спроси меня что-нибудь!",
                         reply_markup=keyboards.reply.gpt_keyboard)
    await state.set_state(FSMgpt_states.gpt_mode_on)


@dp.message(lambda message: message.text == "Выключить GPT")
async def gpt_turn_off(message: types.Message, state: FSMContext):
    await message.answer(text="Было приятно пообщаться!",
                        reply_markup=keyboards.reply.home_keyboard)
    await state.set_state(default_state)


@dp.message(StateFilter(FSMgpt_states.gpt_mode_on))
async def gpt_talk(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id,
                               action=ChatAction.TYPING)
    gpt_answer = await ask_gpt(message.text)
    await message.answer(text=gpt_answer)


@dp.callback_query(StateFilter(default_state), F.data == 'noti_button_is_on')
async def start_notifications(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text='Напоминалки ща будут')

    chat_id = callback.from_user.id
    scheduler.add_job(send_message_time,
                      trigger='date',
                      run_date=datetime.now() + timedelta(seconds=10),
                      kwargs={'bot': bot, 'msg_id': chat_id})

    scheduler.add_job(send_message_cron,
                      trigger='cron',
                      hour=datetime.now().hour,
                      minute=datetime.now().minute + 1,
                      start_date=datetime.now(),
                      kwargs={'bot': bot, 'msg_id': chat_id})

    scheduler.add_job(send_message_interval,
                      trigger='interval',
                      seconds=5,
                      kwargs={'bot': bot, 'msg_id': chat_id})

    scheduler.start()

    await callback.message.edit_text(text="⚙️Настройки⚙️",
                                     reply_markup=InlineKeyboardMarkup(
                                                        inline_keyboard=[
                                                            [keyboards.inline.noti_off_button],
                                                            [keyboards.inline.settings_exit_button]]
                                                            ))

    await state.set_state(FSMnotifications.turned_on)


@dp.callback_query(StateFilter(FSMnotifications.turned_on), F.data == 'noti_button_is_off')
async def pause_notifications(callback: CallbackQuery, state: FSMContext):
    scheduler.pause()
    await callback.answer(text='Напоминания приостановлены... ')
    await state.set_state(FSMnotifications.turned_off)
    await callback.message.edit_text(text="⚙️Настройки⚙️",
                                     reply_markup=InlineKeyboardMarkup(
                                         inline_keyboard=[[keyboards.inline.noti_on_button],
                                                          [keyboards.inline.settings_exit_button]]))


@dp.callback_query(StateFilter(FSMnotifications.turned_off), F.data == 'noti_button_is_on')
async def resume_notification(callback: CallbackQuery, state: FSMContext):
    scheduler.resume()
    await callback.answer('Напоминания возобновлены! ')
    await state.set_state(FSMnotifications.turned_on)

    await callback.message.edit_text(text="⚙️Настройки⚙️",
                                     reply_markup=InlineKeyboardMarkup(
                                                    inline_keyboard=[[keyboards.inline.noti_off_button],
                                                                     [keyboards.inline.settings_exit_button]]))


@dp.callback_query(F.data == 'settings_exit')
async def exit_settings(callback: CallbackQuery):
    await callback.message.delete()


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
