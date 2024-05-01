import asyncio
from aiogram import Bot, Router
from aiogram import F
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.storage.redis import Redis
from aiogram.exceptions import TelegramBadRequest

from datetime import datetime
from database.select_schedule import get_todays_schedule
from database.jobstore import scheduler
from database.db_entityFunc import view_all_job_ids

import keyboards
from bot_init import bot
from keyboards.inline import remind_again_button, skip_remind_button

redis = Redis(host='localhost', port=6379)


async def schedule(database):
    return await get_todays_schedule(database)

apsched_router = Router(name="apsched_router")


async def async_message(chat_id: int, text):
    await bot.send_message(chat_id=chat_id, text=text)


async def custom_noti(chat_id: int, text, job_id: str) -> None:

    await redis.set(str(chat_id) + 'REM', job_id)
    await bot.send_message(chat_id=chat_id, text="<b>Новое напоминание:</b>\n" + "<i>" + text + "</i>", 
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[[remind_again_button], [skip_remind_button]]))


@apsched_router.callback_query(F.data == 'noti_button_is_on')
async def notifications(callback: CallbackQuery, bot: Bot, database) -> None:

    if scheduler.state == 0:
        try:
            await callback.answer(text='Напоминалки ща будут')
        except TelegramBadRequest:
            pass

        schedule_ = await schedule(database=database)
        chat_id = callback.from_user.id

        scheduler.add_job(async_message,
                        trigger='cron',
                        hour=datetime.now().hour,
                        minute=datetime.now().minute + 1,
                        start_date=datetime.now(),
                        jobstore='redis',
                        replace_existing=True,
                        kwargs={'chat_id': chat_id, 'text': schedule_})

        jobs_dict = await view_all_job_ids(database=database, telegram_id=callback.from_user.id)

        for job_id, date_time in jobs_dict.items():
            if job_id and date_time:
                scheduler.reschedule_job(job_id=job_id, jobstore='redis', trigger='cron', hours='*', start_date=date_time)
            else:
                continue

        scheduler.start()
        await asyncio.sleep(0.3)

        await callback.message.edit_text(text="⚙️Настройки⚙️",
                                        reply_markup=InlineKeyboardMarkup(
                                                            inline_keyboard=[
                                                                [keyboards.inline.noti_off_button],
                                                                [keyboards.inline.settings_exit_button]]
                                                                ))

    elif scheduler.state == 2:
        scheduler.resume()

        try:
            await callback.answer('Напоминания включены! ')
        except TelegramBadRequest:
            pass

        await asyncio.sleep(0.3)
        await callback.message.edit_text(text="⚙️Настройки⚙️",
                                        reply_markup=InlineKeyboardMarkup(
                                                        inline_keyboard=[[keyboards.inline.noti_off_button],
                                                                        [keyboards.inline.settings_exit_button]]))


@apsched_router.callback_query(F.data == 'noti_button_is_off')
async def pause_notifications(callback: CallbackQuery) -> None:
    if scheduler.state == 1:
        scheduler.pause()
        try:
            await callback.answer(text='Напоминания приостановлены... ')

        except TelegramBadRequest:
            pass

        await asyncio.sleep(0.3)
        await callback.message.edit_text(text="⚙️Настройки⚙️",
                                        reply_markup=InlineKeyboardMarkup(
                                            inline_keyboard=[[keyboards.inline.noti_on_button],
                                                            [keyboards.inline.settings_exit_button]]))
    else:
        raise RuntimeError("Scheduler is not stopped.")