import telebot
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


bot = telebot.TeleBot('')
output, diagram = [], []
count, numb = 0, 0
now = datetime.now()
now_plus_10 = now + timedelta(minutes=10)
all_list = dict()


@bot.message_handler(commands=['start'])
def send_hello(message):
    bot.reply_to(message, 'Вітаю!\nЦе бот валют. Курс рахуємо по евро.\n'
                          'В нас є такі команди:\n'
                          '"\help" - перелік команд.\n'
                          '"/list" - курс усіх валют.\n'
                          '"/currency" - перегляд курсу певної валюти.\n'
                          '"/exchange" - обмін валют.\n'
                          '"/history" - графік обмінного курсу вибраної валюти за останні 7 днів.')


@bot.message_handler(func=lambda n: True)
def commands(message):
    global count
    global all_list
    global now
    global now_plus_10

    if now > now_plus_10 or count == 0:
        all_list = requests.get(
            'http://data.fixer.io/api/latest?access_key=43974656474e1bc0cc5bb9750288f7c2')
        all_list = all_list.json()['rates']
        count += 1

    if message.text == '/list':
        for currency in all_list:
            key_val = '{} : {}'.format(currency, all_list[currency])
            bot.send_message(message.from_user.id, key_val)

    if message.text == '/help':
        bot.send_message(message.from_user.id,
                         'В нас є такі команди:\n'
                          '"\help" - перелік команд.\n'
                          '"/list" - курс усіх валют.\n'
                          '"/currency" - перегляд курсу певної валюти.\n'
                          '"/exchange" - обмін валют.\n'
                          '"/history" - графік обмінного курсу вибраної валюти за останні 7 днів.')

    if message.text == '/currency':
        bot.send_message(message.from_user.id, "Введіть валюту (наприклад: UAH)")
        bot.register_next_step_handler(message, show_currency)

    if message.text == '/exchange':
        bot.send_message(message.from_user.id, "Введіть число, валюту (наприклад: UAH) и валюту, в яку будемо "
                                               "конвертувати.\nНаприклад: 300 UAH USD")
        bot.register_next_step_handler(message, exchange)

    if message.text == '/history':
        bot.send_message(message.from_user.id, "Введіть валюту (наприклад: UAH)")
        bot.register_next_step_handler(message, draw_plot)


@bot.message_handler(func=lambda n: True)
def show_currency(message):
    global now
    global now_plus_10
    global all_list
    global count

    if now > now_plus_10 or count == 0:
        all_list = requests.get(
            'http://data.fixer.io/api/latest?access_key=43974656474e1bc0cc5bb9750288f7c2')
        all_list = all_list.json()['rates']

        count += 1

    if message.text in all_list:
        res = '{} {}'.format(message.text, all_list[message.text])
        bot.send_message(message.from_user.id, res)

    else:
        bot.send_message(message.from_user.id, 'Такої валюти немає')


@bot.message_handler(func=lambda n: True)
def exchange(message):
    message.text = message.text.split(" ")
    global count
    global all_list
    global now
    global now_plus_10

    if now > now_plus_10 or count == 0:
        all_list = requests.get(
            'http://data.fixer.io/api/latest?access_key=43974656474e1bc0cc5bb9750288f7c2')
        all_list = all_list.json()['rates']

    if len(message.text) == 2:
        name_1 = message.text[0]
        name_2 = message.text[1]
        if name_1 and name_2 in message.text:
            res = all_list[name_2] / all_list[name_1]
            res = '{} {}'.format(round(res, 2), message.text[1])
            bot.send_message(message.from_user.id, res)
        else:
            bot.send_message(message.from_user.id, 'Такої валюти немає')

    if len(message.text) == 3:
        name_1 = message.text[1]
        name_2 = message.text[2]
        if name_1 and name_2 in all_list.keys():
            res = (all_list[name_2] * float(message.text[0])) / all_list[name_1]
            res = '{} {}'.format(round(res, 2), message.text[2])
            bot.send_message(message.from_user.id, res)
        else:
            bot.send_message(message.from_user.id, 'Такої валюти немає')

    else:
        bot.send_message(message.from_user.id, 'Значення введено невірно')


@bot.message_handler(func=lambda n: True)
def draw_plot(message):
    global diagram
    now = datetime.now()

    for day in range(7):
        now_month = now.month if now.month >= 10 else '0{}'.format(now.month)
        now_day = now.day if now.day >= 10 else '0{}'.format(now.day)
        moment = '{}-{}-{}'.format(now.year, now_month, now_day)

        all_list = requests.get(
            'http://data.fixer.io/api/%s?access_key=43974656474e1bc0cc5bb9750288f7c2' %
            (moment))
        all_list = all_list.json()['rates']

        if message.text in all_list:
            values = '{}.{} {}'.format(now_day, now_month, all_list[message.text])
            diagram.append(values)
            now = (now - timedelta(days=1))

        else:
            bot.send_message(message.from_user.id, 'Такої валюти немає')
            break

        if day == 6:
            draw(message)


@bot.message_handler(func=lambda n: True)
def draw(message):
    global numb
    x, y = [], []
    for item in diagram:
        x.append(float(item[0:6]))
        y.append(float(item[6:]))
    plt.figure(numb)
    plt.plot(x, y)
    plt.xlabel('x - day')
    plt.ylabel('y - changes')
    plt.figure(numb).savefig('plot.png')
    bot.send_photo(message.from_user.id, open('plot.png', 'rb'))
    numb += 1
    x.clear()
    y.clear()
    diagram.clear()
    pass


bot.polling(none_stop=True)