import os
import sys
import traceback
import telebot
import configparser
from google.cloud import translate

import initdialog
import logger

proxy_port = ""
proxy_type = ""
json_key = ""
project_name = "projects/"

layouts = {'en': "qwertyuiop[]asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?`~",
           'ru': "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,ёЁ",
           'uk': "йцукенгшщзхїфівапролджєячсмитьбю.ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮ,'₴",
           'be': "йцукенгшўзх'фывапролджэячсмітьбю.ЙЦУКЕНГШЎЗХ'ФЫВАПРОЛДЖЭЯЧСМІТЬБЮ,ёЁ"}

langlist = ""


def config_init():
    import distort
    import translate
    global proxy_port
    global proxy_type
    global json_key
    global project_name

    if not os.path.isfile("polyglot.ini"):
        initdialog.init_dialog()

    config = configparser.ConfigParser()
    logger.clear_log()
    try:
        config.read("polyglot.ini")
        token = config["Polyglot"]["token"]
        log_key = config["Polyglot"]["key"]
        translate_verify = config["Polyglot"]["translate-verify"]
        json_key = config["GoogleAPI"]["keypath"]
        project_name = project_name + config["GoogleAPI"]["projectname"]
        # proxy_port = config["Polyglot"]["proxy"] Temporary disabled
        # proxy_type = config["Polyglot"]["proxy-type"]
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


def list_of_langs():
    global langlist
    output = "Список всех кодов и соответствующих им языков:\n"
    langlist = translator.get_supported_languages(parent=project_name, display_language_code="ru")
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
