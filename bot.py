import aiohttp, asyncio, uuid, urllib, langid
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery, InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent

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

    lang = langid.classify(city)[0]
    if lang not in languages:
        lang = "en"

    text_url = urllib.parse.quote_plus(city)
    async with session.get(f"https://weather.hotaru.ga/{lang}/{text_url}") as resp:
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
    result_uuid = str(uuid.uuid4())
    text = inline_query.query

    if not text:
        item = InlineQueryResultArticle(
            id=result_uuid,
            title="Введите название города.",
            input_message_content=InputTextMessageContent("Введите название города.")
        )
        return await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1800)

    lang = langid.classify(text)[0]
    if lang not in languages:
        lang = "en"

    text_url = urllib.parse.quote_plus(text)
    async with session.get(f"https://nominatim.openstreetmap.org/search.php?q={text_url}&format=jsonv2") as res:
        city = await res.text()

    if city != "[]":
        item = InlineQueryResultPhoto(
            id=result_uuid,
            photo_url=f"https://weather.hotaru.ga/{lang}/{text_url}?fuck_cache={result_uuid}",
            thumb_url=f"https://weather.hotaru.ga/{lang}/{text_url}?fuck_cache={result_uuid}",
            photo_width=800,
            photo_height=656
        )
    else:
        item = InlineQueryResultArticle(
            id=result_uuid,
            title="Город не найден.",
            input_message_content=InputTextMessageContent("Город не найден.")
        )

    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1800)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
