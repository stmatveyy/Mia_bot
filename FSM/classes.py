from aiogram.fsm.state import State, StatesGroup


class FSMnotifications(StatesGroup):
    turned_on = State()
    turned_off = State()


class FSMcustom_notifications(StatesGroup):
    fill_notification = State()
    fill_exec_time = State()


class FSMgpt_states(StatesGroup):
    gpt_mode_on = State()


class FSMuser_state(StatesGroup):
    not_registered = State()


class FSMnotes(StatesGroup):
    adding_note = State()
    deleting_note = State()
