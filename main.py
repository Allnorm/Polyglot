import configparser
import os
import traceback
import datetime
import time

from telebot import types

import adservice
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
    version = "1.0 pre-alpha"
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


def chat_settings_lang(message, auxiliary_text):
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
        except interlayer.EqualLangsException:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "equalLangsException"))
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
            chat_settings_lang(message, "start")
            return
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "startMSG"))


@utils.bot.message_handler(commands=['settings'])
def send_welcome(message):
    if botname_checker(message):
        logger.write_log(logger.BLOB_TEXT, message)
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


def force_premium(message, current_chat):
    if utils.user_admin_checker(message) is False:
        return
    if current_chat[0][3] == "no":
        timer = "0"
        if utils.extract_arg(message.text, 2) is not None:
            try:
                timer = str(int(time.time()) + int(utils.extract_arg(message.text, 2)) * 86400)
            except ValueError:
                utils.bot.reply_to(message, locales.get_text(message.chat.id, "parseTimeError"))
                return
        try:
            sql_worker.write_chat_info(message.chat.id, "premium", "yes")
            sql_worker.write_chat_info(message.chat.id, "expire_time", timer)
        except sql_worker.SQLWriteError:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "premiumError"))
            return
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "forcePremium"))
    else:
        try:
            sql_worker.write_chat_info(message.chat.id, "premium", "no")
            sql_worker.write_chat_info(message.chat.id, "expire_time", "0")
        except sql_worker.SQLWriteError:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "premiumError"))
            return
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "forceUnPremium"))


@utils.bot.message_handler(commands=['premium'])
def premium(message):

    if not botname_checker(message):
        return

    sql_worker.actualize_chat_premium(message.chat.id)
    current_chat = sql_worker.get_chat_info(message.chat.id)
    if current_chat is None:
        try:
            sql_worker.write_chat_info(message.chat.id, "premium", "no")
        except sql_worker.SQLWriteError:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "premiumError"))
            return
        current_chat = sql_worker.get_chat_info(message.chat.id)

    if utils.extract_arg(message.text, 1) == "force":
        # Usage: /premium force [time_in_hours (optional argument)]
        force_premium(message, current_chat)
        return

    if current_chat[0][3] == "no":
        premium_status = locales.get_text(message.chat.id, "premiumStatusDisabled")
    else:
        if current_chat[0][4] != 0:
            premium_status = locales.get_text(message.chat.id, "premiumStatusTime") + " " + \
                         datetime.datetime.fromtimestamp(current_chat[0][4]).strftime("%d.%m.%Y %H:%M:%S")
        else:
            premium_status = locales.get_text(message.chat.id, "premiumStatusInfinity")

    utils.bot.reply_to(message, locales.get_text(message.chat.id, "premiumStatus") + " <b>" + premium_status + "</b>",
                       parse_mode="html")


@utils.bot.message_handler(commands=['mailing'])
def mailing(message):

    if not botname_checker(message):
        return
    if utils.user_admin_checker(message) is False:
        return

    if message.reply_to_message is None:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "pleaseAnswer"))
        return

    logger.write_log(logger.BLOB_TEXT, message)
    adservice.mailing(message.reply_to_message)
    utils.bot.reply_to(message, locales.get_text(message.chat.id, "mailingSuccess"))


def btn_checker(message, who_id):
    chat_info = sql_worker.get_chat_info(message.chat.id)
    if chat_info is not None:
        if utils.bot.get_chat_member(message.chat.id, who_id).status != "administrator" \
                and chat_info[0][2] == "yes":
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
    if utils.bot.get_chat_member(call_msg.message.chat.id, call_msg.from_user.id).status != "administrator":
        utils.bot.answer_callback_query(callback_query_id=call_msg.id,
                                        text=locales.get_text(call_msg.message.chat.id, "adminsOnly"), show_alert=True)
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


utils.bot.infinity_polling()
