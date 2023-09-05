from aiogram.dispatcher.filters.state import StatesGroup, State


# класс состояний юзера, где мы опишем все states, чтобы потом переключаться между ними.
class LowPrice(StatesGroup):
    start = State()
    city = State()
    destinationId = State()
    date_of_entry = State()
    departure_date = State()
    quantity_hotels = State()
    photo = State()
    result_without_photo = State()
    quantity_photo = State()


class ClientStatesGroup(StatesGroup):
    photo = State()
    descr = State()


class ProfileStatesGroup(StatesGroup):
    photo = State()
    name = State()
    age = State()
    descr = State()
