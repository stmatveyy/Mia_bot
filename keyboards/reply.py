from aiogram.types import ReplyKeyboardMarkup,KeyboardButton

# Основная клавиатура
gpt_mode_button = KeyboardButton(text="GPT 📡")
homework_button = KeyboardButton(text="Домашка 📚")
custom_notifications_button = KeyboardButton(text="Планы 📈")
more_button = KeyboardButton(text="+Еще")

home_keyboard = ReplyKeyboardMarkup(keyboard=[
    [gpt_mode_button,homework_button,custom_notifications_button],[more_button]],resize_keyboard=True)

## GPT клавиатура
gpt_off_button = KeyboardButton(text="Выключить GPT")
gpt_keyboard = ReplyKeyboardMarkup(keyboard=[[gpt_off_button]],resize_keyboard=True)

## Клава для контактов
send_num_button = KeyboardButton(text="📱 Отправить",request_contact=True)
not_send_num_button =KeyboardButton(text="Не хочу отправлять")
num_keyboard = ReplyKeyboardMarkup(keyboard=[[send_num_button],[not_send_num_button]],resize_keyboard=True)
num_keyboard2 = ReplyKeyboardMarkup(keyboard=[[send_num_button]],resize_keyboard=True)