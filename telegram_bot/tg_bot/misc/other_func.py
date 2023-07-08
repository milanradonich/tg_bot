import re
import datetime
from distutils import command
from json import JSONDecodeError

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import MediaGroup, ReplyKeyboardRemove
from aiogram_calendar import DialogCalendar
from loguru import logger
from tg_bot.keyboards.base_btn import need_photo_hotel
from hotels_requests import get_id_city, send_hotels_without_photo


async def json_decode_error(error_information: dict):
    message = error_information['message']
    state = error_information['state']
    current_command = error_information['current_command']
    logger.error("Ошибка JSONDecodeError")
    await message.answer(f'Не получилось найти данные по введенному городу, попробуйте снова.\n'
                         f'Для этого пропишите команду /{current_command}')
    await state.reset_state()


async def type_error(error_information: dict):
    message = error_information['message']
    state = error_information['state']
    current_command = error_information['current_command']
    logger.error("Ошибка TypeError")
    await message.answer(f'В ходе поиска возникла ошибка, попробуйте снова.\n'
                         f'Для этого пропишите команду /{current_command}')
    await state.reset_state()


async def check_special_symbols(symbol_information: dict):
    answer = symbol_information['answer']
    state = symbol_information['state']
    current_state = symbol_information['current_state']
    message = symbol_information['message']
    special_symbols = re.compile("|".join(map(re.escape, "@.,:;^№!?_*+()/#¤%&)"))).search
    if not bool(special_symbols(answer)):
        await state.update_data(city=answer)
        await message.answer("Пожалуйста выберите дату въезда",
                             reply_markup=await DialogCalendar().start_calendar())
        await current_state.arrival_date.set()
    else:
        await message.answer('Ошибка ввода! \nГород содержит спецсимволы, попробуйте снова')
        await current_state.city.set()


async def check_city(city_information: dict):           # проверяем введенный город
    message = city_information['message']
    state = city_information['state']
    current_state = city_information['current_state']
    answer = message.text
    if re.search(r'\d', answer) is None:
        symbol_information = {'message': message, 'state': state, 'current_state': current_state, 'answer': answer}
        await check_special_symbols(symbol_information=symbol_information)
    else:
        await message.answer('Ошибка ввода! \nГород содержит цифры, попробуйте снова')
        await current_state.city.set()


async def get_arrival_date(arrival_date_info: dict):        #
    callback_query = arrival_date_info['callback_query']
    callback_data = arrival_date_info['callback_data']
    state = arrival_date_info['state']
    current_state = arrival_date_info['current_state']
    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(f'Дата заезда {date.strftime("%d/%m/%Y")}')
        await state.update_data(arrival_date=datetime.datetime.strptime(date.strftime("%Y%m%d"), "%Y%m%d").date())
        await callback_query.message.answer('Выберите дату выезда',
                                            reply_markup=await DialogCalendar().start_calendar())
        await current_state.departure_date.set()


async def get_departure_date(departure_date_info: dict):
    callback_query = departure_date_info['callback_query']
    callback_data = departure_date_info['callback_data']
    state = departure_date_info['state']
    current_state = departure_date_info['current_state']
    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'Дата выезда {date.strftime("%d/%m/%Y")}'
        )
        await state.update_data(departure_date=datetime.datetime.strptime(date.strftime("%Y%m%d"), "%Y%m%d").date())

        await callback_query.message.answer('Сколько отелей показать? (максимальное количество: 15)')
        await current_state.quantity_hotels.set()


async def request_hotel_quantity(message: types.Message, state: FSMContext, current_state):
    answer = message.text
    if re.search(r'\D', answer):
        await message.answer('Ошибка ввода! \nМожно вводить только цифры, попробуйте снова')
        await current_state.quantity_hotels.set()
    elif 1 <= int(answer) <= 15:
        await state.update_data(quantity_hotels=answer)
        await message.answer('Показать фото отелей?', reply_markup=need_photo_hotel)
        await current_state.photo.set()
    else:
        await message.answer('Ошибка ввода! \nВведите от 1 до 15, попробуйте снова')
        await current_state.quantity_hotels.set()


async def send_info_without_photo(final_information: dict):
    state = final_information['state']
    message = final_information['message']
    find_hotel_func_name = final_information['find_hotel_func_name']
    data = await state.get_data()
    days_quantity = (data['departure_date'] - data['date_of_entry']).days
    city_id = await get_id_city(data)
    hotels_information = await find_hotel_func_name(data, city_id)

    for index in range(len(hotels_information)):
        await send_hotels_without_photo(hotels_information=hotels_information, index=index, command=command,
                                        days_quantity=days_quantity, message=message)

    await state.reset_state()
    await message.answer('Команда выполнена. Для просмотра всего функционала введите /help')


async def send_result_without_photo(search_information: dict):
    message = search_information['message']
    state = search_information['state']
    find_hotel_func_name = search_information['find_hotel_func_name']
    current_state = search_information['current_state']
    await message.answer('Хорошо, приступаю к поиску', reply_markup=ReplyKeyboardRemove())
    logger.info(f"Бот приступает к выполнению команды /{current_state}")
    try:
        final_information = {'state': state, 'message': message, 'final_hotel_func_name': find_hotel_func_name}
        await send_info_without_photo(final_information=final_information)
    except JSONDecodeError:
        error_information = {'message': message, 'state': state, 'current_command': 'bestdeal'}
        await json_decode_error(error_information=error_information)
    except TypeError:
        error_information = {'message': message, 'state': state, 'current_command': 'bestdeal'}
        await type_error(error_information=error_information)


async def send_info_with_photo(final_information: dict):
    state = final_information['state']
    message = final_information['message']
    find_hotel_func_name = final_information['find_hotel_func_name']
    data = await state.get_data()
    days_quantity = (data['departure_date'] - data['date_of_entry']).days
    city_id = await get_id_city(data)
    hotels_information = await find_hotel_func_name(data, city_id)

    for index in range(len(hotels_information)):
        await set_hotels_with_photos(MediaGroup=MediaGroup, command=command, data=data,
                                     days_quantity=days_quantity, hotels_information=hotels_information,
                                     index=index, message=message)

    await state.reset_state()
    await message.answer('Команда выполнена. Для просмотра всего функционала введите /help')


async def send_result_with_photo(search_information: dict):
    state = search_information['state']
    answer = search_information['answer']
    message = search_information['message']
    current_state = search_information['current_state']
    find_hotel_func_name = search_information['find_hotel_func_name']

    await state.update_data(photo_quantity=answer)
    await message.answer('Хорошо, приступаю к поиску')
    logger.info(f"Бот приступает к выполнению команды /{current_state}")
    try:
        final_information = {'state': state, 'message': message, 'find_hotel_func_name': find_hotel_func_name}
        await send_info_with_photo(final_information)
    except JSONDecodeError:
        error_information = {'message': message, 'state': state, 'current_command': 'highprice'}
        await json_decode_error(error_information=error_information)
    except TypeError:
        error_information = {'message': message, 'state': state, 'current_command': 'highprice'}
        await type_error(error_information=error_information)

