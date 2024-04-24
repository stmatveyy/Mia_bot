from . import inline, reply
from datetime import datetime as dt
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def time_keyboard() -> list[list[InlineKeyboardButton]]:

    is_evening:bool = dt.now().hour in [0] + [j for j in range(17, 23)]
    is_weekend:bool = dt.now().weekday() in [5,6]

    keys: list[list[InlineKeyboardButton]] = []

    if not is_evening:
        keys.append([inline.today_evening])

    keys.append([inline.tomorrow_morning])
    keys.append([inline.in_3_days])

    if not is_weekend:
        keys.append([inline.on_weekend])

    return keys
