import logging
import random
import traceback

import ad_module
import locales
import logger
import utils

MAX_INITS_DEFAULT = 10
max_inits = MAX_INITS_DEFAULT
lang_output = False


def distort_init(config):
    global max_inits, lang_output
    try:
        max_inits = int(config["Polyglot"]["max-inits"])
        if config["Polyglot"]["distort-output"].lower() == "true":
            lang_output = "True"
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
        if utils.translator.lang_list.get(endlang) is None:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "distortWrongLang"))
            return
    else:
        try:
            endlang = utils.translator.extract_lang(inputshiz)
        except utils.translator.UnkTransException:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "langDetectErr"))
            return
        except utils.translator.TooLongMsg:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooLongMsg"))
            return
        except utils.translator.TooManyRequestException:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooManyRequestException"))
            return

    try:
        lastlang = utils.translator.extract_lang(inputshiz)
    except utils.translator.UnkTransException:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "langDetectErr"))
        return
    except utils.translator.TooLongMsg:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooLongMsg"))
        return
    except utils.translator.TooManyRequestException:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "tooManyRequestException"))
        return

    tmpmessage = utils.bot.reply_to(message, locales.get_text(message.chat.id, "distortStarted"))
    idc = tmpmessage.chat.id
    idm = tmpmessage.message_id
    randlang = random.choice(list(utils.translator.lang_list))
    randlang_list = ""
    if lang_output:
        randlang_list = locales.get_text(message.chat.id, "usedDistortions")

    for i in range(counter):
        while randlang == lastlang:
            randlang = random.choice(list(utils.translator.lang_list))

        try:
            inputshiz = utils.translator.get_translate(inputshiz, randlang, True)
        except utils.translator.TooManyRequestException:
            utils.bot.edit_message_text(locales.get_text(message.chat.id, "tooManyRequestException"), idc, idm)
            return
        except utils.translator.TooLongMsg:
            utils.bot.edit_message_text(locales.get_text(message.chat.id, "tooLongMsg"), idc, idm)
            return
        except utils.translator.UnkTransException:
            utils.bot.edit_message_text(locales.get_text(message.chat.id, "distortUnkTransException"), idc, idm)
            return

        if lang_output:
            randlang_list += randlang + "; "
        lastlang = randlang

    try:
        inputshiz = utils.translator.get_translate(inputshiz, endlang)
    except (utils.translator.UnkTransException, utils.translator.TooLongMsg,
            utils.translator.TooManyRequestException, utils.translator.BadTrgLangException):
        utils.bot.edit_message_text(locales.get_text(message.chat.id, "distortEndingError"), idc, idm)
        return

    utils.bot.edit_message_text(inputshiz + randlang_list + ad_module.add_ad(idc), idc, idm)
