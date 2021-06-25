import requests
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await bot.send_message(
        message.chat.id,
        "Привет! Я бот который может рассказать тебе о текущей погоде. Отправь в чат /weather <Город> и я вышлю тебе картинку с текущей погодой.",
    )


@dp.message_handler(commands=["weather"])
async def send_weather(message: types.Message):
    if not (city := message.get_args()):
        return await bot.send_message(message.chat.id, "Введите город")
    url = f"http://weather.hotaru.ga/ru/{city}"
    response = requests.get(url)
    if response.headers["content-type"] == "image/jpeg":
        await bot.send_chat_action(message.chat.id, "upload_photo")
        await bot.send_photo(message.chat.id, response.content)
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Не удалось подключиться к API, вы ввели несуществующий город, или хост упал.",
        )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)