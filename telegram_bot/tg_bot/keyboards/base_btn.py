from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,\
    InlineKeyboardButton

photo_hotel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn_yes = KeyboardButton(text='ДА ☑️')
btn_no = KeyboardButton(text='НЕТ 🚫️')
photo_hotel.add(btn_yes, btn_no)


photo_choice = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn_cat = KeyboardButton(text='Котики')
btn_dog = KeyboardButton(text='Собачки')
photo_choice.add(btn_cat, btn_dog)


ikb = InlineKeyboardMarkup(row_width=2)
ib1 = InlineKeyboardButton(text='❤️ ',
                           callback_data='like')
ib2 = InlineKeyboardButton(text='💔️ ',
                           callback_data='dislike')
ikb.add(ib1, ib2)

# photo_choice = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text='Cat'),
#             KeyboardButton(text='Dogs')
#         ]
#     ],
#     resize_keyboard=True, one_time_keyboard=True)
