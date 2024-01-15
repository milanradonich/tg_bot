import requests
import json
import re
import config

my_url = "https://hotels4.p.rapidapi.com/locations/v3/search"


headers = {
	"X-RapidAPI-Key": config.RAPID_API_KEY,
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


pattern = '<[^<]+?>'
querystring = {"q": "rome", "locale": "en_US"}
response = requests.get(my_url, headers=headers, params=querystring)
print(response.json())
data = json.loads(response.text)           # десериализация JSON
# with open('descr_city.json', 'a') as city_file:
#     json.dump(data, city_file, indent=4)   # сериализация JSON
# print(data)

if response:
    cities = list()
    try:
        result = json.loads(response.text)
        for place in result.get('sr'):
            if place.get('type') in ['CITY', 'NEIGHBORHOOD']:
                city = place.get('regionNames').get('primaryDisplayName')
                description = place.get('regionNames').get('secondaryDisplayName')
                city_id = place.get('gaiaId')
                cities.append((city, description, city_id))
    except Exception:
        cities = None
    print(cities)

# possible_city = {}
#
# info_list = data.get("suggestions")
#
# for item in info_list:
#     for key, value in item.items():
#         if key == 'group' and value == 'CITY_GROUP':
#             hotels = item.get('entities')
#             for hotel in hotels:
#                 if hotel.get('type') == 'CITY':
#                     city_id = hotel.get('destinationId')
#                     city_name = re.sub(pattern, '', hotel.get('caption'))
#                     possible_city[city_id] = city_name
# print(possible_city)


