from aiogram import Bot as bt
from aiogram.enums import ParseMode
from config_data.config import config

bot = bt(config.tg_bot.token, parse_mode=ParseMode.HTML)