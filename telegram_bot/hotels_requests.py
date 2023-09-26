import requests
import json
import re
import config
import random
# """
# sdcsdcsdcsdc
# """

from aiogram.types import Message, InputMediaPhoto
from typing import Dict
from main import bot
from tg_bot.database import add_response
from tg_bot.misc.other_func import get_hotels, hotel_info

my_url = "https://hotels4.p.rapidapi.com/locations/v2/search"

headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


# def request(method: str, url: str, querystring: dict) -> requests.Response:
#     """
#     Посылаем запрос к серверу
#     : param method : str
#     : param url : str
#     : param query_string : dict
#     : return : request.Response
#     """
#     if method == "GET":
#         response_get = requests.request("GET", url, params=querystring, headers=headers)
#         return response_get
#     elif method == "POST":
#         response_post = requests.request("POST", url, json=querystring, headers=headers)
#         return response_post


def destination_id(city):
    pattern = '<[^<]+?>'
    querystring = {"query": city, "locale": "en_US", "currency": "USD"}
    response = requests.get(my_url, headers=headers, params=querystring)
    data = json.loads(response.text)  # десериализация JSON
    # with open('descr_city.json', 'a') as city_file:
    # 	json.dump(data, city_file, indent=4)   # сериализация JSON

    possible_city = {}
    info_list = data.get("suggestions")

    for item in info_list:
        for key, value in item.items():
            if key == 'group' and value == 'CITY_GROUP':
                hotels = item.get('entities')
                for hotel in hotels:
                    if hotel.get('type') == 'CITY':
                        city_id = hotel.get('destinationId')
                        city_name = re.sub(pattern, '', hotel.get('caption'))
                        possible_city[city_id] = city_name
    return possible_city


async def get_info_hotels(message: Message, data: Dict):
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": data['destinationId']},
        "checkInDate": str(data['date_of_entry'])
            # 'day': int(data['date_of_entry']['day']),
            # 'month': int(data['date_of_entry']['month']),
            # 'year': int(data['date_of_entry']['year'])
        ,
        "checkOutDate": str(data['departure_date'])
            # 'day': int(data['departure_date']['day']),
            # 'month': int(data['departure_date']['month']),
            # 'year': int(data['departure_date']['year'])
        ,
        "rooms": [
            {
                "adults": 2,
                "children": [{"age": 5}, {"age": 7}]
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 30,
        "sort": 'PRICE_LOW_TO_HIGH',
        "filters": {"price": {
            "max": 150,
            "min": 10
        }}
    }

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    response_hotels = requests.post(url, json=payload, headers=headers)
    if response_hotels.status_code == 200:
        hotels = get_hotels(response_hotels.text)

        if 'error' in hotels:
            bot.send_message(message.chat.id, hotels['error'])
            bot.send_message(message.chat.id, 'Попробуйте осуществить поиск с другими параметрами')
            bot.send_message(message.chat.id, '')

        count = 0
        for hotel in hotels.values():
            if count < int(data['quantity_hotels']):
                count += 1
                summary_payload = {
                    "currency": "USD",
                    "eapid": 1,
                    "locale": "en_US",
                    "siteId": 300000001,
                    "propertyId": hotel['id']
                }
                summary_url = "https://hotels4.p.rapidapi.com/properties/v2/get-summary"
                get_summary = requests.post(summary_url, json=summary_payload, headers=headers)
                if get_summary.status_code == 200:
                    summary_info = hotel_info(get_summary.text)

                    caption = f'Название: {hotel["name"]}\n ' \
                              f'Адрес: {summary_info["address"]}\n' \
                              f'Стоимость проживания в сутки: {hotel["price"]}\n ' \
                              # f'Расстояние до центра: {round(hotel["distance"], 2)} mile.\n'

                    medias = []
                    links_to_images = []
                    try:
                        for random_url in range(int(data['quantity_photo'])):
                            links_to_images.append(summary_info['images']
                                                   [random.randint(0, len(summary_info['images']) - 1)])
                    except IndexError:
                        continue

                    data_to_db = {hotel['id']: {'name': hotel['name'], 'address': summary_info['address'],
                                                'price': hotel['price'], 'distance': round(hotel["distance"], 2),
                                                'date_time': data['date_time'], 'images': links_to_images}}
                    await add_response(data_to_db)

                    if int(data['quantity_photo']) > 0:
                        # формируем MediaGroup с фотографиями и описанием отеля и посылаем в чат
                        for number, url in enumerate(links_to_images):
                            if number == 0:
                                medias.append(InputMediaPhoto(media=url, caption=caption))
                            else:
                                medias.append(InputMediaPhoto(media=url))

                        await bot.send_media_group(message.chat.id, medias)
                    else:
                        # если фотки не нужны, то просто выводим данные об отеле
                        await bot.send_message(message.chat.id, caption)

                else:
                    await bot.send_message(message.chat.id, f'Что-то пошло не так, код ошибки: {get_summary.status_code}')
            else:
                break
    else:
        await bot.send_message(message.chat.id, f'Что-то пошло не так, код ошибки: {response_hotels.status_code}')
    await bot.send_message(message.chat.id, 'Поиск окончен!')
