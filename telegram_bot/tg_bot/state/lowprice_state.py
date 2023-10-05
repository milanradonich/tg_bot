from aiogram.dispatcher.filters.state import StatesGroup, State


# класс состояний юзера, где мы опишем все states, чтобы потом переключаться между ними.
class LowPrice(StatesGroup):
    start = State()
    city = State()
    destinationId = State()
    date_of_entry = State()
    departure_date = State()
    minPrice = State()
    maxPrice = State()
    landmark_in = State()
    landmark_out = State()
    quantity_hotels = State()
    need_photo = State()
    quantity_photo = State()


# class ClientStatesGroup(StatesGroup):
#     photo = State()
#     descr = State()
#
#
# class ProfileStatesGroup(StatesGroup):
#     photo = State()
#     name = State()
#     age = State()
#     descr = State()
