import os
from dataclasses import dataclass
from dotenv import load_dotenv

from typing import List


@dataclass
class TgBot:
    token: str


@dataclass
class RapCONFIG:
    key: str


@dataclass
class Config:
    tg_bot: TgBot
    api_key: RapCONFIG


def load_config(path: str = None) -> Config:
    load_dotenv('.env')
    return Config(
        tg_bot=TgBot(
            token=os.getenv('API_TOKEN'),
        ),
        api_key=RapCONFIG(
            key=os.getenv('RAPID_API_KEY'),
        ),
    )
