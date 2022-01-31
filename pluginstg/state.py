from aiogram.dispatcher.filters.state import State, StatesGroup

class Dnevnik(StatesGroup):
    rasp = State()
    home_work = State()

class Start(StatesGroup):
    menu = State()
    new_account = State()
    schools = State()

class Other(StatesGroup):
    action = State()
    get_subject = State()
    get_mark = State()