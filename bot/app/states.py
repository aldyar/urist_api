from aiogram.fsm.state import StatesGroup, State


class Documents(StatesGroup):
    wait_docx = State()
    wait_pdf = State()
    delete_doc = State()

class Chat(StatesGroup):
    chat = State()

class Setting(StatesGroup):
    role = State()
    prompt = State()
    model = State()