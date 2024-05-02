from aiogram import Router, types
from aiogram.filters import Command
from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
import keyboards
from . import apshced

settings_router = Router(name='settings_router')


@settings_router.message(Command(commands='settings'))
async def open_settings(message: types.Message) -> None:

    if apshced.scheduler.state == 1:
        await message.answer(text="<b>⚙️ Настройки</b>",
                             reply_markup=InlineKeyboardMarkup(
                                    inline_keyboard=[[keyboards.inline.noti_off_button],
                                                     [keyboards.inline.settings_exit_button]]))
    else:
        await message.answer(text="<b>⚙️ Настройки</b>", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[keyboards.inline.noti_on_button], [keyboards.inline.settings_exit_button]]))


@settings_router.callback_query(F.data == 'settings_exit')
async def exit_settings(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.answer()
        await callback.message.delete()
        await state.set_state(None)

    except TelegramBadRequest:
        await callback.message.answer(text='Старые диалоговые окна не получится закрыть...')
