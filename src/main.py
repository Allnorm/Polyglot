import configparser
import os
import traceback
import logging

from telebot import types

import locales
import logger
import sql_worker
import utils
import threading

from ad_module import ad_module_init, status_premium, module_add_task, module_rem_task, add_ad
from auto_trans import auto_status, auto_enable, auto_engine
from distort import distort_main, distort_init
from transphoto import photo_main, transphoto_config_init
from qwerty import qwerty_main
from inline import query_text_main


def pre_init():
    config: configparser.ConfigParser
    version = "1.4"
    build = "1"

    if logger.logger_init():
        logging.info("log was cleared successful")

    config = utils.config_init()
    transphoto_config_init(config)
    logger.logger_config_init(config)
    ad_module_init(config)
    distort_init(config)
    utils.whitelist_init()
    utils.translator.translate_init()
    utils.list_of_langs()
    locales.locales_check_integrity(config)
    if locales.locale_data.get("version") != version:
        logging.warning("Polyglot and locale versions doesn't match! This can cause the bot to malfunction."
                        "\nPlease, try to check updates for bot or locales file.")
    logging.info("###POLYGLOT {} build {} HAS BEEN STARTED###".format(version, build))


pre_init()


def botname_checker(message):  # Crutch to prevent the bot from responding to other bots commands

    cmd_text = message.text.split()[0]

    if ("@" in cmd_text and "@" + utils.bot.get_me().username in cmd_text) or not ("@" in cmd_text):
        return True
    else:
        return False


def chat_settings_lang(message, auxiliary_text):
    locales_list = locales.locale_data.get("localesList")
    buttons = types.InlineKeyboardMarkup()
    for locale in locales_list:
        try:
            locale_name = locales.locale_data.get(locale).get("fullName")
        except AttributeError as e:
            logging.error("lang parsing failed!")
            logging.error(str(e) + "\n" + traceback.format_exc())
            continue
        buttons.add(types.InlineKeyboardButton(text=locale_name, callback_data=locale + " " + auxiliary_text))
    if auxiliary_text == "settings" and message.chat.type != "private":
        buttons.add(types.InlineKeyboardButton(text=locales.get_text(message.chat.id, "backBtn"),
                                               callback_data="back"))
        utils.bot.edit_message_text(locales.get_text(message.chat.id, "chooseLang"), message.chat.id, message.id,
                                    reply_markup=buttons, parse_mode='html')
        return
    utils.bot.reply_to(message, locales.get_text(message.chat.id, "chooseLang"),
                       reply_markup=buttons, parse_mode='html')


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


@utils.bot.message_handler(commands=['scan', 'transphoto', 'tph'])
def photo(message):

    if botname_checker(message):
        threading.Thread(target=photo_main, args=(message,)).start()


@utils.bot.message_handler(commands=['translate', 'trans', 't'])
def translate(message):
    if not botname_checker(message):
        return

    inputtext = utils.textparser(message)
    if inputtext is None:
        logger.write_log(message, "none")
        return

    logger.write_log(message, inputtext)
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
        utils.bot.reply_to(message, utils.translator.get_translate(inputtext, lang, src_lang=src_lang)
                           + add_ad(message.chat.id))
    except utils.translator.BadTrgLangException:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "badTrgLangException"))
    except utils.translator.BadSrcLangException:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "badSrcLangException"))
    except utils.translator.TooManyRequestException:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooManyRequestException"))
    except utils.translator.TooLongMsg:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooLongMsg"))
    except utils.translator.EqualLangsException:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "equalLangsException"))
    except utils.translator.UnkTransException:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "unkTransException"))


@utils.bot.message_handler(commands=['detect'])
def detect(message):
    if not botname_checker(message):
        return

    inputtext = utils.textparser(message)
    if inputtext is None:
        logger.write_log(message, "none")
        return

    logger.write_log(message, inputtext)
    try:
        lang = utils.translator.lang_list.get(utils.translator.extract_lang(inputtext))
        if locales.get_chat_lang(message.chat.id) != "en":
            translated_lang = " (" + utils.translator.get_translate(lang, locales.get_chat_lang(message.chat.id)) + ")"
        else:
            translated_lang = ""
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "langDetectedAs").format(lang, translated_lang))
    except (utils.translator.BadTrgLangException, utils.translator.UnkTransException):
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "langDetectErr"))
    except utils.translator.TooLongMsg:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooLongMsg"))
        return
    except utils.translator.TooManyRequestException:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooManyRequestException"))
        return


@utils.bot.message_handler(commands=['start'])
def send_welcome(message):
    if botname_checker(message):
        logger.write_log(message, logger.BLOB_TEXT)
        chat_info = sql_worker.get_chat_info(message.chat.id)
        if not chat_info:
            chat_settings_lang(message, "start")
            return
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "startMSG"))


@utils.bot.message_handler(commands=['settings'])
def send_welcome(message):
    if botname_checker(message):
        logger.write_log(message, logger.BLOB_TEXT)
        if message.chat.type == "private":
            chat_settings_lang(message, "settings")
        else:
            if btn_checker(message, message.from_user.id):
                utils.bot.reply_to(message, locales.get_text(message.chat.id, "adminsOnly"))
                return
            buttons = types.InlineKeyboardMarkup()
            buttons.add(types.InlineKeyboardButton(text=locales.get_text(message.chat.id, "langBtn"),
                                                   callback_data="chooselang"))
            buttons.add(types.InlineKeyboardButton(text=locales.get_text(message.chat.id, "lockBtn"),
                                                   callback_data="adminblock"))
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "settings"),
                               reply_markup=buttons, parse_mode='html')


@utils.bot.message_handler(commands=['help', 'h'])
def send_help(message):
    if botname_checker(message):
        logger.write_log(message, logger.BLOB_TEXT)
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "helpText"))


@utils.bot.message_handler(commands=['langs', 'l'])
def send_list(message):
    if botname_checker(message):
        logger.write_log(message, logger.BLOB_TEXT)

        try:
            file = open("../langlist.txt", "r", encoding="UTF-8")
            utils.bot.send_document(message.chat.id, file, message.id,
                                    locales.get_text(message.chat.id, "langList"))
        except FileNotFoundError:
            logging.warning("trying to re-create removed langlist file")
            utils.translator.list_of_langs()

            if not os.path.isfile("../langlist.txt"):
                utils.bot.reply_to(message, locales.get_text(message.chat.id, "langListRemakeErr"))
                return

            file = open("../langlist.txt", "r")
            utils.bot.send_document(message.chat.id, file, message.id,
                                    locales.get_text(message.chat.id, "langList"))
        except Exception as e:
            logging.error("langlist file isn't available")
            logging.error(str(e) + "\n" + traceback.format_exc())
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "langListReadErr"))


@utils.bot.message_handler(commands=['log'])
def download_log(message):
    if botname_checker(message):
        logger.write_log(message, logger.BLOB_TEXT)
        utils.download_clear_log(message, True)


@utils.bot.message_handler(commands=['clrlog'])
def clear_log(message):
    if botname_checker(message):
        logger.write_log(message, logger.BLOB_TEXT)
        utils.download_clear_log(message, False)


@utils.bot.message_handler(commands=['auto'])
def auto_trans_set(message):
    if not botname_checker(message):
        return

    logger.write_log(message, logger.BLOB_TEXT)

    if not utils.enable_auto:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "autoTransDisabledConf"))
        return

    if utils.extract_arg(message.text, 1) is None:
        auto_status(message)
        return
    else:
        if btn_checker(message, message.from_user.id):
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "adminsOnly"))
            return
        auto_enable(message)


@utils.bot.message_handler(commands=['premium'])
def premium(message):
    if not botname_checker(message):
        return

    logger.write_log(message, logger.BLOB_TEXT)

    status_premium(message)


@utils.bot.message_handler(commands=['addtask'])
def add_task(message):
    if not botname_checker(message):
        return

    logger.write_log(message, logger.BLOB_TEXT)

    module_add_task(message)


@utils.bot.message_handler(commands=['remtask'])
def rm_task(message):
    if not botname_checker(message):
        return

    logger.write_log(message, logger.BLOB_TEXT)

    module_rem_task(message)


def btn_checker(message, who_id):
    chat_info = sql_worker.get_chat_info(message.chat.id)
    if chat_info:
        if chat_info[0][2] == "yes":
            status = utils.bot.get_chat_member(message.chat.id, who_id).status
            if status != "administrator" and status != "owner" and status != "creator":
                return True
    return False


@utils.bot.callback_query_handler(func=lambda call: call.data.split()[0] == "chooselang")
def callback_inline_lang_list(call_msg):
    if btn_checker(call_msg.message, call_msg.from_user.id):
        utils.bot.answer_callback_query(callback_query_id=call_msg.id,
                                        text=locales.get_text(call_msg.message.chat.id, "adminsOnly"), show_alert=True)
        return
    chat_settings_lang(call_msg.message, "settings")


@utils.bot.callback_query_handler(func=lambda call: call.data.split()[0] == "adminblock")
def callback_inline_lang_list(call_msg):
    status = utils.bot.get_chat_member(call_msg.message.chat.id, call_msg.from_user.id).status
    if status != "administrator" and status != "owner" and status != "creator":
        utils.bot.answer_callback_query(callback_query_id=call_msg.id,
                                        text=locales.get_text(call_msg.message.chat.id, "adminsOnly"), show_alert=True)
        return
    chat_info = sql_worker.get_chat_info(call_msg.message.chat.id)
    if not chat_info:
        try:
            sql_worker.write_chat_info(call_msg.message.chat.id, "lang", "en")
        except sql_worker.SQLWriteError:
            return
        chat_info = sql_worker.get_chat_info(call_msg.message.chat.id)
    if chat_info[0][2] == "yes":
        set_lock = "no"
    else:
        set_lock = "yes"
    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton(text=locales.get_text(call_msg.message.chat.id, "backBtn"),
                                           callback_data="back"))
    try:
        sql_worker.write_chat_info(call_msg.message.chat.id, "is_locked", set_lock)
    except sql_worker.SQLWriteError:
        utils.bot.edit_message_text(locales.get_text(call_msg.message.chat.id, "configFailed"),
                                    call_msg.message.chat.id, call_msg.message.id,
                                    reply_markup=buttons, parse_mode="html")
        return
    if set_lock == "yes":
        utils.bot.edit_message_text(locales.get_text(call_msg.message.chat.id, "canSetAdmins"),
                                    call_msg.message.chat.id, call_msg.message.id,
                                    reply_markup=buttons, parse_mode="html")
    else:
        utils.bot.edit_message_text(locales.get_text(call_msg.message.chat.id, "canSetAll"),
                                    call_msg.message.chat.id, call_msg.message.id,
                                    reply_markup=buttons, parse_mode="html")


@utils.bot.callback_query_handler(func=lambda call: call.data.split()[0] == "back")
def callback_inline_back(call_msg):
    if btn_checker(call_msg.message, call_msg.from_user.id):
        utils.bot.answer_callback_query(callback_query_id=call_msg.id,
                                        text=locales.get_text(call_msg.message.chat.id, "adminsOnly"), show_alert=True)
        return
    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton(text=locales.get_text(call_msg.message.chat.id, "langBtn"),
                                           callback_data="chooselang"))
    buttons.add(types.InlineKeyboardButton(text=locales.get_text(call_msg.message.chat.id, "lockBtn"),
                                           callback_data="adminblock"))
    utils.bot.edit_message_text(locales.get_text(call_msg.message.chat.id, "settings"),
                                call_msg.message.chat.id, call_msg.message.id, reply_markup=buttons, parse_mode='html')


@utils.bot.callback_query_handler(func=lambda call: True)
def callback_inline_lang_chosen(call_msg):
    if call_msg.data.split()[0] == "adminblock" or call_msg.data.split()[0] == "back" \
            or call_msg.data.split()[0] == "chooselang":
        return
    if btn_checker(call_msg.message, call_msg.from_user.id):
        utils.bot.answer_callback_query(callback_query_id=call_msg.id,
                                        text=locales.get_text(call_msg.message.chat.id, "adminsOnly"), show_alert=True)
        return
    try:
        sql_worker.write_chat_info(call_msg.message.chat.id, "lang", call_msg.data.split()[0])
    except sql_worker.SQLWriteError:
        buttons = types.InlineKeyboardMarkup()
        if call_msg.message.chat.type != "private":
            buttons.add(types.InlineKeyboardButton(text=locales.get_text(call_msg.message.chat.id, "backBtn"),
                                                   callback_data="back"))
        utils.bot.edit_message_text(locales.get_text(call_msg.message.chat.id, "configFailed"),
                                    call_msg.message.chat.id, call_msg.message.id,
                                    reply_markup=buttons, parse_mode="html")
        if call_msg.data.split()[1] == "settings":
            return
    if call_msg.data.split()[1] == "start":
        utils.bot.edit_message_text(locales.get_text(call_msg.message.chat.id, "startMSG"),
                                    call_msg.message.chat.id, call_msg.message.id)
    elif call_msg.data.split()[1] == "settings":
        buttons = types.InlineKeyboardMarkup()
        if call_msg.message.chat.type != "private":
            buttons.add(types.InlineKeyboardButton(text=locales.get_text(call_msg.message.chat.id, "backBtn"),
                                                   callback_data="back"))
        utils.bot.edit_message_text(locales.get_text(call_msg.message.chat.id, "configSuccess"),
                                    call_msg.message.chat.id, call_msg.message.id,
                                    reply_markup=buttons, parse_mode="html")


@utils.bot.message_handler(content_types=["text", "audio", "document", "photo", "video"])
def auto_translate(message):
    if not utils.enable_auto:
        return

    auto_engine(message)


utils.bot.infinity_polling()
