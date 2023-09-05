import requests
import json
import re
import config


from aiogram.types import Message
from typing import Dict

my_url = "https://hotels4.p.rapidapi.com/locations/v2/search"

headers = {
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


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


def get_info_hotels(message: Message, data: Dict):
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": data['destinationId']},
        "checkInDate": {
            'day': int(data['date_of_entry']['day']),
            'month': int(data['date_of_entry']['month']),
            'year': int(data['date_of_entry']['year'])
        },
        "checkOutDate": {
            'day': int(data['departure_date']['day']),
            'month': int(data['departure_date']['month']),
            'year': int(data['departure_date']['year'])
        },
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

    response_hotels = requests.post('POST', url, payload)
    if response_hotels.status_code == 200:
        response_data = json.loads(response_hotels.text)
        hotels = response_data(response_hotels.text)


    for hotel in hotels:

