import aiohttp, asyncio, uuid
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery, InlineQueryResultPhoto
from config import TOKEN

from utils import constants

languages = constants.messages["ms"].keys()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def s(): return aiohttp.ClientSession()
session = asyncio.get_event_loop().run_until_complete(s())

@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот который может рассказать тебе о текущей погоде. Отправь в чат /weather <Город> и я вышлю тебе картинку с текущей погодой.")

@dp.message_handler(commands=["weather"])
async def send_weather(message: types.Message):
    if not (city := message.get_args()):
        return await message.answer("Введите город")

    lang = city.split(" ")[-1]
    if lang not in languages:
        lang = "en"

    async with session.get(f"https://weather.hotaru.ga/{lang}/{city}") as resp:
        if resp.headers["content-type"] == "image/jpeg":
            response = await resp.read()
        else:
            response = None

    if response:
        await message.answer_chat_action("upload_photo")
        await message.answer_photo(response)
    else:
        await message.answer("Не удалось подключиться к API, вы ввели несуществующий город, или хост упал.")

@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    await asyncio.sleep(2) # prevent api from flooding
    text = inline_query.query

    city_lang = text.split(" ")[-1]
    if city_lang not in languages:
        city_lang = "en"

    async with session.get(f"https://nominatim.openstreetmap.org/search.php?q={text}&format=jsonv2") as res:
        city = await res.text()

    result_uuid = str(uuid.uuid4())
    if city != "[]":
        item = InlineQueryResultPhoto(
            id=result_uuid,
            photo_url=f"https://weather.hotaru.ga/{city_lang}/{text}?fuck_cache={result_uuid}",
            thumb_url=f"https://weather.hotaru.ga/{city_lang}/{text}?fuck_cache={result_uuid}",
            photo_width=800,
            photo_height=656
        )
    else:
        item = InlineQueryResultPhoto(
            id=result_uuid,
            photo_url=f"https://weather.hotaru.ga/404",
            thumb_url=f"https://weather.hotaru.ga/404",
            photo_width=800,
            photo_height=656
        )

    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1800)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
