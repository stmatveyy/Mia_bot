from aiogram import Router, types, Bot
from aiogram.filters import StateFilter
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.enums.chat_action import ChatAction
import FSM.classes
import keyboards.reply
import keyboards.inline

from gpt.answer_gen import ask_gpt

gpt_router = Router(name='gpt_router')


@gpt_router.message(F.text == "GPT 📡")
async def gpt_turn_on(message: types.Message, state: FSMContext):
    await message.answer(text="Я GPT. Спроси меня о чем-угодно!",
                         reply_markup=keyboards.reply.gpt_keyboard)
    await state.set_state(FSM.classes.FSMgpt_states.gpt_mode_on)


@gpt_router.message(F.text == "Выключить GPT")
async def gpt_turn_off(message: types.Message, state: FSMContext):
    await message.answer(text="Было приятно пообщаться!",
                         reply_markup=keyboards.reply.home_keyboard)
    await state.set_state(None)


@gpt_router.message(StateFilter(FSM.classes.FSMgpt_states.gpt_mode_on))
async def gpt_talk(message: types.Message, bot: Bot):
    await bot.send_chat_action(chat_id=message.chat.id,
                               action=ChatAction.TYPING)
    gpt_answer = await ask_gpt(message.text)
    await message.answer(text=gpt_answer)
