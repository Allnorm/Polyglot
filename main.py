import logger
import utils

from distort import distort_main
from qwerty import qwerty_main
from translate import translate_main

logger.clear_log()
logger.write_log("###POLYGLOT WAS STARTED###")
logger.key_reader()
utils.list_of_langs()


@utils.bot.message_handler(commands=['qwerty', 'q'])
def qwerty(message):

    qwerty_main(message)


@utils.bot.message_handler(commands=['d', 'distort'])
def distort(message):

    distort_main(message)


@utils.bot.message_handler(commands=['translate', 'trans', 't'])
def translate(message):

    translate_main(message)


@utils.bot.message_handler(commands=['start'])
def send_welcome(message):

    logger.write_log(logger.BLOB_TEXT, message)
    utils.bot.reply_to(message, "Привет. Я бот - переводчик. "
                          "Работаю на основе Google Translate API, и могу переводить сообщения в чате на лету.\n\n"
                          "Для этого добавь меня в чат, и при необходимости перевести чьё-то "
                          "сообщение 'Ответь' на него, и напиши команду: /t <код языка>. "
                          "Исходный язык перевода бот определит автоматически.\n\n"
                          "Остальные команды можно узнать командой /help.\n\n"
                          "Также я могу работать в личных сообщениях, как обычный переводчик.")


@utils.bot.message_handler(commands=['help', 'h'])
def send_help(message):

    logger.write_log(logger.BLOB_TEXT, message)
    utils.bot.reply_to(message, "[/t, /trans, /translate] <язык> - перевести сообщение. Исходный язык определяется "
                          "автоматически. Коды языков можно узнать с помощью команды /langs или /l\n"
                          "[/l, /langs] - список доступных языковых кодов и раскладок клавиатуры\n"
                          "[/d, /distort] <количество итераций> <итоговый язык> - Перевести сообщение на заданное количество "
                          "рандомных языков и вывести результат на нужном вам языке. "
                          "Если оставить параметр <итоговый язык> пустым, результат будет выведен на языке "
                          "оригинала\n"
                          "[/q, /qwerty] <исходный язык> <итоговый язык> ИЛИ "
                          "/q <итоговый язык> - смена раскладки текста. Исходный язык может определяться "
                          "автоматически. Список доступных раскладок можно посмотреть с помощью команды /langs")


@utils.bot.message_handler(commands=['langs', 'l'])
def send_list(message):

    logger.write_log(logger.BLOB_TEXT, message)

    try:
        file = open("langlist.txt", "r")
        utils.bot.send_document(message.chat.id, file, message.id,
                          "Здесь список всех языков для перевода и раскладок")
    except FileNotFoundError as e:
        utils.bot.reply_to(message, "Ошибка, список языков отсутствует. Попытка пересоздания файла, попробуйте "
                              "отправить команду ещё раз. "
                              "Если это не сработает, обратитесь к автору бота.")
        logger.write_log("WARN: Trying to re-create removed langlist file")
        utils.list_of_langs()
    except Exception as e:
        utils.bot.reply_to(message, "Неизвестная ошибка чтения файла с языками")
        logger.write_log("ERR: langlist isn't available")
        logger.write_log("ERR: " + str(e))


@utils.bot.message_handler(commands=['downloadlog'])
def download_log(message):

    logger.write_log(logger.BLOB_TEXT, message)
    logger.download_clear_log(message, True)

@utils.bot.message_handler(commands=['clearlog'])
def clear_log(message):

    logger.write_log(logger.BLOB_TEXT, message)
    logger.download_clear_log(message, False)

utils.bot.polling(none_stop=True)
