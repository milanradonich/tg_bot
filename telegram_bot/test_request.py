import requests
import json
import re
import config
import aiohttp
from typing import Dict


async def destination_id(city):
    async with aiohttp.ClientSession() as session:

        url = "https://hotels4.p.rapidapi.com/locations/v2/search"

        querystring = {"query": city.get("city"), "locale": "en_US", "currency": "USD"}

        headers = {
            "X-RapidAPI-Key": config.RAPID_API_KEY,
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }

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


