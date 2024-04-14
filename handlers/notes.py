import asyncio
from aiogram import Router,types
from aiogram.filters import StateFilter
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup,CallbackQuery
import FSM.classes
import keyboards
from database import db_notes
from database.database_func import Database

notes_router = Router(name='notes_router')

@notes_router.message(F.text == "Заметки 📒", ~StateFilter(FSM.classes.FSMuser_state.not_registered))
async def open_notes(message: types.Message, database: Database):
    no_notes_text = "<b>У тебя пока нет заметок.</b>\n Нажми <b>«Добавить»</b> для новой"
    notes_list = await db_notes.view_all_notes(message.from_user.id, database)
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
    
@notes_router.callback_query(F.data == 'go_back_notes',~StateFilter(FSM.classes.FSMuser_state.not_registered)) # Повтор пред.блока (При нажатии кнопки "Назад")
async def open_notes2(callback:CallbackQuery, database: Database):
    await callback.answer()
    no_notes_text = "<b>У тебя пока нет заметок.</b>\nНажми «Добавить» для новой"
    notes_list = await db_notes.view_all_notes(callback.from_user.id, database)
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
    
@notes_router.callback_query(F.data == 'add_note')
async def add_note(callback: CallbackQuery,state: FSMContext):
    await asyncio.sleep(0.3)
    await callback.answer()
    await callback.message.edit_text(text="Напиши текст заметки и отправь его.",reply_markup=InlineKeyboardMarkup(inline_keyboard=
        [[keyboards.inline.notes_back_button]]
    ))
    await state.set_state(FSM.classes.FSMnotes.adding_note)
    
@notes_router.message(F.text, StateFilter(FSM.classes.FSMnotes.adding_note))
async def write_new_note(message:types.Message,state: FSMContext, database: Database):
    await db_notes.write_note("'" + message.text + "'", message.from_user.id)
    all_notes = await db_notes.view_all_notes(message.from_user.id, database)
    await message.answer(text="<b>Заметка создана!</b>\nВсе заметки:\n\n" + 
                        all_notes[0],reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[keyboards.inline.notes_add_button],
                         [keyboards.inline.notes_delete_one_button],
                         [keyboards.inline.notes_exit_button]]
    ))
    await state.set_state(default_state)

@notes_router.message(StateFilter(FSM.classes.FSMnotes.adding_note))
async def wrong_input(message:types.Message):
    await message.answer(text="<b>Это не заметка.</b>\nНапиши ее текстом или нажми «Назад»",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_back_button]]))

@notes_router.callback_query(F.data == 'delete_note')
async def delete_note(callback:CallbackQuery,state:FSMContext, database: Database):
    all_notes = await db_notes.view_all_notes(callback.from_user.id, database)
    await callback.answer()
    await asyncio.sleep(0.3)
    await callback.message.edit_text(text="Напиши номер заметки для удаления\n" + all_notes[0],
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_back_button]]))
    await state.set_state(FSM.classes.FSMnotes.deleting_note)

@notes_router.message(StateFilter(FSM.classes.FSMnotes.deleting_note))
async def note_delete(message: types.Message,state: FSMContext, database: Database):
    if message.text and message.text.isnumeric():
        all_notes = await db_notes.view_all_notes(message.from_user.id, database)
        if int(message.text) > all_notes[1]:
            await message.answer(text="<b>Такой заметки не существует</b>\nПопробуй еще раз или нажми «Назад»",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keyboards.inline.notes_back_button]]))
        else:
            user_choice = int(message.text)
            await db_notes.delete_note(message.from_user.id,user_choice, database)
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
        
@notes_router.callback_query(F.data == 'notes_exit')
async def exit_notes(callback: CallbackQuery):
    try:
        await callback.answer()
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer(text="Старые диалоговые окна не получится закрыть...")