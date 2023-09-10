from aiogram.types import Message
from typing import Dict
import json


async def print_data_without_photo(message: Message, data: Dict):
    text_message = ('Данные вашего запроса: \n'
                    f'Название города: {data["city"]}\n'
                    f'ID города: {data["destinationId"]}\n'
                    f'Дата заезда: {data["date_of_entry"]}\n'
                    f'Дата выезда: {data["departure_date"]}\n'
                    f'Кол-во отелей для выбора: {data["quantity_hotels"]}\n'
                    f'Нужны ли фото? {data["need_photo"]}\n'
                    )

    await message.answer(text_message)


async def print_data_with_photo(message: Message, data: Dict):
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


def get_hotels(response_text: str):
    pass


def hotel_info(hotels_request: str):
    pass

