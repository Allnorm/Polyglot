import os
import traceback

import interlayer
import logger
import utils
import threading

from distort import distort_main
from qwerty import qwerty_main
from translate import translate_main
from inline import query_text_main

interlayer.translate_init()
interlayer.list_of_langs()
logger.write_log("###POLYGLOT v0.6 pre-alpha build 1 HAS BEEN STARTED###")


def botname_checker(message):  # Crutch to prevent the bot from responding to other bots commands

    if ("@" in message.text and "@" + utils.bot.get_me().username in message.text) or not ("@" in message.text):
        return True
    else:
        return False


@utils.bot.inline_handler(lambda query: len(query.query) >= 0)
def query_text(inline_query):

    query_text_main(inline_query)


@utils.bot.message_handler(commands=['qwerty', 'q'])
def qwerty(message):

    if botname_checker(message):
        qwerty_main(message)


@utils.bot.message_handler(commands=['d', 'distort'])
def distort(message):

    if botname_checker(message):
        threading.Thread(target=distort_main, args=(message,)).start()


@utils.bot.message_handler(commands=['translate', 'trans', 't'])
def translate(message):

    if botname_checker(message):
        translate_main(message)


@utils.bot.message_handler(commands=['start'])
def send_welcome(message):

    if botname_checker(message):
        logger.write_log(logger.BLOB_TEXT, message)
        utils.bot.reply_to(message, "Привет. Я бот - переводчик. "
                                    "Работаю на основе Google Translate API, и могу переводить сообщения "
                                    "в чате на лету.\n\n"
                                    "Для этого добавь меня в чат, и при необходимости перевести чьё-то "
                                    "сообщение 'Ответь' на него, и напиши команду: /t <код языка>. "
                                    "Исходный язык перевода бот определит автоматически.\n\n"
                                    "Остальные команды можно узнать командой /help.\n\n"
                                    "Также я могу работать в личных сообщениях, как обычный переводчик.")


@utils.bot.message_handler(commands=['help', 'h'])
def send_help(message):

    if botname_checker(message):
        logger.write_log(logger.BLOB_TEXT, message)
        utils.bot.reply_to(message, "[/t, /trans, /translate] <язык> - перевести сообщение. Исходный язык определяется "
                                    "автоматически. Коды и названия языков можно "
                                    "узнать с помощью команды /langs или /l\n"
                                    "[/l, /langs] - список доступных языковых кодов и раскладок клавиатуры\n"
                                    "[/d, /distort] <количество итераций> <итоговый язык> - "
                                    "Перевести сообщение на заданное количество "
                                    "рандомных языков и вывести результат на нужном вам языке. "
                                    "Если оставить параметр <итоговый язык> пустым, "
                                    "результат будет выведен на языке оригинала\n"
                                    "[/q, /qwerty] <исходный язык> <итоговый язык> ИЛИ "
                                    "/q <итоговый язык> - смена раскладки текста. Исходный язык может определяться "
                                    "автоматически. Список доступных раскладок можно "
                                    "посмотреть с помощью команды /langs")


@utils.bot.message_handler(commands=['langs', 'l'])
def send_list(message):

    if botname_checker(message):
        logger.write_log(logger.BLOB_TEXT, message)

        try:
            file = open("langlist.txt", "r")
            utils.bot.send_document(message.chat.id, file, message.id,
                                    "Здесь список всех языков для перевода и раскладок")
        except FileNotFoundError:
            logger.write_log("WARN: Trying to re-create removed langlist file")
            interlayer.list_of_langs()
            if not os.path.isfile("langlist.txt"):
                utils.bot.reply_to(message, "Ошибка, список языков отсутствует. Попытка пересоздания файла не удалась. "
                                            "Обратитесь к авторам бота. Информация для отладки сохранена в логах бота.")

        except Exception as e:
            logger.write_log("ERR: langlist file isn't available")
            logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
            utils.bot.reply_to(message, "Ошибка чтения файла с языками. Обратитесь к авторам бота. "
                                        "Информация для отладки сохранена в логах бота.")


@utils.bot.message_handler(commands=['downloadlog'])
def download_log(message):

    if botname_checker(message):
        logger.write_log(logger.BLOB_TEXT, message)
        logger.download_clear_log(message, True)


@utils.bot.message_handler(commands=['clearlog'])
def clear_log(message):

    if botname_checker(message):
        logger.write_log(logger.BLOB_TEXT, message)
        logger.download_clear_log(message, False)


utils.bot.infinity_polling(True)
