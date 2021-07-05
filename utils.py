import os
import sys
import threading
import time
import traceback
import telebot
import configparser
import json

from google.cloud import translate

import initdialog
import logger

proxy_port = ""
proxy_type = ""
json_key = ""
project_name = ""

layouts = {'en': "qwertyuiop[]asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?`~",
           'ru': "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,ёЁ",
           'uk': "йцукенгшщзхїфівапролджєячсмитьбю.ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮ,'₴",
           'be': "йцукенгшўзх'фывапролджэячсмітьбю.ЙЦУКЕНГШЎЗХ'ФЫВАПРОЛДЖЭЯЧСМІТЬБЮ,ёЁ"}

langlist = ""
lang_frozen = True


def config_init():
    import distort
    global proxy_port, proxy_type, json_key, project_name

    token, key, log_key = "", "", ""

    if not os.path.isfile("polyglot.ini"):
        logger.write_log("WARN: Config file isn't created, trying to create it now")
        print("Hello, mr. new user!")
        initdialog.init_dialog()

    config = configparser.ConfigParser()
    logger.clear_log()
    while True:
        try:
            config.read("polyglot.ini")
            token = config["Polyglot"]["token"]
            log_key = config["Polyglot"]["key"]
            json_key = config["Polyglot"]["keypath"]
            # proxy_port = config["Polyglot"]["proxy"] Temporary disabled
            # proxy_type = config["Polyglot"]["proxy-type"]
            distort.max_inits = config["Distort"]["max-inits"]
            distort.attempts = config["Distort"]["attempts"]
            distort.cooldown = config["Distort"]["cooldown"]
            break
        except Exception as e:
            logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
            logger.write_log("ERR: Incorrect config file! Trying to remake!")
            initdialog.init_dialog()

    if token == "":
        logger.write_log("ERR: Token is unknown! Bot will close!")
        sys.exit(1)
    if log_key == "":
        logger.write_log("WARN: Key isn't available! Unsafe mode!")
    if not os.path.isfile(json_key):
        logger.write_log("ERR: JSON file wasn't found! Bot will close!")
        sys.exit(1)
    try:
        project_name = "projects/" + json.load(open(json_key, 'r')).get("project_id")
    except Exception as e:
        logger.write_log("ERR: Project name isn't readable from JSON! Bot will close!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        sys.exit(1)

    logger.key = log_key
    distort.distort_init()
    return token


bot = telebot.TeleBot(config_init())

translator = translate.TranslationServiceClient.from_service_account_json(json_key)


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
    return translator.detect_language(parent=project_name, content=lang).languages[0].language_code


def lang_frozen_checker():
    time.sleep(15)
    if lang_frozen is True:
        logger.write_log("ERR: langlist-gen timed out! Please check your JSON key or Google Cloud settings!")
        os._exit(1)


def list_of_langs():
    global langlist, lang_frozen
    threading.Thread(target=lang_frozen_checker).start()
    output = "Список всех кодов и соответствующих им языков:\n"
    langlist = translator.get_supported_languages(parent=project_name, display_language_code="ru")
    lang_frozen = False
    for lang in langlist.languages:
        output = output + lang.display_name + " - " + lang.language_code + "\n"

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
