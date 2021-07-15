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

lang_frozen = True


def config_init():
    import distort
    global proxy_port, proxy_type

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
            distort.max_inits = config["Polyglot"]["max-inits"]
            config = interlayer.api_init(config)
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

    logger.key = log_key
    distort.distort_init()
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
        logger.write_log("WARN: too long msg from " + logger.username_parser(message))
        return

    return inputtext


def extract_arg(arg, num):
    try:
        return arg.split()[num]
    except Exception:
        pass


def download_clear_log(message, down_clear_check):
    if extract_arg(message.text, 1) != logger.key and logger.key != "":
        bot.reply_to(message, "Неверный ключ доступа")
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
        except Exception:
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
