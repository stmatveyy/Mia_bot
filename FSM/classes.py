from aiogram.fsm.state import State, StatesGroup

class FSMgpt_states(StatesGroup):
    gpt_mode_on = State()


class FSMnotes(StatesGroup):
    adding_note = State()
    deleting_note = State()
    adding_time = State()

