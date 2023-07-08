from aiogram.types import Message
from aiogram import types
from main import dp


@dp.message_handler(content_types=['text'])
async def text_handler(message: types.Message):
    user_name = message.from_user.full_name
    if message.text.lower() == "привет":
        await message.reply(f'Привет, {user_name} ! Что будем искать?')
    else:
        await message.reply('Я вас не понял. Введите команду твердо и четко')
