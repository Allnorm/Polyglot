import sys
import traceback
import telebot
from googletrans import Translator, LANGUAGES
import logger

# proxy = {'http':'ip:port'}
# translator = Translator(service_urls=['translate.googleapis.com'], proxies=proxy)
# try it if bot was banned in Google Api
# usually unban happens in about half an hour

translator = Translator(service_urls=['translate.googleapis.com'])

layouts = {'en': "qwertyuiop[]asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?`~",
           'ru': "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,ёЁ",
           'uk': "йцукенгшщзхїфівапролджєячсмитьбю.ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮ,'₴",
           'be': "йцукенгшўзх'фывапролджэячсмітьбю.ЙЦУКЕНГШЎЗХ'ФЫВАПРОЛДЖЭЯЧСМІТЬБЮ,ёЁ"}


def config_init():
    logger.clear_log()
    try:
        file = open("polyglot.conf", 'r')
        token = file.readline().rstrip()
        log_key = file.readline().rstrip()
        file.close()
    except Exception as e:
        logger.write_log("ERR: Config file was not found or not readable! Bot will close!")
        logger.write_log("ERR: " + str(e))
        traceback.print_exc()
        sys.exit(1)
    if token == "":
        logger.write_log("ERR: Token is unknown! Bot will close!")
        sys.exit(1)
    if log_key == "":
        logger.write_log("WARN: Key isn't available! Unsafe mode!")
    logger.key = log_key
    return token


bot = telebot.TeleBot(config_init())


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
        logger.write_log("ERR: " + str(e))
        traceback.print_exc()
