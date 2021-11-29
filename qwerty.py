import traceback

import interlayer
import locales
import logger
import utils


def qwerty_main(message):

    text = utils.textparser(message)
    if text is None:
        logger.write_log("none", message)
        return

    logger.write_log(text, message)
    message.text = utils.lang_autocorr(message.text)
    arg1, arg2 = utils.extract_arg(message.text, 1), utils.extract_arg(message.text, 2)

    if arg2 is None:
        tab1 = utils.layouts.get(interlayer.extract_lang(text))
        tab2 = utils.layouts.get(arg1)
    else:
        tab1 = utils.layouts.get(arg1)
        tab2 = utils.layouts.get(arg2)

    if tab1 is None and arg2 is None:
        try:
            recognized_lang = interlayer.get_translate(interlayer.lang_list.get
                                                             (interlayer.extract_lang(text)), "ru")
        except (interlayer.BadTrgLangException, interlayer.UnkTransException, interlayer.TooManyRequestException):
            recognized_lang = "Unknown"
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "unknownSourceLang").format(recognized_lang))
        return

    if tab1 is None or tab2 is None:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "unknownLayout"))
        return

    try:
        translated_text = text.translate(str.maketrans(tab1, tab2))
        utils.bot.reply_to(message, translated_text + utils.add_ad(message.chat.id))
    except Exception as e:
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "layoutError"))
