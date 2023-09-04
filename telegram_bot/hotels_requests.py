import requests
import json
import re
import config

my_url = "https://hotels4.p.rapidapi.com/locations/v2/search"


headers = {
	"X-RapidAPI-Key": config.RAPID_API_KEY,
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def destination_id(city):
	pattern = '<[^<]+?>'
	querystring = {"query": city, "locale": "en_US", "currency": "USD"}
	response = requests.get(my_url, headers=headers, params=querystring)
	data = json.loads(response.text)           # десериализация JSON
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
