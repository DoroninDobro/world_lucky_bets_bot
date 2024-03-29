from aiogram.dispatcher.filters.state import StatesGroup, State


class Report(StatesGroup):
    bet = State()
    result = State()
    bookmaker = State()
    ok = State()


class Panel(StatesGroup):
    users = State()
    user_main = State()
    change_salary = State()
    change_salary_value = State()
    remove_user = State()


class AddTransaction(StatesGroup):
    sign = State()
    currency = State()
    amount = State()
    comment = State()
