from aiogram.dispatcher.filters.state import StatesGroup, State


class Report(StatesGroup):
    bet = State()
    result = State()
    bookmaker = State()
    ok = State()


class Panel(StatesGroup):
    users = State()
    user_main = State()
