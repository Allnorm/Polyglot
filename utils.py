import os
import random
import sys
import time
import traceback
import telebot
import configparser

import initdialog
import locales
import logger
import interlayer
import sql_worker

proxy_port = ""
proxy_type = ""
bot: telebot.TeleBot
whitelist = []
enable_ad = True
ad_percent = 50

layouts = {'en': "qwertyuiop[]asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?`~",
           'ru': "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,ёЁ",
           'uk': "йцукенгшщзхїфівапролджєячсмитьбю.ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮ,'₴",
           'be': "йцукенгшўзх'фывапролджэячсмітьбю.ЙЦУКЕНГШЎЗХ'ФЫВАПРОЛДЖЭЯЧСМІТЬБЮ,ёЁ"}


def config_init():
    global proxy_port, proxy_type, bot, enable_ad, ad_percent

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
        enable_ad_set = config["Polyglot"]["enable-ad"].lower()
    except (ValueError, KeyError):
        logger.write_log("ERR: Incorrect enable-ad configuration, ad module will be work by default\n"
                         + traceback.format_exc())
        enable_ad_set = "true"
    if enable_ad_set == "true":
        pass
    elif enable_ad_set == "false":
        enable_ad = False
    else:
        logger.write_log("ERR: Incorrect enable-ad configuration, ad module will be work by default")

    try:
        ad_percent = int(config["Polyglot"]["ad-percent"])
    except (ValueError, KeyError):
        logger.write_log("ERR: Incorrect ad-percent configuration, reset to default (50%)\n"
                         + traceback.format_exc())
    if ad_percent < 0 or ad_percent > 100:
        logger.write_log("ERR: Incorrect ad-percent value, reset to default (50%). Should to be in range 0-100%")

    for checker in range(3):
        try:
            bot.get_me()
            break
        except Exception as e:
            if checker >= 2:
                logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
                logger.write_log("ERR: Telegram API isn't working correctly after three tries, bot will close! "
                                 "Check your connection or API token")
                sys.exit(1)
            else:
                time.sleep(5)

    return config


def textparser(message):
    if message.reply_to_message is None:
        bot.reply_to(message, locales.get_text(message.chat.id, "pleaseAnswer"))
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
        bot.reply_to(message, locales.get_text(message.chat.id, "textNotFound"))
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
            bot.send_message(message.chat.id, locales.get_text(message.chat.id, "logNotFound"))
        except IOError:
            logger.write_log("ERR: user " + logger.username_parser(message) +
                             " tried to download log, but something went wrong!\n" + traceback.format_exc())
            bot.send_message(message.chat.id, locales.get_text(message.chat.id, "logUploadError"))
    else:
        if logger.clear_log():
            logger.write_log("INFO: log was cleared by user " + logger.username_parser(message) + ". Have fun!")
            bot.send_message(message.chat.id, locales.get_text(message.chat.id, "logClearSuccess"))
        else:
            logger.write_log("ERR: user " + logger.username_parser(message) +
                             " tried to clear log, but something went wrong\n!")
            bot.send_message(message.chat.id, locales.get_text(message.chat.id, "logClearError"))


def list_of_langs():
    output = "List of all codes and their corresponding languages:\n"
    interlayer.list_of_langs()
    for key, value in interlayer.lang_list.items():
        output = output + value + " - " + key + "\n"

    output = output + "\nList of all available keyboard layouts: "

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


def add_ad(chat_id):
    if enable_ad is False:
        return ""
    lang_chat_code = "en"
    chat_info = sql_worker.get_chat_info(chat_id)
    if chat_info:
        if chat_info[0][3] == "yes":
            return ""  # Return for premium
        lang_chat_code = chat_info[0][1]
    list_ad = sql_worker.get_tasks(lang_chat_code)
    if not list_ad:
        return ""
    for current_ad in list_ad:
        if int(current_ad[3]) < int(time.time()):
            try:
                sql_worker.rem_task(current_ad[0], current_ad[4])
            except sql_worker.SQLWriteError:
                pass
    percent = random.randint(1, 100)
    if percent > ad_percent:
        return ""
    random_index = random.randint(0, len(list_ad) - 1)
    if list_ad[random_index][2] != lang_chat_code:
        return ""
    return "\n---------------\n" + list_ad[random_index][1]
