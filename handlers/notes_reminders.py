import asyncio
from aiogram import Router, types, Bot
from aiogram.filters import StateFilter
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from uuid import uuid4
import FSM.classes
import keyboards
from database import db_entityFunc
from database.database_func import Database
import keyboards.builder
import keyboards.inline
from misc import times as t
from database.jobstore import scheduler
from . import apshced
from database.jobstore import add_user_job
from datetime import datetime as dt
from datetime import time, timedelta
from aiogram.fsm.storage.redis import Redis

redis = Redis(host='localhost', port=6379)
notes_router = Router(name='notes_router')


@notes_router.message(F.text == "Блокнот 📜")
async def open_notes(message: types.Message, database: Database) -> None:

    '''Отправляет текст всех заметок. При отсутствии предлагает создать новую.'''
    no_notes_text = "<b>У тебя пока нет записей.</b>\n Нажми <b>«Добавить»</b> для новой"
    notes_reminders_list = await db_entityFunc.view_all_entities(telegram_id=message.from_user.id,
                                                       database=database)
    if notes_reminders_list[1] == 1:

        await message.answer(text=no_notes_text, reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[keyboards.inline.notes_add_button], [keyboards.inline.notes_exit_button]]
        ))
    else:
        await message.answer(text= notes_reminders_list[0],
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_add_button],
                                                                                [keyboards.inline.notes_delete_one_button],
                                                                                [keyboards.inline.notes_exit_button]]))

# Повтор пред.блока (При нажатии кнопки "Назад")
@notes_router.callback_query(F.data == 'go_back_notes')
async def open_notes_callback(callback: CallbackQuery,
                              database: Database) -> None:
    '''Отправляет текст всех заметок. Отвечает на callback'''
    await callback.answer()
    no_notes_text = "<b>У тебя пока нет записей.</b>\nНажми «Добавить» для новой"
    notes_list = await db_entityFunc.view_all_entities(telegram_id=callback.from_user.id,
                                                       database=database)

    if notes_list[1] == 1:

        await asyncio.sleep(0.3)
        await callback.message.edit_text(text=no_notes_text,
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_add_button],
                                                                                            [keyboards.inline.notes_exit_button]]))
    else:

        await asyncio.sleep(0.3)
        await callback.message.edit_text(text="<b>Твои заметки:</b>\n" + notes_list[0],
                             reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[[keyboards.inline.notes_add_button],
                                              [keyboards.inline.notes_delete_one_button],
                                              [keyboards.inline.notes_exit_button]]))


@notes_router.callback_query(F.data == 'add_note')
async def add_note(callback: CallbackQuery, state: FSMContext) -> None:
    '''Приглашает написать текст заметки.'''
    await asyncio.sleep(0.3)
    await callback.answer()
    await callback.message.edit_text(text="Напиши текст записи и отправь его.",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_back_button]]))
    await state.set_state(FSM.classes.FSMnotes.adding_note)


@notes_router.message(F.text, StateFilter(FSM.classes.FSMnotes.adding_note))
async def ask_for_time(message: types.Message,
                       state: FSMContext):
    '''Предлагает установить время и запоминает текст заметки / напоминания'''
    
    await message.answer(text='Добавь время, чтобы заметка стала напоминанием',
                            reply_markup=InlineKeyboardMarkup(
                                inline_keyboard=[[keyboards.inline.yes_remind_button],
                                                [keyboards.inline.no_remind_button]]))
    await state.update_data(msg_text=message.text)


@notes_router.callback_query(F.data == 'add_time' )
async def add_time(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    keys = await keyboards.builder.time_keyboard()
    await callback.message.edit_text('Когда напомнить? ', reply_markup=
                                     InlineKeyboardMarkup(inline_keyboard=keys))
    await state.set_state(FSM.classes.FSMnotes.adding_time)


@notes_router.callback_query(F.data.in_({'today_evn', 'tomorrow_mor', 'days_3', 'weekend'}))
async def time_chosen(callback: CallbackQuery, state: FSMContext, database:Database, bot: Bot):
    await callback.answer()
    
    all_data = await state.get_data()
    reminder_text = all_data['msg_text']

    match callback.data:
        case 'today_evn':
            timestamp = t.TODAY_EVN
        case 'tomorrow_mor':
            timestamp = t.TOMORROW_MOR
        case 'days_3':
            timestamp = t.DAYS_3
        case 'weekend':
            timestamp = t.WEEKENDS

    await db_entityFunc.write_entity(
                                    text="'" + reminder_text + "'",
                                    telegram_id=callback.from_user.id,
                                    database=database,
                                    type_='reminders',         
                                    timestamp=timestamp)

    notes_reminders_list = await db_entityFunc.view_all_entities(telegram_id=callback.from_user.id,
                                                       database=database)
    
    await callback.message.edit_text(text='Напоминание создано! \n' + notes_reminders_list[0], reply_markup=InlineKeyboardMarkup(
         inline_keyboard=[[keyboards.inline.notes_add_button],
                          [keyboards.inline.notes_delete_one_button],
                          [keyboards.inline.notes_exit_button]]))
    
    job_number = str(uuid4())
    job_id = f"user_{callback.from_user.id}_{job_number}"

    redis_job_id = add_user_job(job_function=apshced.custom_noti,
                      user_id=callback.from_user.id,
                      scheduler=scheduler,
                      trigger='date',
                      run_date=timestamp,
                      job_id=job_id,
                      
                      kwargs={'chat_id': callback.from_user.id, 'text': reminder_text, 'job_id':job_id})
    
    await db_entityFunc.write_job_id(database=database,
                                              telegram_id=callback.from_user.id,
                                              redis_job_id=redis_job_id)
    await state.set_state(None)


@notes_router.callback_query(F.data == 'no_time')
async def no_time(callback: CallbackQuery, state: FSMContext, database: Database):
    await callback.answer()
    data = await state.get_data()
    note_text = data['msg_text']
    await db_entityFunc.write_entity(text="'" + note_text + "'",
                                     telegram_id=callback.from_user.id,
                                     database=database,
                                     type_='notes')

    all_notes = await db_entityFunc.view_all_entities(telegram_id=callback.from_user.id,
                                                       database=database)
    
    await callback.message.edit_text(text='Заметка создана!\n' + all_notes[0], reply_markup=InlineKeyboardMarkup(
         inline_keyboard=[[keyboards.inline.notes_add_button],
                          [keyboards.inline.notes_delete_one_button],
                          [keyboards.inline.notes_exit_button]]))

    await state.set_state(None)


@notes_router.message(StateFilter(FSM.classes.FSMnotes.adding_note))
async def wrong_input(message: types.Message) -> None:
    '''Неверная заметка.'''
    await message.reply(text="<b>Это не заметка.</b>\nНапиши ее текстом или нажми «Назад»",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_back_button]]))


@notes_router.callback_query(F.data == 'delete_note')
async def delete_note(callback: CallbackQuery,
                      state: FSMContext,
                      database: Database) -> None:
    all_notes = await db_entityFunc.view_all_entities(callback.from_user.id, database)
    await callback.answer()
    await asyncio.sleep(0.3)
    await callback.message.edit_text(text="Напиши номер записи для удаления\n" + all_notes[0],
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_back_button]]))
    await state.set_state(FSM.classes.FSMnotes.deleting_note)


@notes_router.message(StateFilter(FSM.classes.FSMnotes.deleting_note))
async def note_delete(message: types.Message,
                      state: FSMContext,
                      database: Database) -> None:
    
    message_is_valid: bool = message.text and message.text.isnumeric()

    if message_is_valid:

        all_entities = await db_entityFunc.view_all_entities(message.from_user.id, database)

        if int(message.text) >= all_entities[1] or int(message.text) == 0:
            await message.answer(text="<b>Такой заметки не существует</b>\nПопробуй еще раз или нажми «Назад»",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_back_button]]))

        else:
            user_choice = int(message.text)
            # Решаем, удалять заметку или напоминание
            if user_choice <= all_entities[2]:
                redis_id = await db_entityFunc.delete_entity(telegram_id=message.from_user.id, 
                                                  index=user_choice, 
                                                  database=database, 
                                                  type_='reminders')
                scheduler.remove_job(job_id=redis_id)
            else:
                user_choice -= all_entities[2]
                await db_entityFunc.delete_entity(telegram_id=message.from_user.id, 
                                                  index=user_choice, 
                                                  database=database, 
                                                  type_='notes')

            all_notes_after_delete = await db_entityFunc.view_all_entities(message.from_user.id, database=database)

            if all_notes_after_delete[1] == 1:
                await asyncio.sleep(0.3)
                await message.answer(text="<b>Запись удалена, а других нет.</b>\nНажми «Добавить» для новой",
                                        reply_markup=InlineKeyboardMarkup(inline_keyboard=
                                                                          [[keyboards.inline.notes_add_button],
                                                                           [keyboards.inline.notes_exit_button]]))
            else:
                await asyncio.sleep(0.3)
                await message.answer(text="<b>Запись удалена!</b>\n" + all_notes_after_delete[0],
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                            [keyboards.inline.notes_add_button],
                                            [keyboards.inline.notes_delete_one_button],
                                            [keyboards.inline.notes_exit_button]]))
            await state.set_state(None)
    else:
        await message.reply(text="<b>Это не номер заметки.</b>\nПопробуй еще раз или нажми «Назад»",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_back_button]]))


@notes_router.callback_query(F.data == 'notes_exit')
async def exit_notes(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.answer()
        await callback.message.delete()
        await state.set_state(None)
    except TelegramBadRequest:
        await callback.answer(text="Старые диалоговые окна не получится закрыть...")
        await state.set_state(None)


@notes_router.callback_query(F.data == 'remind_again')
async def rem_again(callback: CallbackQuery):
    job_ = await redis.get(str(callback.from_user.id) + 'REM')
    job_id = job_.decode('utf-8')
    scheduler.reschedule_job(job_id=str(job_id), jobstore='redis', trigger='date', run_date=(dt.now() + timedelta(hours=1)))

    try:
        await callback.answer(text="Напоминание перенесено на час. ")
        await callback.message.delete()
    except TelegramBadRequest():
        await callback.answer(text="Старые диалоговые окна не получится закрыть... ")

    
@notes_router.callback_query(F.data == 'skip_remind')
async def no_remind(callback: CallbackQuery, state: FSMContext, database: Database):
    try:
        await callback.answer(text="Напоминание закрыто ")
        await callback.message.delete()
    except TelegramBadRequest():
        await callback.answer(text="Старые диалоговые окна не получится закрыть... ")