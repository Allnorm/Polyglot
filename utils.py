import os
import sys
import traceback
import telebot
import configparser
from googletrans import Translator, LANGUAGES

import initdialog
import logger

proxy_port = ""
proxy_type = ""

layouts = {'en': "qwertyuiop[]asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?`~",
           'ru': "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,ёЁ",
           'uk': "йцукенгшщзхїфівапролджєячсмитьбю.ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮ,'₴",
           'be': "йцукенгшўзх'фывапролджэячсмітьбю.ЙЦУКЕНГШЎЗХ'ФЫВАПРОЛДЖЭЯЧСМІТЬБЮ,ёЁ"}


def config_init():
    import distort
    import translate
    global proxy_port
    global proxy_type

    if not os.path.isfile("polyglot.ini"):
        initdialog.init_dialog()

    config = configparser.ConfigParser()
    logger.clear_log()
    try:
        config.read("polyglot.ini")
        token = config["Polyglot"]["token"]
        log_key = config["Polyglot"]["key"]
        translate_verify = config["Polyglot"]["translate-verify"]
        proxy_port = config["Polyglot"]["proxy"]
        proxy_type = config["Polyglot"]["proxy-type"]
        distort.max_inits = config["Distort"]["max-inits"]
        distort.attempts = config["Distort"]["attempts"]
        distort.cooldown = config["Distort"]["cooldown"]
    except Exception as e:
        logger.write_log("ERR: Config file was not found, not readable or incorrect! Bot will close!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        sys.exit(1)

    if token == "":
        logger.write_log("ERR: Token is unknown! Bot will close!")
        sys.exit(1)
    if log_key == "":
        logger.write_log("WARN: Key isn't available! Unsafe mode!")

    if translate_verify == "true" or translate_verify == "True" or translate_verify == "1":
        translate_verify = True
    elif translate_verify == "false" or translate_verify == "False" or translate_verify == "0":
        translate_verify = False
    else:
        logger.write_log("Unknown value \"translate-verify\", value will be set to default")
        translate_verify = True

    logger.key = log_key
    translate.translate_verify = translate_verify
    distort.distort_init()
    return token

bot = telebot.TeleBot(config_init())

if proxy_port != "" and proxy_type != "":
    proxy = {proxy_type: proxy_port}
    translator = Translator(service_urls=['translate.googleapis.com'], proxies=proxy)
    logger.write_log("WARN: working with proxy! Type " + proxy_type + ", address " + proxy_port)
else:
    translator = Translator(service_urls=['translate.googleapis.com'])

    # proxy = {'http':'ip:port'}
    # translator = Translator(service_urls=['translate.googleapis.com'], proxies=proxy)
    # try it if bot was banned in Google Api
    # usually unban happens in about half an hour


def textparser(message):
    if message.reply_to_message is None:
        bot.reply_to(message, "Пожалуйста, используйте эту команду как ответ на сообщение")
        return

    if message.reply_to_message.text is not None:
        inputtext = message.reply_to_message.text
    elif message.reply_to_message.caption is not None:
        inputtext = message.reply_to_message.caption
    elif hasattr(message.reply_to_message, 'poll'):
        inputtext = message.reply_to_message.poll.question + "\n\n"
        for option in message.reply_to_message.poll.options:
            inputtext += "☑️ " + option.text + "\n"
    else:
        bot.reply_to(message, "Перевод не выполнен. В сообщении не обнаружен текст.\n")
        return

    if len(inputtext) >= 3000:
        bot.reply_to(message, "Ошибка. В сообщении более 3000 символов!")
        return

    return inputtext


def extract_arg(arg, num):
    try:
        return arg.split()[num]
    except Exception:
        pass


def extract_lang(lang):
    return translator.detect(lang).lang


def list_of_langs():
    output = "Список всех кодов и соответствующих им языков:\n"

    for key, value in LANGUAGES.items():
        output = output + key + " - " + value + "\n"

    output = output + "\nСписок всех доступных раскладок клавиатуры: "

    for key, value in layouts.items():
        output = output + key + " "

    try:
        file = open("langlist.txt", "w")
        file.write(output)
        file.close()
        logger.write_log("INFO: langlist updated successful")
    except Exception as e:
        logger.write_log("ERR: langlist file isn't available")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
