import requests
import json
import re
import config
import random

from aiogram.types import Message, InputMediaPhoto
from typing import Dict
from aiogram import Bot, Dispatcher, executor, types

from main import bot


# from main import bot


def get_id_city(city):
    my_url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    headers = {
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

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


# 712491


async def find_hotels(message, data):
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": data['destinationId']},
        "checkInDate": {
            data['date_of_entry']
            # "day": 10,
            # "month": 10,
            # "year": 2023
        },
        "checkOutDate": {
            data['departure_date']
            # "day": 15,
            # "month": 10,
            # "year": 2023
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

    response_properties = requests.post(url, payload, headers)
    # assert 200 == response_properties.status_code
    if response_properties.status_code == 200:
        print('Успешно!')
        all_info = json.loads(response_properties.text)
        hotels_data = {}
        for hotel in all_info['data']['propertySearch']['properties']:
            try:
                hotels_data[hotel['id']] = {
                    'name': hotel['name'], 'id': hotel['id'],
                    'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
                    'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
                    'price': hotel['price']['lead']['amount']
                }
            except (KeyError, TypeError):
                continue

        count_hotels = 0
        for hotel in hotels_data.values():
            if count_hotels < int(data['quantity_hotels']):
                count_hotels += 1
                summary_payload = {
                    "currency": "USD",
                    "eapid": 1,
                    "locale": "en_US",
                    "siteId": 300000001,
                    "propertyId": hotel['id']
                }
                summary_url = "https://hotels4.p.rapidapi.com/properties/v2/get-summary"
                summary_response = requests.post(summary_url, json=summary_payload, headers=headers)  # !!!!!
                assert 200 == summary_response.status_code
                if summary_response.status_code == 200:
                    print('Успешно!')
                    info_summary = json.loads(summary_response.text)

                    hotel_data = {
                        'id': info_summary['data']['propertyInfo']['summary']['id'],
                        'name': info_summary['data']['propertyInfo']['summary']['name'],
                        'address': info_summary['data']['propertyInfo']['summary']['location']['address'][
                            'addressLine'],
                        'coordinates': info_summary['data']['propertyInfo']['summary']['location']['coordinates'],
                        'images': [
                            url['image']['url'] for url in
                            info_summary['data']['propertyInfo']['propertyGallery']['images']

                        ]
                    }

                    caption = f'Название: {hotel["name"]}\n ' \
                              f'Адрес: {hotel_data["address"]}\n' \
                              f'Стоимость проживания в сутки: {hotel["price"]}\n ' \
                              f'Расстояние до центра: {round(hotel["distance"], 2)} mile.\n'

                    medias = []
                    links_to_images = []

                    try:
                        for random_url in range(int(data['quantity_hotels'])):
                            links_to_images.append(hotel_data['images']
                                                   [random.randint(0, len(hotel_data['images']) - 1)])
                    except IndexError:
                        continue

                    if int(data['quantity_hotels']) > 0:
                        for number, url in enumerate(links_to_images):
                            if number == 0:
                                medias.append(InputMediaPhoto(media=url, caption=caption))
                            else:
                                medias.append(InputMediaPhoto(media=url))
                        await medias
                    else:
                        await caption

    else:
        print('Провал(')

#
# print(get_id_city('rome'))
# print(find_hotels)

# class Test_new_location():
#     """Работа с новой локацией"""
#     def test_create_new_location(self):
#         """создание новой локации"""
#
#         base_url = 'https://rahulshettyacademy.com'  # базовая юрл
#         key = '?key=qaclick123'     # Параметр для всех запросов
#         post_resouce = '/maps/api/place/add/json'  # ресурс метода пост
#
#         post_url = base_url + post_resouce + key
#
#         json_create_new_location = {
#             "location": {
#                 "lat": -38.383494,
#                 "lng": 33.427362
#             }, "accuracy": 50,
#             "name": "Frontline house",
#             "phone_number": "(+91) 983 893 3937",
#             "address": "29, side layout, cohen 09",
#             "types": [
#                 "shoe park",
#                 "shop"
#             ],
#             "website": "http://google.com",
#             "language": "French-IN"
#
#         }
#
#         result_post = requests.post(post_url, json=json_create_new_location)
#         print(result_post.text)
#         print("Статус код: " + str(result_post.status_code))
#         assert 200 == result_post.status_code
#         if result_post.status_code == 200:
#             print('Успешно!')
#         else:
#             print('Провал(')
#
#         check_post = result_post.json()
#         check_info_post = check_post.get("status")
#         print("Статус-код ответа: " + check_info_post)
#         assert check_info_post =='OK'
#         print("статус верный")
#         place_id = check_post.get("place_id")
#
#         """проверка локации"""
#
#         get_resource = '/maps/api/place/get/json'
#         get_url = base_url + get_resource + key + "&place_id=" + place_id
#         print(get_url)
#         result_get = requests.get(get_url)
#         print(result_get.text)
#
#
# new_place = Test_new_location()
# new_place.test_create_new_location()
