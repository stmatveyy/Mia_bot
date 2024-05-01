from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Основная клавиатура
gpt_mode_button = KeyboardButton(text="GPT 📡")
homework_button = KeyboardButton(text="Домашка 📚")
noti_notes_button = KeyboardButton(text="Блокнот 📜")

home_keyboard = ReplyKeyboardMarkup(keyboard=[
    [gpt_mode_button, homework_button, noti_notes_button]],
    resize_keyboard=True)

# GPT клавиатура
gpt_off_button = KeyboardButton(text="Выключить GPT")
gpt_keyboard = ReplyKeyboardMarkup(keyboard=[[gpt_off_button]],
                                   resize_keyboard=True)

# Клава для контактов
send_num_button = KeyboardButton(text="📱 Отправить", request_contact=True)

num_keyboard = ReplyKeyboardMarkup(keyboard=[[send_num_button]],
                                   resize_keyboard=True)
