import telebot
from telebot import types
import requests
from requests.auth import HTTPDigestAuth
from time import sleep
import os
from logger2_0 import add_to_log, make_image, CAMERA_IP, LOGIN, PASSWORD


# Enter you Telegram bot API key
bot = telebot.TeleBot('TELEGRAM BOT API KEY')
status = True


def create_path():
    # check or create directories for file and data saving
    try:
        gen_path = os.path.join("C:/", "TeleBot")
        os.mkdir(gen_path)

        try:
            photo_path = os.path.join("C:/TeleBot/", "photo")
            os.mkdir(photo_path)
        except OSError:
            print("C:/TeleBot/photo -- already exist!")

        try:
            log_path = os.path.join("C:/TeleBot/", "log")
            os.mkdir(log_path)
        except OSError:
            print("C:/TeleBot/log -- already exist!")

    except OSError:
        print("C:/TeleBot -- already exist!")



@bot.message_handler(commands=['start'])
def start(msg):
    # Enter telegram account id
    telegram_id = 'INPUT YOUR ID'
    username = f"Hello, <b>{msg.from_user.first_name} {msg.from_user.last_name if msg.from_user.last_name else ''}</b>"
    bot.send_message(msg.chat.id, username, parse_mode='html')

    if msg.from_user.id == telegram_id:
        @bot.message_handler(commands=['help'])
        def butt(msg):
            markup = types.ReplyKeyboardMarkup()
            unlock = types.KeyboardButton('Открыть')
            unlocked = types.KeyboardButton('Постоянно открыт')
            locked = types.KeyboardButton('Закрыть/ Постоянно закрыт')

            markup.add(unlock, unlocked, locked)
            bot.send_message(msg.chat.id, "Barier control:", reply_markup=markup)

        @bot.message_handler(commands=['stopbot401'])
        def stop(msg):
            bot.stop_polling()

        @bot.message_handler(content_types=['text'])
        def message_reply(msg):
            if msg.text == "Открыть":

                try:
                    body = '''<IOPortData xmlns="http://www.hikvision.com/ver20/XMLSchema">
                     <outputState>high</outputState>
                    </IOPortData>'''
                    requests.put(f'http://{CAMERA_IP}/ISAPI/System/IO/outputs/1/trigger', data=body,
                                 auth=HTTPDigestAuth(LOGIN, PASSWORD))
                    make_image('Открыто')
                    bot.send_message(msg.chat.id, 'Открыто!')
                    add_to_log(msg.text, "Въездная группа №1.")
                except requests.exceptions.ConnectionError:
                    bot.send_message(telegram_id, "Превышен интервал ожидания. "
                                                "Не удалось получить доступ до камеры.", parse_mode='html')
                    add_to_log("Ошибка операции открытия", "Въездная группа №1.")

                sleep(5)

                try:
                    body = '''<IOPortData xmlns="http://www.hikvision.com/ver20/XMLSchema">
                     <outputState>low</outputState>
                    </IOPortData>'''
                    requests.put(f'http://{CAMERA_IP}/ISAPI/System/IO/outputs/1/trigger', data=body,
                                 auth=HTTPDigestAuth(LOGIN, PASSWORD))
                except requests.exceptions.ConnectionError:
                    bot.send_message(telegram_id, "Превышен интервал ожидания на закрытие. "
                                                "Не удалось получить доступ до камеры.", parse_mode='html')

            elif msg.text == "Постоянно открыт":

                try:
                    body = '''<IOPortData xmlns="http://www.hikvision.com/ver20/XMLSchema">
                     <outputState>high</outputState>
                    </IOPortData>'''
                    requests.put(f'http://{CAMERA_IP}/ISAPI/System/IO/outputs/1/trigger', data=body,
                                 auth=HTTPDigestAuth(LOGIN, PASSWORD))
                    make_image('Постоянно открыт')
                    bot.send_message(msg.chat.id, 'Постоянно открыт!')
                    add_to_log(msg.text, "Въездная группа №1.")
                except requests.exceptions.ConnectionError:
                    bot.send_message(telegram_id, "Превышен интервал ожидания для выполнения --Постоянно открыт--. "
                                                "Не удалось получить доступ до камеры.", parse_mode='html')
                    add_to_log("Ошибка операции постоянно открыт", "Въездная группа №1.")

            elif msg.text == "Закрыть/ Постоянно закрыт":

                try:
                    body = '''<IOPortData xmlns="http://www.hikvision.com/ver20/XMLSchema">
                     <outputState>low</outputState>
                    </IOPortData>'''
                    requests.put(f'http://{CAMERA_IP}/ISAPI/System/IO/outputs/1/trigger', data=body,
                                 auth=HTTPDigestAuth(LOGIN, PASSWORD))
                    bot.send_message(msg.chat.id, 'Закрыт')
                    add_to_log(msg.text, "Въездная группа №1.")
                except requests.exceptions.ConnectionError:
                    bot.send_message(telegram_id, "Превышен интервал ожидания для --Постоянно закрыт--. "
                                                "Не удалось получить доступ до камеры.", parse_mode='html')
                    add_to_log("Ошибка операции закрытия", "Въездная группа №1.")


create_path()
bot.polling(none_stop=status)
