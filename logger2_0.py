from datetime import datetime
import requests
from requests.auth import HTTPDigestAuth
import csv
import telebot


CAMERA_IP = input("Enter camera IP: ")
LOGIN = input("Enter login: ")
PASSWORD = input("Enter password: ")
TELEGRAM_ID = 'INPUT YOUR ID'

bot = telebot.TeleBot('TELEGRAM BOT API KEY')


def add_to_log(msg, camera):
    # adding event/ errors to log_file.csv file
    try:
        with open("C:\\TeleBot\\log\\log_file.csv", 'a', newline='', encoding='cp1251') as file:
            writer = csv.writer(file)
            text = [datetime.now().strftime('%Y_%m_%d--%H-%M-%S'), msg, camera]
            writer.writerow(text)
    except PermissionError:
        bot.send_message(TELEGRAM_ID, "Ошибка при сохранении лога. Файл используется другим приложением. Данные не были "
                                    "сохранены.", parse_mode='html')


def make_image(txt):
    dt = datetime.now().strftime("%Y_%m_%d--%H-%M-%S")
    try:
        r = requests.get(f'http://{CAMERA_IP}/ISAPI/Streaming/channels/101/picture?snapShotImageType=JPEG',
                     auth=HTTPDigestAuth(LOGIN, PASSWORD))

    except requests.exceptions.ConnectionError:
        bot.send_message(TELEGRAM_ID, f"Превышен интервал ожидания. "
                                    "Не удалось получить снимок с камеры.", parse_mode='html')

    else:
        if r.status_code == 200:
            with open(f'C:\\TeleBot\\photo\\{dt}--{txt}.jpg', 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)

            with open(f'C:\\TeleBot\\photo\\{dt}--{txt}.jpg', 'rb') as photo:
                bot.send_photo(TELEGRAM_ID, photo)
