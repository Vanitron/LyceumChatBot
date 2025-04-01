import webbrowser
import telebot
import json
import os
from dotenv import load_dotenv
from telebot import types

# Загружаю переменные из .env
load_dotenv()

# Загружаю помещения из Rooms.json
with open('rooms.json', 'r') as file:
    rooms = json.load(file)
list_rooms = sorted([room_dict['name'] for room_dict in rooms])

print(list_rooms)

# Инициализирую подключение к чату
bot = telebot.TeleBot(os.environ.get('TELEGRAM_API_KEY'), parse_mode='HTML')


@bot.message_handler(commands=['site', 'website', 'сайт', 'вебсайт'])
def site(message):
    webbrowser.open('https://estalsch8.edumsko.ru/')


@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, 'Нажми /start для выбор кабинета!')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=4)
    for current_room in list_rooms:
        markup.add(types.InlineKeyboardButton(current_room, callback_data=current_room))
    bot.send_message(message.chat.id, text="Выберите помещение, и я подскажу, как туда добраться. Доступные варианты:",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def get_directions(call):
    if call.message:
        room_name = call.data
        if room_name in list_rooms:
            # поиск помещения
            room = next(item for item in rooms if item["name"] == room_name)
            answer = f"\r\n\r\n\r\n-----\r\nПомещение <b>{room_name}</b> находится на {room['floor']} этаже:\r\n\r\n"

            # выбор соседних помещений
            floor = [element for element in rooms if
                     element['floor'] == room['floor'] and element['side'] == room['side']]

            # если этаж второй добавляем лестницу
            if room['floor'] > 1:
                answer = answer + '⬆️'

            arrow = '→'
            i = 0
            for current_room in floor:
                i += 1
                if i > 1:
                    answer = answer + arrow

                if current_room == room:
                    arrow = '←'
                    answer = answer + f"<b>{current_room['name']}</b>"
                else:
                    answer = answer + current_room['name']

            # если этаж второй добавляем лестницу
            if room['floor'] > 1:
                answer = answer + '⬆️'

            answer = answer + f"\r\n-----\r\n"

            bot.send_message(call.message.chat.id, answer)
        else:
            bot.send_message(call.message.chat.id,
                             f"Помещение {room_name} не найдено. Доступные кабинеты: " + ", ".join(list_rooms))


bot.polling(none_stop=True)
