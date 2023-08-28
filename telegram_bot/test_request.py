import requests
import json
import re
import config

my_url = "https://hotels4.p.rapidapi.com/locations/search"

headers = {
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

pattern = '<[^>]*'
querystring = {"query": "milan", "locale": "en_US", "currency": "USD"}
response = requests.get(my_url, headers=headers, params=querystring)
data = json.loads(response.text)  # десериализация JSON
with open('descr_city.json', 'w') as city_file:
    json.dump(data, city_file, indent=4)  # сериализация JSON

possible_city = {}
for i_city in data['suggestions'][0]['entities']:
    possible_city[i_city['destinationId']] = re.sub(pattern, '', i_city['caption'])
print(possible_city)

