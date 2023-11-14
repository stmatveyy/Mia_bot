from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Клавиатура для тоггла расписания

noti_on_button = InlineKeyboardButton(text='Уведомления: 🔕',
                                      callback_data='noti_button_is_on')
noti_off_button = InlineKeyboardButton(text='Уведомления: 🔔',
                                       callback_data='noti_button_is_off')

settings_exit_button = InlineKeyboardButton(text='Закрыть',
                                            callback_data='settings_exit')
