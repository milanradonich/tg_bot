import logging
import datetime
import asyncio
import pprint

from aiogram.types import BotCommand, CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar

import hotels_requests
from config import API_TOKEN
from typing import Dict

from tg_bot.database import add_user
from tg_bot.misc.other_func import print_data_without_photo, print_data_with_photo
from tg_bot.keyboards.base_btn import photo_hotel, photo_choice, ikb
from tg_bot.state.lowprice_state import ClientStatesGroup, ProfileStatesGroup, LowPrice
# from tg_bot.database.SQlite import db_start, create_profile, edit_profile


logging.basicConfig(level=logging.INFO)

cb = CallbackData('inline_kb', 'action')  # pattern # коллбек кнопки
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)  # создаем экземпляр бота, подключаемся к API
dp = Dispatcher(bot=bot,
                storage=storage)


async def set_default_commands(dp) -> None:
    commands = [
        BotCommand(command='start', description='Start the bot'),
        BotCommand(command='help', description='Show all commands'),
        BotCommand(command='lowprice', description='Must lower value')
        # BotCommand(command='custom', description='Custom setting search'),
        # BotCommand(command='history', description='Request history'),
        # BotCommand(command='photo', description='Get photo'),
        # BotCommand(command='create', description='new profile')
    ]
    await dp.bot.set_my_commands(commands=commands)


# коллбек кнопки
def get_inline() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Button1', callback_data=cb.new('push_1'))],
        [InlineKeyboardButton('Button2', callback_data=cb.new('push_2'))]
    ])

    return inline_kb


def get_city_btn(city_list: Dict):
    keyboard = []
    for city_id, city_name in city_list.items():
        button = InlineKeyboardButton(city_name, callback_data=city_id)
        keyboard.append([button])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# кнопка для FSM
def get_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Начать работу!'))
    return kb


def get_cancel() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/cancel'))


# Конец


start_kb = ReplyKeyboardMarkup(resize_keyboard=True, )
start_kb.row('Navigation Calendar', 'Dialog Calendar')


async def on_startup(dp):
    print('Загружаем команды...')
    await set_default_commands(dp)
    print('Загружаем базу данных')
    # await db_start()
    print('Бот успешно запущен!')


HELP_CMD = """"
<b>/help</b> - <em>список команд</em>
<b>/start</b> - <em>начать работу с ботом</em>
<b>/lowprice</b> - <em>начать работу с ботом</em>
"""


@dp.message_handler(commands=['cancel'], state='*')
async def cmd_stop(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await message.reply('Галя, отмена!')
    await state.finish()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message) -> None:
    user_name = message.from_user.full_name
    await message.reply(f"Привет, {user_name}!\nДобро пожаловать в бот-путешественник.\n"
                        f"Я помогу тебе найти жилье в разных странах и городах.")

    # await create_profile(user_id=message.from_user.id)  # создается профиль юзера
    await add_user(message.chat.id, message.from_user.username, message.from_user.full_name)
    await message.delete()


@dp.message_handler(commands=['lowprice'])
async def city_input(message: types.Message) -> None:
    await message.reply('Давайте начнем поиск. Введите название города',
                        reply_markup=get_cancel())
    await LowPrice.city.set()


@dp.message_handler(state=LowPrice.city)
async def load_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text

    possible_city = hotels_requests.destination_id(data['city'])
    await message.answer('Выбери город: ', reply_markup=get_city_btn(possible_city))
    await LowPrice.destinationId.set()


@dp.callback_query_handler(lambda callback_query: True, state=LowPrice.destinationId)
async def load_city_id(callback_query: types.CallbackQuery, state: FSMContext):
    city_id = callback_query.data
    async with state.proxy() as data:
        data['destinationId'] = city_id
    await bot.send_message(callback_query.from_user.id, f"Вы выбрали город: {city_id}!")
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=None)
    await callback_query.message.answer("Выберите дату заезда",
                                        reply_markup=await SimpleCalendar().start_calendar())
    await LowPrice.date_of_entry.set()


@dp.callback_query_handler(simple_cal_callback.filter(), state=LowPrice.date_of_entry)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'Дата заезда {date.strftime("%d/%m/%Y")}')
        await state.update_data(date_of_entry=datetime.datetime.strptime(date.strftime("%Y%m%d"), "%Y%m%d").date())
        await callback_query.message.answer('Выберите дату выезда',
                                            reply_markup=await SimpleCalendar().start_calendar())
        await LowPrice.departure_date.set()


@dp.callback_query_handler(simple_cal_callback.filter(), state=LowPrice.departure_date)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'Дата выезда {date.strftime("%d/%m/%Y")}')
        await state.update_data(departure_date=datetime.datetime.strptime(date.strftime("%Y%m%d"), "%Y%m%d").date())
        await callback_query.message.answer('Сколько отелей показать? (от 1 до 5)')
        await LowPrice.quantity_hotels.set()


@dp.message_handler(state=LowPrice.quantity_hotels)
async def load_quantity_hotels(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['quantity_hotels'] = message.text

    await message.answer('Нужно показать фото отелей?', reply_markup=photo_hotel)
    await message.delete()
    await LowPrice.need_photo.set()


@dp.message_handler(Text(equals='НЕТ 🚫️'), state=LowPrice.need_photo)
async def need_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['need_photo'] = message.text
        await message.reply('Держи без фото')
        await print_data_without_photo(message, data)
    await state.finish()


@dp.message_handler(Text(equals='ДА ☑️'), state=LowPrice.need_photo)
async def get_quantity_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['need_photo'] = message.text
    await message.answer('Сколько фото показать?', reply_markup=ReplyKeyboardRemove())
    await LowPrice.quantity_photo.set()
    await message.delete()


@dp.message_handler(state=LowPrice.quantity_photo)
async def send_result_with_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['quantity_photo'] = message.text
        await message.reply('Держи с фото')
        await print_data_with_photo(message, data)
    await state.finish()


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=HELP_CMD, parse_mode='HTML')  # отправляем список только в личку юзеру


@dp.message_handler(content_types=['text'])
async def echo_handler(message: types.Message):
    user_name = message.from_user.full_name
    if message.text.lower() == "привет":
        await message.reply(f'Привет, {user_name} ! Введите команду')
    else:
        await message.reply('Я вас не понял. Введите команду твердо и четко')


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def audio_handler(message: types.Message):
    await message.reply('Я не ищу отели по фото! Повторите команду.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

# создание анкеты с помощью FSM__________________________________________________________________________
# @dp.message_handler(commands=['cancel'], state='*')
# async def cmd_start(message: types.Message, state: FSMContext) -> None:
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#
#     await message.reply('Галя, отмена!')
#     await state.finish()
#
#
# @dp.message_handler(commands=['create'])
# async def cmd_create(message: types.Message) -> None:
#     await message.reply('Давай создадим твой профиль. Для начала отправь мне свое фото',
#                         reply_markup=get_cancel())
#     await ProfileStatesGroup.photo.set()    # установка состояние фото. Бот будет ожидать фото от пользователя
#
#
# @dp.message_handler(lambda message: not message.photo, state=ProfileStatesGroup.photo)
# async def check_photo(message: types.Message):
#     await message.reply('Это не фотография')
#
#
# @dp.message_handler(content_types=['photo'], state=ProfileStatesGroup.photo) # хэндлер обрабатывает входящие фото в состоянии state
# async def load_photo(message: types.Message, state: FSMContext) -> None:
#     async with state.proxy() as data:  #  открываем временное хранилище данных
#         data['photo'] = message.photo[0].file_id    # сохраняем значение фотографии id-фото
#
#     await message.reply('Отправь свое имя')
#     await ProfileStatesGroup.next()   # изменяем состояние на следующее
#
#
# @dp.message_handler(lambda message: not message.text.isdigit() or float(message.text) > 100,
#                     state=ProfileStatesGroup.age)
# async def check_photo(message: types.Message):
#     await message.reply('Введите реальный возраст!')
#
#
# @dp.message_handler(state=ProfileStatesGroup.name)
# async def load_name(message: types.Message, state: FSMContext) -> None:
#     async with state.proxy() as data:  #  открываем временное хранилище данных
#         data['name'] = message.text   # сохраняем значение name
#
#     await message.reply('Сколько тебе лет?')
#     await ProfileStatesGroup.next()   # изменяем состояние на следующее
#
#
# @dp.message_handler(state=ProfileStatesGroup.age)
# async def load_age(message: types.Message, state: FSMContext) -> None:
#     async with state.proxy() as data:  #  открываем временное хранилище данных
#         data['age'] = message.text   # сохраняем значение age
#
#     await message.reply('Расскажи немоного о себе')
#     await ProfileStatesGroup.next()   # изменяем состояние на следующее
#
#
# @dp.message_handler(state=ProfileStatesGroup.descr)
# async def load_descr(message: types.Message, state: FSMContext) -> None:
#     async with state.proxy() as data:  #  открываем временное хранилище данных
#         data['descr'] = message.text   # сохраняем значение descr
#         await bot.send_photo(chat_id=message.from_user.id,
#                                photo=data['photo'], caption=f"{data['name']}, {data['age']}\n{data['descr']}"
#                                                             )
#     await edit_profile(state, user_id=message.from_user.id)
#     await message.reply('Ваша анкета создана')
#     await state.finish()   # завершаем состояние
# конец регистрации


# команда обработчик для FSM
# @dp.message_handler(commands=['start_push'])
# async def cmd_start(message: types.Message) -> None:
#     await message.answer('Добро пожаловать',
#                          reply_markup=get_keyboard())
#
#
# @dp.message_handler(commands=['cancel'], state='*')
# async def cmd_start(message: types.Message, state: FSMContext) -> None:
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#
#     await message.reply('Отменил',
#                         reply_markup=get_keyboard())
#     await state.finish()
#
#
# @dp.message_handler(Text(equals='Начать работу!', ignore_case=True), state=None)
# async def start_work(message: types.Message) -> None:
#     await ClientStatesGroup.photo.set()
#     await message.answer('Сначала отправь нам фотографию!',
#                          reply_markup=get_cancel())
#
#
# @dp.message_handler(lambda message: not message.photo, state=ClientStatesGroup.photo)
# async def check_photo(message: types.Message):
#     return await message.reply('Это не фотография!')
#
#
# @dp.message_handler(lambda message: message.photo, content_types=['photo'], state=ClientStatesGroup.photo)
# async def load_photo(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['photo'] = message.photo[0].file_id
#
#     await ClientStatesGroup.next()
#     await message.reply('А теперь отправь нам описание!')
#
#
# @dp.message_handler(state=ClientStatesGroup.descr)
# async def load_photo(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['descr'] = message.text
#
#     await message.reply('Ваша фотография сохранена!')
#
#     async with state.proxy() as data:
#         await bot.send_photo(chat_id=message.from_user.id,
#                              photo=data['photo'],
#                              caption=data['descr'])
#
#     await state.finish()
# конец


# коллбек кнопки
# @dp.message_handler(commands=['test'])
# async def send_welcome(message: types.Message):
#     await message.reply(text='Welcome!', reply_markup=get_inline())
#
#
# @dp.callback_query_handler(cb.filter(action='push_1'))
# async def push_first_cb_handler(callback: types.CallbackQuery) -> None:
#     await callback.answer('Hello!')
#
#
# @dp.callback_query_handler(cb.filter(action='push_2'))
# async def push_sec_cb_handler(callback: types.CallbackQuery) -> None:
#     await callback.answer('World!')
# конец


# отправка фоточек
# @dp.message_handler(commands=['photo'])
# async def send_image(message: types.Message):
#     await message.answer(text='Кого отправить?', reply_markup=photo_choice)
#     await message.delete()
#
#
# @dp.message_handler(Text(equals='Котики'))
# async def send_cats(message: types.Message):
#     await bot.send_photo(chat_id=message.from_user.id,
#                          photo='http://vsesvoi43.ru/wp-content/uploads/2020/09/kogo-zavesti-kota-ili-koshku.jpg',
#                          caption='Нравится котики?',
#                          reply_markup=ikb)
#     await message.delete()
#
#
# @dp.message_handler(Text(equals='Собачки'))
# async def send_dogs(message: types.Message):
#     await bot.send_photo(chat_id=message.from_user.id,
#                          photo='https://klike.net/uploads/posts/2023-01/1675061216_3-25.jpg',
#                          caption='Нравится собачка?',
#                          reply_markup=ikb)
#     await message.delete()
#
#
# @dp.callback_query_handler()
# async def vote_callback(callback: types.CallbackQuery):
#     if callback.data == 'like':
#         await callback.answer(text='Тебе понравились котики!')
#     await callback.answer(text='Тебе не понравились котики(')
# # конец
