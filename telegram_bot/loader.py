from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import load_config


config = load_config()
storage = MemoryStorage()         #хранилище
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)   #хранилище
bot['config'] = config
rapid_key = config
headers = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com", "X-RapidAPI-Key": rapid_key
}
