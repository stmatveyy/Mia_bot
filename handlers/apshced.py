from aiogram import Bot, Router
from aiogram import F
from aiogram.types import InlineKeyboardMarkup, CallbackQuery

from datetime import datetime, timedelta

import database.select_schedule
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import keyboards


async def schedule():
    return await database.select_schedule.get_todays_schedule()

# schedule_for_today = asyncio.run(schedule()) ## НЕ ТЕСТИРОВАЛОСЬ.

scheduler = AsyncIOScheduler()
apsched_router = Router(name="apsched_router")


async def send_message_cron(bot: Bot, msg_id: int) -> None:
    '''Отправляет сообщение с расписанием.'''
    await bot.send_message(chat_id=msg_id, text=await schedule())


async def send_message_time(bot: Bot, msg_id: int) -> None:
    '''Отправляет сообщение с любым текстом.'''
    await bot.send_message(chat_id=msg_id,
                           text="Это сообщение отправится через секунды после старта бота")


async def send_message_interval(bot: Bot, msg_id: int) -> None:
    '''Отправляет сообщение для частых уведомлений.'''
    await bot.send_message(chat_id=msg_id, text="Частые уведы")


async def shut_down() -> None:
    scheduler.shutdown()

@apsched_router.callback_query(lambda settings: settings.notification == False and settings.first_time == True,
                    F.data == 'noti_button_is_on')
async def start_notifications(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer(text='Напоминалки ща будут')

    chat_id = callback.from_user.id
    scheduler.add_job(send_message_time,
                      trigger='date',
                      run_date=datetime.now() + timedelta(seconds=10),
                      kwargs={'bot': bot, 'msg_id': chat_id})

    scheduler.add_job(send_message_cron,
                      trigger='cron',
                      hour=datetime.now().hour,
                      minute=datetime.now().minute + 1,
                      start_date=datetime.now(),
                      kwargs={'bot': bot, 'msg_id': chat_id})

    scheduler.add_job(send_message_interval,
                      trigger='interval',
                      seconds=5,
                      kwargs={'bot': bot, 'msg_id': chat_id})

    scheduler.start()
    await asyncio.sleep(0.3)
    await callback.message.edit_text(text="⚙️Настройки⚙️",
                                     reply_markup=InlineKeyboardMarkup(
                                                        inline_keyboard=[
                                                            [keyboards.inline.noti_off_button],
                                                            [keyboards.inline.settings_exit_button]]
                                                            ))

    # settings.notification = True
    # settings.first_time = False


@apsched_router.callback_query(lambda settings: settings.notification == True,
                   F.data == 'noti_button_is_off')
async def pause_notifications(callback: CallbackQuery) -> None:
    scheduler.pause()
    await callback.answer(text='Напоминания приостановлены... ')
    await asyncio.sleep(0.3)
    await callback.message.edit_text(text="⚙️Настройки⚙️",
                                     reply_markup=InlineKeyboardMarkup(
                                         inline_keyboard=[[keyboards.inline.noti_on_button],
                                                          [keyboards.inline.settings_exit_button]]))

    # settings.notification = False
    # settings.first_time = False

@apsched_router.callback_query(lambda settings: settings.notification == False and settings.first_time == False, F.data == 'noti_button_is_on')
async def resume_notification(callback: CallbackQuery) -> None:
    scheduler.resume()
    await callback.answer('Напоминания включены! ')
    await asyncio.sleep(0.3)
    await callback.message.edit_text(text="⚙️Настройки⚙️",
                                     reply_markup=InlineKeyboardMarkup(
                                                    inline_keyboard=[[keyboards.inline.noti_off_button],
                                                                     [keyboards.inline.settings_exit_button]]))
    #settings.notification = True
    # settings.first_time = False

#TODO: Сделать MagicData и вернуться сюда