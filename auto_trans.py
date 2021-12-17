import logging

import ad_module
import interlayer
import locales
import logger
import sql_worker
import utils


def auto_status(message):
    disabled = False
    chat_info = sql_worker.get_chat_info(message.chat.id)
    if not chat_info:
        disabled = True
    if chat_info:
        if chat_info[0][6] == "disable" or chat_info[0][6] == "" or chat_info[0][6] is None:
            disabled = True
    if disabled:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "autoTransStatus")
                           + locales.get_text(message.chat.id, "premiumStatusDisabled"))
        return

    lang = interlayer.lang_list.get(chat_info[0][6])
    try:
        if locales.get_chat_lang(message.chat.id) != "en":
            translated_lang = lang + " (" + interlayer.get_translate(lang, chat_info[0][1]) + ")"
        else:
            translated_lang = ""
    except (interlayer.BadTrgLangException, interlayer.UnkTransException):
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "langDetectErr"))
        return

    utils.bot.reply_to(message, locales.get_text(message.chat.id, "autoTransStatus")
                       + locales.get_text(message.chat.id, "autoTransLang") + translated_lang)


def auto_enable(message):
    set_lang = utils.lang_autocorr(utils.extract_arg(message.text, 1))
    if interlayer.lang_list.get(set_lang) is None and set_lang != "disable":
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "distortWrongLang"))
    else:
        try:
            sql_worker.write_chat_info(message.chat.id, "target_lang", set_lang)
        except sql_worker.SQLWriteError:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "configFailed"))
        if set_lang != "disable":
            lang = interlayer.lang_list.get(set_lang)
            try:
                if locales.get_chat_lang(message.chat.id) != "en":
                    translated_lang = lang + " (" \
                                      + interlayer.get_translate(lang, locales.get_chat_lang(message.chat.id)) + ")"
                else:
                    translated_lang = lang
            except (interlayer.BadTrgLangException, interlayer.UnkTransException):
                utils.bot.reply_to(message, locales.get_text(message.chat.id, "langDetectErr"))
                return
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "autoTransSuccess") + translated_lang)
        else:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "autoTransDisabled"))


def auto_engine(message):

    chat_info = sql_worker.get_chat_info(message.chat.id)
    if not chat_info:
        return

    if chat_info[0][6] == "disable" or chat_info[0][6] == "" or chat_info[0][6] is None:
        return

    if message.text is not None:
        inputtext = message.text
    elif message.caption is not None:
        inputtext = message.caption
    elif hasattr(message, 'poll'):
        inputtext = message.poll.question + "\n\n"
        for option in message.poll.options:
            inputtext += "☑️ " + option.text + "\n"
    else:
        return

    logging.info("user " + logger.username_parser(message) + " sent an AUTO translated message: " + inputtext)

    try:
        text_lang = interlayer.extract_lang(inputtext)
    except interlayer.UnkTransException:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "langDetectErr"))
        return

    if text_lang != chat_info[0][6]:
        try:
            utils.bot.reply_to(message, interlayer.get_translate(inputtext, chat_info[0][6])
                               + ad_module.add_ad(message.chat.id))
        except interlayer.BadTrgLangException:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "badTrgLangException"))
        except interlayer.TooManyRequestException:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooManyRequestException"))
        except interlayer.TooLongMsg:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooLongMsg"))
        except interlayer.UnkTransException:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "unkTransException"))
