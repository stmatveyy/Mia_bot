from aiogram.types import InlineKeyboardButton

# Клавиатура для тоггла расписания

noti_on_button = InlineKeyboardButton(text='Уведомления: 🔕',
                                      callback_data='noti_button_is_on')
noti_off_button = InlineKeyboardButton(text='Уведомления: 🔔',
                                       callback_data='noti_button_is_off')

settings_exit_button = InlineKeyboardButton(text='Закрыть',
                                            callback_data='settings_exit')


# Клавиатура для заметок

notes_add_button = InlineKeyboardButton(text="Добавить",
                                        callback_data='add_note')

notes_delete_one_button = InlineKeyboardButton(text="Стереть",
                                               callback_data='delete_note')

notes_exit_button = InlineKeyboardButton(text='Закрыть',
                                         callback_data='notes_exit')

notes_back_button = InlineKeyboardButton(text="Назад",
                                         callback_data='go_back_notes')

# Клавиатура для напоминаний

yes_remind_button = InlineKeyboardButton(text='Добавить',
                                         callback_data='add_time')

no_remind_button = InlineKeyboardButton(text='Пропустить',
                                        callback_data='no_time')

remind_again_button = InlineKeyboardButton(text='Напомнить через час',
                                           callback_data='remind_again')

skip_remind_button = InlineKeyboardButton(text='Закрыть',
                                          callback_data='skip_remind')


# Клавиатура для выбора времени напоминания

today_evening = InlineKeyboardButton(text='Сегодня вечером',
                                     callback_data='today_evn')

tomorrow_morning = InlineKeyboardButton(text='Завтра утром',
                                        callback_data='tomorrow_mor')

in_3_days = InlineKeyboardButton(text='Через три дня',
                                 callback_data='days_3')

on_weekend = InlineKeyboardButton(text='На выходных',
                                  callback_data='weekend')
