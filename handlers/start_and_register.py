from aiogram import Router,types,Bot
from aiogram.filters import CommandStart
from aiogram import F
from aiogram.fsm.context import FSMContext
import FSM.classes
from database import user_register
import keyboards

start_router = Router(name='start_router')

@start_router.message(CommandStart())
async def cmd_start(message: types.Message):
    if not await user_register.check_if_registered(id_=message.from_user.id):
        await message.answer("Давай знакомиться! Отправь мне свои контакты, чтобы продолжить.",
                             reply_markup=keyboards.reply.num_keyboard)
    else:
        await message.answer(f'Привет, {message.from_user.first_name}!', reply_markup=keyboards.reply.home_keyboard)

@start_router.message(F.content_type == types.ContentType.CONTACT)
async def num_sent(message: types.Message, bot:Bot):
    contact = message.contact
    if not await user_register.check_user_data(num=contact.phone_number,message=message):
        await message.answer(text="Ты не студент учебной группы. Если это ошибка, или ты хочешь подключить свою группу, пиши ему: ")
        await bot.send_contact(chat_id=message.chat.id, phone_number= '+79057984548', first_name='Матвей', last_name='Столяров')
    else:
        await message.answer(f'Добро пожаловать, {message.from_user.first_name}!', reply_markup=keyboards.reply.home_keyboard)

@start_router.message(F.text == 'Не хочу отправлять')
async def number_refuse(message: types.Message,state: FSMContext):
    await message.answer(text="<b>Без номера телефона не получится воспользоваться ботом :(</b>",reply_markup=keyboards.reply.num_keyboard2)
    await state.set_state(FSM.classes.FSMuser_state.not_registered)