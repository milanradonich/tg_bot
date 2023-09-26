from aiogram.types import Message
from typing import Dict
import json
import asyncio
import tg_bot.database.add_to_db

import hotels_requests


async def print_data_without_photo(message: Message, data: Dict):
    tg_bot.database.add_to_db.add_query(data)
    text_message = ('Данные вашего запроса: \n'
                    f'Название города: {data["city"]}\n'
                    f'ID города: {data["destinationId"]}\n'
                    f'Дата заезда: {data["date_of_entry"]}\n'
                    f'Дата выезда: {data["departure_date"]}\n'
                    f'Кол-во отелей для выбора: {data["quantity_hotels"]}\n'
                    f'Нужны ли фото? {data["need_photo"]}\n'
                    )

    await message.answer(text_message)
    await message.answer(await hotels_requests.get_info_hotels(message, data))


async def print_data_with_photo(message: Message, data: Dict):
    tg_bot.database.add_to_db.add_query(data)
    text_message = ('Данные вашего запроса: \n'
                    f'Название города: {data["city"]}\n'
                    f'ID города: {data["destinationId"]}\n'
                    f'Дата заезда: {data["date_of_entry"]}\n'
                    f'Дата выезда: {data["departure_date"]}\n'
                    f'Кол-во отелей для выбора: {data["quantity_hotels"]}\n'
                    f'Нужны ли фото? {data["need_photo"]}\n'
                    f'Кол-во фото: {data["quantity_photo"]}'
                    )

    await message.answer(text_message)
    await message.answer(await hotels_requests.get_info_hotels(message, data))


def get_hotels(response_text: str, command: str, landmark_in: str, landmark_out: str):
    data = json.loads(response_text)
    if not data:
        raise LookupError('Запрос пуст...')
    if 'errors' in data.keys():
        return {'error': data['errors'][0]['message']}

    hotels_data = {}
    for hotel in data['data']['propertySearch']['properties']:
        try:
            hotels_data[hotel['id']] = {
                'name': hotel['name'], 'id': hotel['id'],
                'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
                'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
                'price': hotel['price']['lead']['amount']
            }
        except (KeyError, TypeError):
            continue
    if command == '/highprice':
        hotels_data = {
            key: value for key, value in
            sorted(hotels_data.items(), key=lambda hotel_id: hotel_id[1]['price'], reverse=True)
        }
    # Обнуляем созданный ранее словарь и добавляем туда только те отели, которые соответствуют диапазону.
    elif command == '/bestdeal':
        hotels_data = {}
        for hotel in data['data']['propertySearch']["properties"]:
            if float(landmark_in) < hotel['destinationInfo']['distanceFromDestination']['value'] < float(landmark_out):
                hotels_data[hotel['id']] = {
                    'name': hotel['name'], 'id': hotel['id'],
                    'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
                    'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
                    'price': hotel['price']['lead']['amount']}
    return hotels_data


def hotel_info(hotels_request: str):
    data = json.loads(hotels_request)
    if not data:
        raise LookupError('Запрос пуст...')
    hotel_data = {
        'id': data['data']['propertyInfo']['summary']['id'], 'name': data['data']['propertyInfo']['summary']['name'],
        'address': data['data']['propertyInfo']['summary']['location']['address']['addressLine'],
        'coordinates': data['data']['propertyInfo']['summary']['location']['coordinates'],
        'images': [
            url['image']['url'] for url in data['data']['propertyInfo']['propertyGallery']['images']

        ]
    }

    return hotel_data

