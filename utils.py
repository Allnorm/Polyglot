import os
import sys
import traceback
import telebot
import configparser

import initdialog
import logger
import interlayer

proxy_port = ""
proxy_type = ""
bot: telebot.TeleBot
whitelist = []

layouts = {'en': "qwertyuiop[]asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?`~",
           'ru': "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,ёЁ",
           'uk': "йцукенгшщзхїфівапролджєячсмитьбю.ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮ,'₴",
           'be': "йцукенгшўзх'фывапролджэячсмітьбю.ЙЦУКЕНГШЎЗХ'ФЫВАПРОЛДЖЭЯЧСМІТЬБЮ,ёЁ"}


def config_init():

    global proxy_port, proxy_type, bot

    if not os.path.isfile("polyglot.ini"):
        logger.write_log("WARN: Config file isn't created, trying to create it now")
        print("Hello, mr. new user!")
        initdialog.init_dialog()

    config = configparser.ConfigParser()

    while True:
        try:
            config.read("polyglot.ini")
            token = config["Polyglot"]["token"]
            if token == "":
                raise ValueError("Token is unknown!")
            config = interlayer.api_init(config)
            break
        except Exception as e:
            logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
            logger.write_log("ERR: Incorrect config file! Trying to remake!")
            initdialog.init_dialog()

    bot = telebot.TeleBot(token)
    try:
        bot.get_me()
    except Exception as e:
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        logger.write_log("ERR: Telegram API isn't working correctly, bot will close! "
                         "Check your connection or API token")
        sys.exit(1)

    return config


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
        logger.write_log("WARN: too long msg from " + logger.username_parser(message))
        return

    return inputtext


def extract_arg(arg, num):
    try:
        return arg.split()[num]
    except IndexError:
        pass


def download_clear_log(message, down_clear_check):

    if user_admin_checker(message) is False:
        return

    if down_clear_check:
        try:
            f = open(logger.current_log, 'r', encoding="utf-8")
            bot.send_document(message.chat.id, f)
            f.close()
            logger.write_log("INFO: log was downloaded successful by " + logger.username_parser(message))
        except FileNotFoundError:
            logger.write_log("INFO: user " + logger.username_parser(message)
                             + " tried to download empty log\n" + traceback.format_exc())
            bot.send_message(message.chat.id, "Лог-файл не найден!")
        except IOError:
            logger.write_log("ERR: user " + logger.username_parser(message) +
                             " tried to download log, but something went wrong!\n" + traceback.format_exc())
            bot.send_message(message.chat.id, "Ошибка выгрузки лога!")
    else:
        if logger.clear_log():
            logger.write_log("INFO: log was cleared by user " + logger.username_parser(message) + ". Have fun!")
            bot.send_message(message.chat.id, "Очистка лога успешна")
        else:
            logger.write_log("ERR: user " + logger.username_parser(message) +
                             " tried to clear log, but something went wrong\n!")
            bot.send_message(message.chat.id, "Ошибка очистки лога")


def list_of_langs():
    output = "Список всех кодов и соответствующих им языков:\n"
    interlayer.list_of_langs()
    for key, value in interlayer.lang_list.items():
        output = output + value + " - " + key + "\n"

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


def lang_autocorr(langstr, inline=False):

    if inline is False:
        langstr = langstr.lower()
        for key, value in interlayer.lang_list.items():
            langstr = langstr.replace(value.lower(), key)
    elif (extract_arg(langstr, 1)) is not None and inline is True:
        for key, value in interlayer.lang_list.items():
            if (extract_arg(langstr, 0) + " " + extract_arg(langstr, 1)).lower() == value.lower():
                args = extract_arg(langstr, 0) + " " + extract_arg(langstr, 1)
                langstr = langstr.replace(args, args.lower(), 1)
                langstr = langstr.replace(value.lower(), key, 1)
                break
            elif (extract_arg(langstr, 0)).lower() == value.lower():
                args = extract_arg(langstr, 0)
                langstr = langstr.replace(args, args.lower(), 1)
                langstr = langstr.replace(value.lower(), key, 1)
                break

    return langstr


def whitelist_init():
    global whitelist

    try:
        file = open("whitelist.txt", 'r', encoding="utf-8")
        whitelist = file.readlines()
    except FileNotFoundError:
        logger.write_log("WARN: file \"whitelist.txt\" not found. Working without admin privileges.")
        return
    except IOError:
        logger.write_log("ERR: file \"whitelist.txt\" isn't readable. Working without admin privileges.")
        return
    if not whitelist:
        logger.write_log("WARN: whitelist is empty. Working without admin privileges.")


def user_admin_checker(message):
    global whitelist

    for checker in whitelist:
        if "@" + str(message.from_user.username) == checker.rstrip("\n") or \
                str(message.from_user.id) == checker.rstrip("\n"):
            return True

    return False
