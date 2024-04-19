from aiogram.fsm.state import State, StatesGroup


class FSMcustom_notifications(StatesGroup):
    fill_notification = State()
    fill_exec_time = State()


class FSMgpt_states(StatesGroup):
    gpt_mode_on = State()


class FSMnotes(StatesGroup):
    adding_note = State()
    deleting_note = State()
