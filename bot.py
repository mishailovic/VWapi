from aiogram.types.inline_query_result import InlineQueryResultPhoto
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery
from time import sleep, time
import uuid
from config import TOKEN
import requests
import urllib.parse

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет! Я бот который может рассказать тебе о текущей погоде. Отправь в чат /weather <Город> и я вышлю тебе картинку с текущей погодой.",
    )


@dp.message_handler(commands=["weather"])
async def send_weather(message: types.Message):
    if not (city := message.get_args()):
        return await message.answer("Введите город")
    url = f"https://weather.hotaru.ga/ru/{city}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.headers["content-type"] == "image/jpeg":
                response = await resp.read()
            else:
                response = None
    if response:    
        await message.answer_chat_action("upload_photo")
        await message.answer_photo(response)
    else:
        await message.answer(
            "Не удалось подключиться к API, вы ввели несуществующий город, или хост упал.",
        )

@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    sleep(2) # prevent api from flooding
    text = inline_query.query
    urltext = urllib.parse.quote(text)
    r = requests.get(f"https://nominatim.openstreetmap.org/search.php?q={urltext}&format=jsonv2")
    if r.text != "[]":
        urluuid = str(uuid.uuid4())
        url = f"https://weather.hotaru.ga/ru/{urltext}?fuck_cache={urluuid}"
        result_id = urluuid
        item = InlineQueryResultPhoto(
            id=result_id,
            photo_url=url,
            thumb_url=url,
            photo_width	=800,
            photo_height=656
        )    
        await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1800)
    else:
        pass
        
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
