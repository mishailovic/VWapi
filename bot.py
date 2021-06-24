import requests
import telebot
import os


bot = telebot.TeleBot(Token)
def extract_arg(arg):
    return arg.split()[1:]
   

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.send_message(message.chat.id, "Привет! Я бот который может рассказать тебе о текущей погоде. Отправь в чат /weather <Город> и я вышлю тебе картинку с текущей погодой.")

@bot.message_handler(commands=['weather'])
def send_welcome(message):
    city = str(extract_arg(message.text))
    msg = bot.send_message(message.chat.id, "Получаю прогноз с апи...") 
    url = f'http://weather.hotaru.ga/ru/{city}'
    response = requests.get(url)
    if response.status_code == 200:
        with open('./Image.jpg','wb') as f:
            f.write(response.content)
        bot.edit_message_text(chat_id = message.chat.id, message_id = msg.message_id, text = "Прогноз получен, отправляю...")
        bot.send_chat_action(message.chat.id, 'upload_photo')
        img = open('Image.jpg', 'rb')
        bot.delete_message(chat_id = message.chat.id, message_id = msg.message_id)
        bot.send_photo(message.chat.id, img)
        os.system("rm Image.jpg")
    else:
        bot.edit_message_text(chat_id = message.chat.id, message_id = msg.message_id, text = "Не удалось подключиться к API, вы ввели несуществующий город, или хост упал.")


bot.polling()

