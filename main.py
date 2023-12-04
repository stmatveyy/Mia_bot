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
from aiogram.exceptions import TelegramBadRequest
from handlers.apshced import send_message_cron, send_message_interval
from handlers.apshced import send_message_time, apsched_router

from filters.admin_filter import adm_list
from config_data.config import config
import keyboards.inline
import keyboards.reply
from gpt.answer_gen import ask_gpt
from database import user_register, db_notes

dp = Dispatcher()
bot = bt(config.tg_bot.token, parse_mode=ParseMode.HTML)
dp.include_router(apsched_router)
scheduler = AsyncIOScheduler()

main_r = Router()  # ХУЙНЯ какая-то
dp.include_router(main_r)


class FSMnotifications(StatesGroup):
    turned_on = State()
    turned_off = State()

class FSMcustom_notifications(StatesGroup):
    fill_notification = State()
    fill_exec_time = State()

class FSMgpt_states(StatesGroup):
    gpt_mode_on = State()

class FSMuser_state(StatesGroup):
    not_registered = State()

class FSMnotes(StatesGroup):
    adding_note = State()
    deleting_note = State()

print('[INFO] Bot is working now...')


@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    if not await user_register.check_if_registered(id_=message.from_user.id):
        await message.answer("Давай знакомиться! Отправь мне свои контакты, чтобы продолжить.",
                             reply_markup=keyboards.reply.num_keyboard)
    else:
        await message.answer(f'Привет, {message.from_user.first_name}!', reply_markup=keyboards.reply.home_keyboard)

@dp.message(F.content_type == types.ContentType.CONTACT)
async def num_sent(message: types.Message):
    contact = message.contact
    if not await user_register.check_user_data(num=contact.phone_number,message=message):
        await message.answer(text="Ты не студент учебной группы. Если это ошибка, или ты хочешь подключить свою группу, пиши ему: ")
        await bot.send_contact(chat_id=message.chat.id, phone_number= '+79057984548', first_name='Матвей', last_name='Столяров')
    else:
        await message.answer(f'Добро пожаловать, {message.from_user.first_name}!', reply_markup=keyboards.reply.home_keyboard)

@dp.message(F.text == 'Не хочу отправлять')
async def number_refuse(message: types.Message,state: FSMContext):
    await message.answer(text="<b>Без номера телефона не получится воспользоваться ботом :(</b>",reply_markup=keyboards.reply.num_keyboard2)
    await state.set_state(FSMuser_state.not_registered)

@dp.message(Command(commands='settings'), ~StateFilter(FSMuser_state.not_registered))
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


@dp.message(F.text == "GPT 📡", ~StateFilter(FSMuser_state.not_registered))
async def gpt_turn_on(message: types.Message, state: FSMContext):
    await message.answer(text="Я GPT. Спроси меня о чем-угодно!",
                         reply_markup=keyboards.reply.gpt_keyboard)
    await state.set_state(FSMgpt_states.gpt_mode_on)


@dp.message(F.text == "Выключить GPT", ~StateFilter(FSMuser_state.not_registered))
async def gpt_turn_off(message: types.Message, state: FSMContext):
    await message.answer(text="Было приятно пообщаться!",
                        reply_markup=keyboards.reply.home_keyboard)
    await state.set_state(default_state)

@dp.message(F.text == "Заметки 📒", ~StateFilter(FSMuser_state.not_registered))
async def open_notes(message: types.Message):
    no_notes_text = "<b>У тебя пока нет заметок.</b>\n Нажми <b>«Добавить»</b> для новой"
    notes_list = await db_notes.view_all_notes(message.from_user.id)
    if notes_list == 0:
        await message.answer(text=no_notes_text,reply_markup= InlineKeyboardMarkup(
            inline_keyboard=[[keyboards.inline.notes_add_button],[keyboards.inline.notes_exit_button]]
        ))
    else:
        await message.answer(text="<b>Твои заметки:</b>\n" + notes_list[0],
                         reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[[keyboards.inline.notes_add_button],
                                              [keyboards.inline.notes_delete_one_button],
                                              [keyboards.inline.notes_exit_button]]))
    
@dp.callback_query(F.data == 'go_back_notes',~StateFilter(FSMuser_state.not_registered)) # Повтор пред.блока (При нажатии кнопки "Назад")
async def open_notes2(callback:CallbackQuery):
    await callback.answer()
    no_notes_text = "<b>У тебя пока нет заметок.</b>\nНажми «Добавить» для новой"
    notes_list = await db_notes.view_all_notes(callback.from_user.id)
    if notes_list == 0:
        await asyncio.sleep(0.3)
        await callback.message.edit_text(text=no_notes_text,reply_markup= InlineKeyboardMarkup(
            inline_keyboard=[[keyboards.inline.notes_add_button],[keyboards.inline.notes_exit_button]]
        ))
    else:
        await asyncio.sleep(0.3)
        await callback.message.edit_text(text="<b>Твои заметки:</b>\n" + notes_list[0],
                         reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[[keyboards.inline.notes_add_button],
                                              [keyboards.inline.notes_delete_one_button],
                                              [keyboards.inline.notes_exit_button]]))
    
@dp.callback_query(F.data == 'add_note')
async def add_note(callback: CallbackQuery,state: FSMContext):
    await asyncio.sleep(0.3)
    await callback.answer()
    await callback.message.edit_text(text="Напиши текст заметки и отправь его.",reply_markup=InlineKeyboardMarkup(inline_keyboard=
        [[keyboards.inline.notes_back_button]]
    ))
    await state.set_state(FSMnotes.adding_note)

@dp.message(F.text, StateFilter(FSMnotes.adding_note))
async def write_new_note(message:types.Message,state: FSMContext):
    await db_notes.write_note("'" + message.text + "'", message.from_user.id)
    all_notes = await db_notes.view_all_notes(message.from_user.id)
    await message.answer(text="<b>Заметка создана!</b>\nВсе заметки:\n\n" + 
                        all_notes[0],reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[keyboards.inline.notes_add_button],
                         [keyboards.inline.notes_delete_one_button],
                         [keyboards.inline.notes_exit_button]]
    ))
    await state.set_state(default_state)

@dp.message(StateFilter(FSMnotes.adding_note))
async def wrong_input(message:types.Message):
    await message.answer(text="<b>Это не заметка.</b>\nНапиши ее текстом или нажми «Назад»",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_back_button]]))

@dp.callback_query(F.data == 'delete_note')
async def delete_note(callback:CallbackQuery,state:FSMContext):
    all_notes = await db_notes.view_all_notes(callback.from_user.id)
    await callback.answer()
    await asyncio.sleep(0.3)
    await callback.message.edit_text(text="Напиши номер заметки для удаления\n" + all_notes[0],
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_back_button]]))
    await state.set_state(FSMnotes.deleting_note)

@dp.message(StateFilter(FSMnotes.deleting_note))
async def note_delete(message: types.Message,state: FSMContext):
    if message.text and message.text.isnumeric():
        all_notes = await db_notes.view_all_notes(message.from_user.id)
        if int(message.text) > all_notes[1]:
            await message.answer(text="<b>Такой заметки не существует</b>\nПопробуй еще раз или нажми «Назад»",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_back_button]]))
        else:
            user_choice = int(message.text)
            await db_notes.delete_note(message.from_user.id,user_choice)
            all_notes_after_delete = await db_notes.view_all_notes(message.from_user.id)
            if all_notes_after_delete == 0:
                await asyncio.sleep(0.3)
                await message.answer(text="<b>Заметка удалена, а других нет.</b>\nНажми «Добавить» для новой",
                                        reply_markup=InlineKeyboardMarkup(inline_keyboard=
                                                                          [[keyboards.inline.notes_add_button],
                                                                           [keyboards.inline.notes_exit_button]]))
            else:
                await asyncio.sleep(0.3)
                await message.answer(text="<b>Заметка удалена!</b>\nВсе заметки:\n\n" + all_notes_after_delete[0],
                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                            [keyboards.inline.notes_add_button],
                                            [keyboards.inline.notes_delete_one_button],
                                            [keyboards.inline.notes_exit_button]]))
            await state.set_state(default_state)
    else:
        await message.answer(text="<b>Это не номер заметки.</b>\nПопробуй еще раз или нажми «Назад»",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_back_button]]))
        
@dp.callback_query(F.data == 'notes_exit')
async def exit_notes(callback: CallbackQuery):
    try:
        await callback.answer()
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer(text="Старые диалоговые окна не получится закрыть...")

@dp.message(StateFilter(FSMgpt_states.gpt_mode_on), ~StateFilter(FSMuser_state.not_registered))
async def gpt_talk(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id,
                               action=ChatAction.TYPING)
    gpt_answer = await ask_gpt(message.text)
    await message.answer(text=gpt_answer)

@dp.callback_query(StateFilter(default_state), F.data == 'noti_button_is_on', ~StateFilter(FSMuser_state.not_registered))
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
    await asyncio.sleep(0.3)
    await callback.message.edit_text(text="⚙️Настройки⚙️",
                                     reply_markup=InlineKeyboardMarkup(
                                                        inline_keyboard=[
                                                            [keyboards.inline.noti_off_button],
                                                            [keyboards.inline.settings_exit_button]]
                                                            ))

    await state.set_state(FSMnotifications.turned_on)


@dp.callback_query(StateFilter(FSMnotifications.turned_on), F.data == 'noti_button_is_off', ~StateFilter(FSMuser_state.not_registered))
async def pause_notifications(callback: CallbackQuery, state: FSMContext):
    scheduler.pause()
    await callback.answer(text='Напоминания приостановлены... ')
    await state.set_state(FSMnotifications.turned_off)
    await asyncio.sleep(0.3)
    await callback.message.edit_text(text="⚙️Настройки⚙️",
                                     reply_markup=InlineKeyboardMarkup(
                                         inline_keyboard=[[keyboards.inline.noti_on_button],
                                                          [keyboards.inline.settings_exit_button]]))


@dp.callback_query(StateFilter(FSMnotifications.turned_off), F.data == 'noti_button_is_on', ~StateFilter(FSMuser_state.not_registered))
async def resume_notification(callback: CallbackQuery, state: FSMContext):
    scheduler.resume()
    await callback.answer('Напоминания возобновлены! ')
    await state.set_state(FSMnotifications.turned_on)
    await asyncio.sleep(0.3)
    await callback.message.edit_text(text="⚙️Настройки⚙️",
                                     reply_markup=InlineKeyboardMarkup(
                                                    inline_keyboard=[[keyboards.inline.noti_off_button],
                                                                     [keyboards.inline.settings_exit_button]]))


@dp.callback_query(F.data == 'settings_exit', ~StateFilter(FSMuser_state.not_registered))
async def exit_settings(callback: CallbackQuery):
    try:
        await callback.answer()
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer(text='Старые диалоговые окна не получится закрыть...')

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


#TODO: state изменяется на дефолтный при заходе в режим GPT, нужно хранить стейты в стеке.