import configparser
import json
import os
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv  # импортируем модуль из библиотеки для хранения констант в переменных среды
from pyrogram import Client, filters

from tg_change_time import change_time_post

load_dotenv()  # Инициализируем его. Константы хранятся в файле .env
config = configparser.ConfigParser()  # создаём объекта парсера файла settings.ini
config.read("settings.ini")

# posting_in_vk = int(config["VK"]["POSTING_IN_VK"])
api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
otloga = int(os.getenv('otloga'))
chanel = int(os.getenv('chanel'))  # блядь, внимательно смотрим совпадение ключей здесь и в .env!!!
tg_period = int(os.getenv('tg_period'))  # через сколько будет постится следующий пост в телеге и вк

with open('times.json') as json_file:  # переписываем время на текущее при старте скрипта
    post_time = json.load(json_file)
post_time["tg"] = int(datetime.now().timestamp())
with open('times.json', 'w') as json_file:
    json.dump(post_time, json_file)  # вот именно таким замысловатым образом

app = Client('smell2', api_id=api_id, api_hash=api_hash)  # инициализируем бота
print("Starting a bot...")


@app.on_message(filters.chat(otloga))  # ждем обновления сообщений в канале предложки (контента)
def new_post(client, message):
    change_time_post()
    with open('times.json') as json_file:
        post_time = json.load(json_file)
    new_time = int(post_time['tg']) + tg_period  # прибавляем время периода в формате 18926473837636
    client.copy_message(  # отправляем сообщение в отложку основного канала
        chat_id=chanel,
        from_chat_id=message.chat.id,
        message_id=message.id,
        schedule_date=datetime.fromtimestamp(new_time).replace(tzinfo=timezone.utc) - timedelta(hours=3))  # тут
    # аккуратно - долго ебся с форматом, только с .replace(tzinfo=timezone.utc) работает
    print("Message uploaded to delayed publication", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Message will be published in channel in", (datetime.fromtimestamp(new_time)))  # с + timedelta(hours=3) в

    post_time['tg'] = new_time  # добавленное время записываем для следующего сообщения
    with open('times.json', 'w') as json_file:
        json.dump(post_time, json_file)

   
app.run()
