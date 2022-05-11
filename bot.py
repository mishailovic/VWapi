import urllib
import uuid
import os

from pymongo import MongoClient
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import (InlineQuery, InlineQueryResultArticle,
                           InlineQueryResultPhoto, InputTextMessageContent)

from config import TOKEN, MONGO_DB, OWM_TOKEN, API_BASE
from utils.http import get_session

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

if MONGO_DB:
    client = MongoClient(MONGO_DB)
    db = client["vwapibot"]
    analytics = db["analytics"]

async def create_user_entry(id):
    analytics.insert_one({
        "_id": id,
        "used_start": 0,
        "used_weather": 0,
        "used_inline": 0
    })

@dp.message_handler(commands=["start", "help"], run_task=True)
async def send_welcome(message: types.Message):
    if MONGO_DB:
        if not analytics.find_one({"_id": message.from_user.id}):
            await create_user_entry(message.from_user.id)

        analytics.update_one({"_id": message.from_user.id}, {"$inc": {"used_start": 1}})

    await message.reply(
        "Привет! Я бот который может рассказать тебе о текущей погоде. Отправь в чат /weather <Город> и я вышлю тебе картинку с текущей погодой."
    )


@dp.message_handler(commands=["weather"], run_task=True)
async def send_weather(message: types.Message):
    if MONGO_DB:
        if not analytics.find_one({"_id": message.from_user.id}):
            await create_user_entry(message.from_user.id)

        analytics.update_one({"_id": message.from_user.id}, {"$inc": {"used_weather": 1}})

    if not (city := message.get_args()):
        return await message.reply("Введите город")

    city = urllib.parse.quote_plus(city)
    session = await get_session()
    async with session.get(API_BASE, params={"city": city}) as resp:
        if resp.headers["content-type"] == "image/jpeg":
            response = await resp.read()
        else:
            response = None

    if response:
        await message.answer_chat_action("upload_photo")
        await message.reply_photo(response)
    else:
        await message.reply(
            "Не удалось подключиться к API, вы ввели несуществующий город, или хост упал."
        )


@dp.inline_handler(run_task=True)
async def inline_echo(inline_query: InlineQuery):
    if MONGO_DB:
        if not analytics.find_one({"_id": inline_query.from_user.id}):
            await create_user_entry(inline_query.from_user.id)

        analytics.update_one({"_id": inline_query.from_user.id}, {"$inc": {"used_inline": 1}})

    result_uuid = str(uuid.uuid4())
    text = inline_query.query

    if not text:
        item = InlineQueryResultArticle(
            id=result_uuid,
            title="Введите название города.",
            input_message_content=InputTextMessageContent(
                "Введите название города."
            ),
        )
        return await bot.answer_inline_query(
            inline_query.id, results=[item], cache_time=1800
        )

    city = urllib.parse.quote_plus(text)
    session = await get_session()
    async with session.get(
        f"https://api.openweathermap.org/geo/1.0/direct?q={city}&appid={OWM_TOKEN}"
    ) as res:
        city_ = await res.text()

    if city_ != "[]":
        url = f"{API_BASE}?city={city}&n={result_uuid}"
        item = InlineQueryResultPhoto(
            id=result_uuid,
            photo_url=url,
            thumb_url=url,
            photo_width=800,
            photo_height=656,
        )
    else:
        item = InlineQueryResultArticle(
            id=result_uuid,
            title="Город не найден.",
            input_message_content=InputTextMessageContent("Город не найден."),
        )

    await bot.answer_inline_query(
        inline_query.id, results=[item], cache_time=1800
    )


if __name__ == "__main__":
    # Heroku defines DYNO environment vaiable
    if os.environ.get("DYNO"):
        app_name = os.environ.get("APP_NAME")

        async def on_startup(dp):
            await bot.set_webhook(f"https://{app_name}.herokuapp.com/bot/{TOKEN}")

        executor.start_webhook(
            dispatcher=dp,
            webhook_path=f"/bot/{TOKEN}",
            on_startup=on_startup,
            skip_updates=True,
            host="localhost",
            port=8081, # Caddy will take care of that
        )
    else:
        executor.start_polling(dp, skip_updates=True)
