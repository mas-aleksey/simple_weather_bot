import asyncio
import logging
import sys
from urllib.parse import quote

import aiohttp
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from bs4 import BeautifulSoup


class BotConfig(BaseSettings):
    token: str
    
    class Config:
        env_file = ".env"
        env_prefix = "BOT_"


dp = Dispatcher()


async def get_weather(city) -> str:
    url = "https://www.google.com/search?q=" + quote("погода в " + city)
    result = ""
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}) as response:
            soup = await response.text()
            bs = BeautifulSoup(soup, "html.parser")
            taw = bs.find("div", {"id": "taw"})
            if taw:
                target = taw.text.split("Результаты:")[-1].replace("∙ Изменить регион", "").strip()
                result = f"Температура в городе {target}: "
            weather = bs.find("span", {"id": "wob_tm"})
            if weather:
                result += weather.text + "°C"
            else:
                return "Не удалось получить погоду в городе " + city
            return result


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello 👋, {hbold(message.from_user.full_name)}!")


@dp.message()
async def message_handler(message: types.Message) -> None:
    try:
        weather = await get_weather(message.text)
        await message.answer(weather)
    except Exception:
        await message.answer("Error")


async def main() -> None:
    load_dotenv()
    config = BotConfig()
    bot = Bot(config.token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
