from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from logger2_0 import add_to_log, make_image, CAMERA_IP, LOGIN, PASSWORD
import telebot
import socket
import requests
from requests.auth import HTTPDigestAuth

IP = socket.gethostbyname(socket.gethostname())  # get server IP-address where HTTP-server will be running
bot = telebot.TeleBot('TELEGRAM BOT API KEY')


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    # run HTTP-server
    server_address = (IP, 8000)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


def set_to_camera():
    # set up ANPR "alarm server" parameter
    try:
        body = f'''<HttpHostNotification version="2.0" xmlns="http://www.hikvision.com/ver20/XMLSchema">
        <id>1</id>
        <url>/</url>
        <protocolType>HTTP</protocolType>
        <parameterFormatType>XML</parameterFormatType>
        <addressingFormatType>ipaddress</addressingFormatType>
        <ipAddress>{IP}</ipAddress>
        <portNo>8000</portNo>
        <userName></userName>
        <httpAuthenticationMethod>none</httpAuthenticationMethod>
        <httpBroken>true</httpBroken>
        <ANPR>
            <detectionUpLoadPicturesType opt="all,licensePlatePicture,detectionPicture">licensePlatePicture</detectionUpLoadPicturesType>
        </ANPR>
        </HttpHostNotification>'''
        requests.put(f'http://{CAMERA_IP}/ISAPI/Event/notification/httpHosts', data=body,
                     auth=HTTPDigestAuth(LOGIN, PASSWORD))
    except requests.exceptions.ConnectionError:
        print("Connection to camera Failed!")
    else:
        print("Connection succeed!")


class HttpGetHandler(BaseHTTPRequestHandler):
    """Handler with implemented methods do_GET, do_POST, do_PUT."""

    def do_GET(self):  # check HTTP-server status
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write('<html><head><meta charset="utf-8">'.encode())
        self.wfile.write('<title>Простой HTTP-сервер.</title></head>'.encode())
        self.wfile.write('<body>Был получен GET-запрос.</body></html>'.encode())

    def do_POST(self):  # get ANPR event
        self.send_response(200)
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        # get number plate
        plate_number = post_body[post_body.find(b'<originalLicensePlate>') + 22:
                        post_body.find(b'</originalLicensePlate>')].decode('utf-8')

        make_image(plate_number)

        telegram_id = 'INPUT YOUR ID'
        bot.send_message(telegram_id, f"Проезд автомобиля: {plate_number}", parse_mode='html')
        add_to_log(plate_number, "Въездная группа №1.")
        self.wfile.write('<html><head><meta charset="utf-8">'.encode())
        self.wfile.write('<body>Был получен POST-запрос.</body></html>'.encode())

    def do_PUT(self):
        self.send_response(200)
        self.wfile.write('<body>Был получен PUT-запрос.</body></html>'.encode())


set_to_camera()
run(handler_class=HttpGetHandler)
