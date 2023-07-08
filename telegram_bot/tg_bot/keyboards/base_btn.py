from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

need_photo_hotel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Да ✅'),
            KeyboardButton(text='Нет ❌')
        ]
    ],
    resize_keyboard=True
)
