from typing import Dict
import aiohttp
from loader import headers
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import requests


async def get_id_city(data: Dict):
    async with aiohttp.ClientSession() as session:
        url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        querystring = {"query": data.get("city"), "locale": "ru_RU", "currency": "USD"}

        async with session.get(url, headers=headers, params=querystring) as response:
            result = await response.json()
            info_list = result.get("suggestions")

            for item in info_list:
                for key, value in item.items():
                    if key == 'group' and value == 'CITY_GROUP':
                        hotels = item.get('entities')
                        for hotel in hotels:
                            if hotel.get('type') == 'CITY':
                                return hotel.get('destinationId')


def get_hotel_results(obj):
    data = obj["data"]
    body = data["body"]
    search_results = body["searchResults"]
    results = search_results["results"]
    return results


async def get_hotel_info_lowprice(data: Dict, id_city):
    async with aiohttp.ClientSession() as session:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        check_in = data["date_of_entry"]
        check_out = data["departure_date"]

        querystring = {"destinationId": id_city, "pageNumber": "1", "pageSize": data.get('quantity_hotels'),
                       "checkIn": str(check_in), "checkOut": str(check_out), "adults1": "1",
                       "sortOrder": "PRICE", "locale": "ru_RU", "currency": "RUB"}

        async with session.get(url, headers=headers, params=querystring) as response:
            result = await response.json()
            hotel_information_dict = get_hotel_results(result)

            return hotel_information_dict


async def send_hotels_without_photo(hotels_information, index, days_quantity, command, message):
    hotel = hotels_information[index]
    hotel_name = hotel["name"]
    hotel_address = hotel["address"].get("streetAddress")
    hotel_rating = hotel["starRating"]
    distance = hotel["landmarks"][0].get("distance")
    distance_without_km = distance.replace(' км', '')
    distance_for_db = float(distance_without_km.replace(',', '.'))
    price_dict = hotel["ratePlan"].get("price")
    full_price = int(price_dict["exactCurrent"])
    hotel_id = str(hotel["id"])
    hotel_link = 'https://ru.hotels.com/ho' + hotel_id
    one_night_price = int(int(price_dict["exactCurrent"]) / days_quantity)
    # dollar = await get_dollar_course()
    # euro = await get_euro_course()
    # dollar_one_night = round(one_night_price / dollar, 2)
    # euro_one_night = round(one_night_price / euro, 2)
    # dollar_all_time = round(full_price / dollar, 2)
    # euro_all_time = round(full_price / euro, 2)

    await command.add_hotel(id=message.from_user.id, name=hotel_name, address=hotel_address,
                            distance=distance_for_db, night_price=one_night_price,
                            all_period_price=full_price, link=hotel_link)

    await message.answer(
        f'Название отеля {hotel_name}\nАдрес: {hotel_address}\nРасстояние до центра города: {distance}'
        f'\nРейтинг отеля: {hotel_rating} ⭐️'
        f'\nЦена за ночь: {one_night_price} ₽|{dollar_one_night} $|{euro_one_night} €\n'
        f'Цена за весь период: {full_price} ₽|{dollar_all_time} $|{euro_all_time} €'
        f'\nСсылка на номер: {hotel_link}')


# async def get_dollar_course():
#     async with aiohttp.ClientSession() as session:
#         url = 'https://www.banki.ru/products/currency/usd/'
#         user_agent = UserAgent()
#
#         async with session.get(url=url, headers={'user-agent': f'{user_agent.random}'}) as response:
#             src = await response.text()
#             soup = BeautifulSoup(src, "lxml")
#             money = soup.find("div", class_="currency-table__large-text").text
#
#             return float(money.replace(',', '.'))
#
#
# async def get_euro_course():
#     async with aiohttp.ClientSession() as session:
#         url = 'https://www.banki.ru/products/currency/eur/'
#         user_agent = UserAgent()
#         async with session.get(url=url, headers={'user-agent': f'{user_agent.random}'}) as response:
#             src = await response.text()
#             soup = BeautifulSoup(src, "lxml")
#             money = soup.find("div", class_="currency-table__large-text").text
#
#             return float(money.replace(',', '.'))

