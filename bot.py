import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN

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
    url = f"http://weather.hotaru.ga/ru/{city}"
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


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
