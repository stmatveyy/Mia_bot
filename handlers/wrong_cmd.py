from aiogram import types,Router

wrong_cmd_router = Router(name='wrong_cmd_router')

@wrong_cmd_router.message()
async def wrong_cmd(message: types.Message):
    await message.reply('Я пока не знаю такой команды :( ')