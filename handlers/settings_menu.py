from aiogram import Router,types
from aiogram.filters import Command, StateFilter
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup,CallbackQuery
import FSM.classes
import keyboards

settings_router = Router(name='settings_router')


@settings_router.message(Command(commands='settings'), ~StateFilter(FSM.classes.FSMuser_state.not_registered))
async def open_settings(message: types.Message, state: FSMContext):
    notifications_are_on = settings.notification
    if notifications_are_on:
        await message.answer(text="<b>⚙️ Настройки</b>",
                             reply_markup=InlineKeyboardMarkup(
                                    inline_keyboard=[[keyboards.inline.noti_off_button],
                                                     [keyboards.inline.settings_exit_button]]))
    else:
        await message.answer(text="<i>⚙️ Настройки</i>", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[keyboards.inline.noti_on_button], [keyboards.inline.settings_exit_button]]))


@settings_router.callback_query(F.data == 'settings_exit', ~StateFilter(FSM.classes.FSMuser_state.not_registered))
async def exit_settings(callback: CallbackQuery):
    try:
        await callback.answer()
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer(text='Старые диалоговые окна не получится закрыть...')

# TODO: Middleware и MAGICDATA, после этого переделать код тут