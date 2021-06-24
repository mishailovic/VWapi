import requests
import telebot
from config import TOKEN

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message: telebot.types.Message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот который может рассказать тебе о текущей погоде. Отправь в чат /weather <Город> и я вышлю тебе картинку с текущей погодой.",
    )


@bot.message_handler(commands=["weather"])
def send_weather(message: telebot.types.Message):
    if not (city := telebot.util.extract_arguments(message.text)):
        return bot.send_message(message.chat.id, "Введите город")
    url = f"http://weather.hotaru.ga/ru/{city}"
    response = requests.get(url)
    if response.headers["content-type"] == "image/jpeg":
        bot.send_chat_action(message.chat.id, "upload_photo")
        bot.send_photo(message.chat.id, response.content)
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="Не удалось подключиться к API, вы ввели несуществующий город, или хост упал.",
        )


bot.infinity_polling()
