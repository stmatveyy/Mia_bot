from aiogram import Router,types,Bot
from aiogram.filters import CommandStart
from aiogram import F
from database import user_register
import keyboards
from database.database_func import Database

start_router = Router(name='start_router')

@start_router.message(CommandStart())
async def cmd_start(message: types.Message, database: Database, approved:bool | None) -> tuple[str,bool]:
    if not await user_register.check_if_registered(id_=message.from_user.id, database=database):
        await message.answer("Давай знакомиться! Отправь мне свои контакты, чтобы продолжить.",
                             reply_markup=keyboards.reply.num_keyboard)
        return ('approved', approved)
    
    else:
        approved = True
        await message.answer(f'Привет, {message.from_user.first_name}!', reply_markup=keyboards.reply.home_keyboard)
        return ('approved', approved)

@start_router.message(F.content_type == types.ContentType.CONTACT)
async def num_sent(message: types.Message, bot:Bot, database:Database) -> tuple[str,bool]:
    contact = message.contact
    if not await user_register.check_user_data(num=contact.phone_number,message=message, database=database):
        approved = False
        await message.answer(text="Ты не студент учебной группы. Если это ошибка, или ты хочешь подключить свою группу, пиши ему: ")
        await bot.send_contact(chat_id=message.chat.id, phone_number= '+79057984548', first_name='Матвей', last_name='Столяров')
        return ('approved', approved)
    else:
        approved = True
        await message.answer(f'Добро пожаловать, {message.from_user.first_name}!', reply_markup=keyboards.reply.home_keyboard)
    
    return ('approved', approved)

@start_router.message(F.text == 'Не хочу отправлять')
async def number_refuse(message: types.Message) -> tuple[str,bool]:
    approved: bool = False
    await message.answer(text="<b>Без номера телефона не получится воспользоваться ботом :(</b>",reply_markup=keyboards.reply.num_keyboard2)
    return ('approved', approved)