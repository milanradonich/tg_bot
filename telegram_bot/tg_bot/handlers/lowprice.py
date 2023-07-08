from aiogram import types
from main import dp
from aiogram.dispatcher.filters import Command
from tg_bot.state import LowPrice
from aiogram.dispatcher.storage import FSMContext    #Finite State Machine
from tg_bot.misc.other_func import check_city, get_arrival_date, get_departure_date, request_hotel_quantity,\
    send_result_with_photo, send_result_without_photo, send_info_without_photo, send_info_with_photo
from hotels_requests import get_hotel_info_lowprice
from aiogram_calendar import dialog_cal_callback
from aiogram.types import ReplyKeyboardRemove, CallbackQuery


@dp.message_handler(commands=['lowprice'])    # хэндлер обрабатывает команду lowprice
async def search_city(message: types.Message):  # фун-ия поиск города
    user_name = message.from_user.full_name
    await message.reply(f'Привет, {user_name} ! Введите город:')
    await LowPrice.city.set()               # обращаемся к классу LowPrice, далее к состоянию city, а методом set() мы устанавливаем данное состояние.


@dp.message_handler(state=LowPrice.city)
async def arrival_date(message: types.Message, state: FSMContext):   #фун-ия дата заезда # FSMContext для того, чтобы мы могли записывать данные пользователя в память
    answer = message.text
    city_information = {'answer': answer, 'state': state, 'message': message, 'current_state': LowPrice}
    await check_city(city_information=city_information)


@dp.callback_query_handler(dialog_cal_callback.filter(), state=LowPrice.arrival_date)
async def arrival_date_check(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):  # фун-ия проверки даты заезда
    arrival_date_info = {'callback_query': callback_query, 'callback_data': callback_data, 'state': state,
                         "current_state": LowPrice}
    await get_arrival_date(arrival_date_info=arrival_date_info)


@dp.callback_query_handler(dialog_cal_callback.filter(), state=LowPrice.departure_date)
async def departure_date(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):   # фун-ия даты выезда
    departure_date_info = {'callback_query': callback_query, 'callback_data': callback_data, 'state': state,
                           'current_state': LowPrice}
    await get_departure_date(departure_date_info=departure_date_info)


@dp.message_handler(state=LowPrice.quantity_hotels)
async def if_need_photo(message: types.Message, state: FSMContext):  # спрашиваем нужно ли фото?
    await request_hotel_quantity(message=message, state=state, current_state=LowPrice)


@dp.message_handler(state=LowPrice.photo)
async def result(message: types.Message, state: FSMContext):     # нет - выводим в результат инфо по отелям без фото пользователю
    answer = message.text                                        # да - спрашиваем сколько фото
    if 'Нет' in answer:
        search_information = {'message': message, 'state': state, 'find_hotel_func_name': get_hotel_info_lowprice,
                              'current_state': 'lowprice'}
        await send_result_without_photo(search_information=search_information)
    elif 'Да' in answer:
        await state.update_data(photo_need=answer)
        await message.answer('Сколько фото отелей показать?', reply_markup=ReplyKeyboardRemove())
        await LowPrice.quantity_photo.set()
    else:
        await message.answer('Ошибка ввода! \nВведите "Да" или "Нет"')
        await LowPrice.photo.set()


@dp.message_handler(state=LowPrice.quantity_photo)
async def result(message: types.Message, state: FSMContext):    # выводится инфо с фото в результат пользователю
    answer = message.text
    if answer.isdigit() is False:
        await message.answer('Ошибка ввода! \nВведите число')
        await LowPrice.quantity_photo.set()
    elif answer == '0':
        await message.answer('Число должно быть больше нуля, попробуйте снова')
        await LowPrice.quantity_photo.set()
    else:
        search_information = {'state': state, 'message': message, 'answer': answer, 'current_state': 'lowprice',
                              'find_hotel_func_name': get_hotel_info_lowprice}
        await send_result_with_photo(search_information)


