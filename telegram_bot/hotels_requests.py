import dp
import requests
import json
import re

import states
from aiogram.dispatcher import FSMContext

import config
import random

from aiogram.types import Message, InputMediaPhoto, message
from typing import Dict, List
from aiogram import Bot, Dispatcher, executor, types


def get_id_city(city):
    my_url = "https://hotels4.p.rapidapi.com/locations/v3/search"

    headers = {
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    pattern = '<[^<]+?>'
    querystring = {"q": city, "locale": "en_US"}
    response = requests.get(my_url, headers=headers, params=querystring)
    data = json.loads(response.text)  # десериализация JSON
    # with open('descr_city.json', 'a') as city_file:
    # 	json.dump(data, city_file, indent=4)   # сериализация JSON

    if response:
        possible_city = {}
        try:
            for place in data.get('sr'):
                if place.get('type') in ['CITY']:
                    city_name = re.sub(pattern, '', place.get('regionNames').get('fullName'))
                    # description = re.sub(pattern, '', place.get('regionNames').get('secondaryDisplayName'))
                    city_id = place.get('gaiaId')
                    possible_city[city_id] = city_name

        except Exception:
            possible_city = None
        return possible_city
    return None


async def find_hotels(message, data):
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": data['destinationId']},
        "checkInDate": {
            "day": int(data['date_of_entry'].day),
            "month": int(data['date_of_entry'].month),
            "year": int(data['date_of_entry'].year)
        },
        "checkOutDate": {
            "day": int(data['departure_date'].day),
            "month": int(data['departure_date'].month),
            "year": int(data['departure_date'].year)
        },
        "rooms": [
            {
                "adults": 2,
                "children": [{"age": 5}, {"age": 7}]
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 200,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": 150,
            "min": 10
        }}
    }

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response_properties = requests.post(url, json=payload, headers=headers)

    if response_properties.status_code == 200:
        all_info = json.loads(response_properties.text)
        hotels_data = {}
        for hotel in all_info['data']['propertySearch']['properties']:
            try:
                hotels_data[hotel['id']] = {
                    'name': hotel['name'], 'id': hotel['id'],
                    'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
                    'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
                    'price': hotel['price']['lead']['amount'] # 250.000,
                    # 'address":...,
                    # "reviews":...,
                }
            except (KeyError, TypeError):
                continue
        hotels_info_dict = dict()
        for hotel in hotels_data.values():
            if len(hotels_info_dict) >= int(data['quantity_hotels']):
                break

            hotel_id = hotel.get('id')
            if not hotel_id:
                continue

            hotel_name = hotel.get('name')
            price_per_night = hotel.get('price', 0)
            # score = hotel.get('reviews', {}).get('score', 0)

            hotels_info_dict[hotel_id] = {
                'name': hotel_name,
                'price_per_night': price_per_night,
                # 'score': score,
            }

            # result = f"<b> Отель:</b> {hotel['name']}\n" \
            #         f'Адрес: {hotels_data["address"]}\n' \
            #         f'Стоимость проживания в сутки: {hotel["price"]}\n ' \
            #         f'Расстояние до центра: {round(hotel["distance"], 2)} mile.\n'
            result = f"<b> Отель:</b> {hotel['name']}\n" \
                    f'Стоимость проживания в сутки: {hotel["price"]}\n ' \
                    f'Расстояние до центра: {round(hotel["distance"], 2)} mile.\n'

            return result





    #     count_hotels = 0
    #     for hotel in hotels_data.values():
    #         if count_hotels < int(data['quantity_hotels']):
    #             count_hotels += 1
    #             summary_payload = {
    #                 "currency": "USD",
    #                 "eapid": 1,
    #                 "locale": "en_US",
    #                 "siteId": 300000001,
    #                 "propertyId": hotel['id']
    #             }
    #             summary_url = "https://hotels4.p.rapidapi.com/properties/v2/get-summary"
    #             summary_response = requests.post(summary_url, json=summary_payload, headers=headers)  # !!!!!!
    #             # assert 200 == summary_response.status_code
    #             if summary_response.status_code == 200:
    #                 print('Успешно!')
    #                 info_summary = json.loads(summary_response.text)
    #                 data = json.loads(info_summary)
    
    #                 hotel_data = {
    #                     'id': data['data']['propertyInfo']['summary']['id'],
    #                     'name': data['data']['propertyInfo']['summary']['name'],
    #                     'address': data['data']['propertyInfo']['summary']['location']['address'][
    #                         'addressLine'],
    #                     'coordinates': data['data']['propertyInfo']['summary']['location']['coordinates'],
    #                     'images': [
    #                         url['image']['url'] for url in
    #                         data['data']['propertyInfo']['propertyGallery']['images']
    
    #                     ]
    #                 }
    
    #                 caption = f'Название: {hotel["name"]}\n ' \
    #                           f'Адрес: {hotel_data["address"]}\n' \
    #                           f'Стоимость проживания в сутки: {hotel["price"]}\n ' \
    #                           f'Расстояние до центра: {round(hotel["distance"], 2)} mile.\n'
    
    #                 medias = []
    #                 links_to_images = []
    
    #                 try:
    #                     for random_url in range(int(data['quantity_hotels'])):
    #                         links_to_images.append(hotel_data['images']
    #                                                [random.randint(0, len(hotel_data['images']) - 1)])
    #                 except IndexError:
    #                     continue
    
    #                 if int(data['quantity_hotels']) > 0:
    #                     for number, url in enumerate(links_to_images):
    #                         if number == 0:
    #                             medias.append(InputMediaPhoto(media=url, caption=caption))
    #                         else:
    #                             medias.append(InputMediaPhoto(media=url))
    #                     await message.answer(message.chat.id, medias)
    #                 else:
    #                     await message.answer(message.chat.id, caption)
    
    # else:
    #     print('Провал(')
