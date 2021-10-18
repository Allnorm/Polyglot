import configparser
import os
import traceback

from telebot import types

import interlayer
import locales
import logger
import sql_worker
import utils
import threading

from distort import distort_main, distort_init
from qwerty import qwerty_main
from inline import query_text_main


def pre_init():
    config: configparser.ConfigParser
    version = "0.7 alpha"
    build = "1"

    if logger.clear_log():
        logger.write_log("INFO: log was cleared successful")

    config = utils.config_init()
    distort_init(config)
    utils.whitelist_init()
    interlayer.translate_init()
    utils.list_of_langs()
    locales.locales_check_integrity(config)
    if locales.locale_data.get("version") != version:
        logger.write_log("WARN: Polyglot and locale versions doesn't match! This can cause the bot to malfunction."
                         "\nPlease, try to check updates for bot or locales file.")
    logger.write_log("###POLYGLOT {} build {} HAS BEEN STARTED###".format(version, build))


pre_init()


def botname_checker(message):  # Crutch to prevent the bot from responding to other bots commands

    if ("@" in message.text and "@" + utils.bot.get_me().username in message.text) or not ("@" in message.text):
        return True
    else:
        return False


def chat_settings_init(message, auxiliary_text):
    locales_list = locales.locale_data.get("localesList")
    buttons = types.InlineKeyboardMarkup()
    for locale in locales_list:
        try:
            locale_name = locales.locale_data.get(locale).get("fullName")
        except AttributeError as e:
            logger.write_log("ERR: lang parsing failed!")
            logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
            continue
        buttons.add(types.InlineKeyboardButton(text=locale_name, callback_data=locale + " " + auxiliary_text))
    utils.bot.reply_to(message, "Choose your language", reply_markup=buttons, parse_mode='html')


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
        inputtext = utils.textparser(message)
        if inputtext is None:
            logger.write_log("none", message)
            return

        logger.write_log(inputtext, message)
        src_lang = None
        message.text = utils.lang_autocorr(message.text)

        if utils.extract_arg(message.text, 2) is not None:
            src_lang = utils.extract_arg(message.text, 1)
            lang = utils.extract_arg(message.text, 2)
        elif utils.extract_arg(message.text, 1) is not None:
            lang = utils.extract_arg(message.text, 1)
        else:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "specifyLang"))
            return

        try:
            inputtext = interlayer.get_translate(inputtext, lang, src_lang=src_lang)
            utils.bot.reply_to(message, inputtext)
        except interlayer.BadTrgLangException:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "badTrgLangException"))
        except interlayer.BadSrcLangException:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "badSrcLangException"))
        except interlayer.TooManyRequestException:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooManyRequestException"))
        except interlayer.TooLongMsg:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooLongMsg"))
        except interlayer.UnkTransException:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "unkTransException"))


@utils.bot.message_handler(commands=['detect'])
def detect(message):
    if not botname_checker(message):
        return

    inputtext = utils.textparser(message)
    if inputtext is None:
        logger.write_log("none", message)
        return

    logger.write_log(inputtext, message)
    try:
        lang = interlayer.lang_list.get(interlayer.extract_lang(inputtext))
        if locales.get_chat_lang(message.chat.id) != "en":
            translated_lang = " (" + interlayer.get_translate(lang, locales.get_chat_lang(message.chat.id)) + ")"
        else:
            translated_lang = ""
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "langDetectedAs").format(lang, translated_lang))
    except (interlayer.BadTrgLangException, interlayer.UnkTransException):
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "langDetectErr"))


@utils.bot.message_handler(commands=['start'])
def send_welcome(message):
    if botname_checker(message):
        logger.write_log(logger.BLOB_TEXT, message)
        chat_info = sql_worker.get_chat_info(message.chat.id)
        if chat_info is None:
            chat_settings_init(message, "start")
            return
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "startMSG"))


@utils.bot.message_handler(commands=['settings'])
def send_welcome(message):
    if botname_checker(message):
        logger.write_log(logger.BLOB_TEXT, message)
        chat_settings_init(message, "settings")


@utils.bot.message_handler(commands=['help', 'h'])
def send_help(message):
    if botname_checker(message):
        logger.write_log(logger.BLOB_TEXT, message)
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "helpText"))


@utils.bot.message_handler(commands=['langs', 'l'])
def send_list(message):
    if botname_checker(message):
        logger.write_log(logger.BLOB_TEXT, message)

        try:
            file = open("langlist.txt", "r")
            utils.bot.send_document(message.chat.id, file, message.id,
                                    locales.get_text(message.chat.id, "langList"))
        except FileNotFoundError:
            logger.write_log("WARN: Trying to re-create removed langlist file")
            interlayer.list_of_langs()

            if not os.path.isfile("langlist.txt"):
                utils.bot.reply_to(message, locales.get_text(message.chat.id, "langListRemakeErr"))
                return

            file = open("langlist.txt", "r")
            utils.bot.send_document(message.chat.id, file, message.id,
                                    locales.get_text(message.chat.id, "langList"))
        except Exception as e:
            logger.write_log("ERR: langlist file isn't available")
            logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "langListReadErr"))


@utils.bot.message_handler(commands=['log'])
def download_log(message):
    if botname_checker(message):
        logger.write_log(logger.BLOB_TEXT, message)
        utils.download_clear_log(message, True)


@utils.bot.message_handler(commands=['clrlog'])
def clear_log(message):
    if botname_checker(message):
        logger.write_log(logger.BLOB_TEXT, message)
        utils.download_clear_log(message, False)


@utils.bot.callback_query_handler(func=lambda call: True)
def callback_inline(call_msg):
    sql_worker.write_chat_info(call_msg.message.chat.id, call_msg.data.split()[0])
    if call_msg.data.split()[1] == "start":
        utils.bot.edit_message_text(locales.get_text(call_msg.message.chat.id, "startMSG"),
                                    call_msg.message.chat.id, call_msg.message.id)
    elif call_msg.data.split()[1] == "settings":
        utils.bot.edit_message_text(locales.get_text(call_msg.message.chat.id, "configSuccess"),
                                    call_msg.message.chat.id, call_msg.message.id)


utils.bot.infinity_polling()
