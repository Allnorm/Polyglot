import logging
import random
import traceback

import ad_module
import interlayer
import locales
import logger
import utils

MAX_INITS_DEFAULT = 10
max_inits = MAX_INITS_DEFAULT


def distort_init(config):
    global max_inits
    try:
        max_inits = int(config["Polyglot"]["max-inits"])
    except (ValueError, KeyError):
        logging.error("incorrect distort configuration, values will be set to defaults " + "\n"
                         + traceback.format_exc())
        max_inits = MAX_INITS_DEFAULT
        return

    if max_inits < 0 or max_inits > 100:
        logging.error("too broad \"max_inits\" value, value will be set to default")
        max_inits = MAX_INITS_DEFAULT


def distort_main(message):

    if max_inits == 0:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "distortDisabled"))
        return

    inputshiz = utils.textparser(message)
    if inputshiz is None:
        logger.write_log(message, "none")
        return

    logger.write_log(message, inputshiz)

    try:
        counter = int(utils.extract_arg(message.text, 1))
    except (ValueError, TypeError):
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "distortNaN"))
        return

    if counter > max_inits or counter < 1:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "distortWrongNumber").format(str(max_inits)))
        return

    if utils.extract_arg(message.text, 2) is not None:
        endlang = utils.extract_arg(utils.lang_autocorr(message.text), 2)
        if interlayer.lang_list.get(endlang) is None:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "distortWrongLang"))
            return
    else:
        endlang = interlayer.extract_lang(inputshiz)

    tmpmessage = utils.bot.reply_to(message, locales.get_text(message.chat.id, "distortStarted"))
    idc = tmpmessage.chat.id
    idm = tmpmessage.message_id
    lastlang = interlayer.extract_lang(inputshiz)
    randlang = random.choice(list(interlayer.lang_list))

    for i in range(counter):
        while randlang == lastlang:
            randlang = random.choice(list(interlayer.lang_list))

        try:
            inputshiz = interlayer.get_translate(inputshiz, randlang, True)
        except interlayer.TooManyRequestException:
            utils.bot.edit_message_text(locales.get_text(message.chat.id, "tooManyRequestException"), idc, idm)
            return
        except interlayer.TooLongMsg:
            utils.bot.edit_message_text(locales.get_text(message.chat.id, "tooLongMsg"), idc, idm)
            return
        except interlayer.UnkTransException:
            utils.bot.edit_message_text(locales.get_text(message.chat.id, "distortUnkTransException"), idc, idm)
            return

        lastlang = randlang

    try:
        inputshiz = interlayer.get_translate(inputshiz, endlang)
    except (interlayer.UnkTransException, interlayer.TooLongMsg, interlayer.TooManyRequestException,
            interlayer.BadTrgLangException):
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "distortEndingError"))

    utils.bot.edit_message_text(inputshiz + locales.get_text(message.chat.id, "usedDistortions")
                                + ad_module.add_ad(idc), idc, idm)
