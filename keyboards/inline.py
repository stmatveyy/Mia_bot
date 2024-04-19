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

notes_delete_one_button = InlineKeyboardButton(text="Стереть заметку",
                                               callback_data='delete_note')

notes_exit_button = InlineKeyboardButton(text='Закрыть',
                                         callback_data='notes_exit')

notes_back_button = InlineKeyboardButton(text="Назад", callback_data='go_back_notes')
