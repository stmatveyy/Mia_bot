from aiogram import Router, types
from filters.admin_filter import adm_list

admin_router = Router(name='admin_router')


@admin_router.message(lambda message: message.from_user.id in adm_list
                      and message.text == 'adm')
async def admin_check(message: types.Message) -> None:
    await message.reply("Ты админ!")
