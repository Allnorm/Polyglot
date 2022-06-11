import logging
import traceback

import ad_module
import locales
import logger
import utils


def qwerty_main(message):

    text = utils.textparser(message)
    if text is None:
        logger.write_log(message, "none")
        return

    logger.write_log(message, text)
    message.text = utils.lang_autocorr(message.text)
    arg1, arg2 = utils.extract_arg(message.text, 1), utils.extract_arg(message.text, 2)

    if arg1 is None:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "specifyLang"))
        return

    if arg2 is None:
        try:
            tab1 = utils.layouts.get(utils.translator.extract_lang(text))
        except utils.translator.UnkTransException:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "langDetectErr"))
            return
        except utils.translator.TooLongMsg:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooLongMsg"))
            return
        except utils.translator.TooManyRequestException:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooManyRequestException"))
            return
        tab2 = utils.layouts.get(arg1)
    else:
        tab1 = utils.layouts.get(arg1)
        tab2 = utils.layouts.get(arg2)

    if tab1 is None and arg2 is None:
        try:
            recognized_lang = utils.translator.get_translate(utils
                                                             .translator.lang_list.get(utils.translator
                                                                                       .extract_lang(text)), "ru")
        except (utils.translator.BadTrgLangException, utils.translator.UnkTransException,
                utils.translator.TooManyRequestException, utils.translator.TooLongMsg):
            recognized_lang = "Unknown"
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "unknownSourceLang").format(recognized_lang))
        return

    if tab1 is None or tab2 is None:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "unknownLayout"))
        return

    try:
        translated_text = text.translate(str.maketrans(tab1, tab2))
        utils.bot.reply_to(message, translated_text + ad_module.add_ad(message.chat.id))
    except Exception as e:
        logging.error(str(e) + "\n" + traceback.format_exc())
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "layoutError"))
