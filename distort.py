import random
import traceback

import interlayer
import logger
import utils

MAX_INITS_DEFAULT = 10
max_inits = MAX_INITS_DEFAULT


def distort_init(config):
    global max_inits
    try:
        max_inits = int(config["Polyglot"]["max-inits"])
    except (ValueError, KeyError):
        logger.write_log("ERR: Incorrect distort configuration, values will be set to defaults " + "\n"
                         + traceback.format_exc())
        max_inits = MAX_INITS_DEFAULT
        return

    if max_inits < 0 or max_inits > 100:
        logger.write_log("ERR: Too broad \"max_inits\" value, value will be set to default")
        max_inits = MAX_INITS_DEFAULT


def distort_main(message):

    if max_inits == 0:
        utils.bot.reply_to(message, "Ошибка, хостер бота принудительно отключил функцию Distort")
        return

    inputshiz = utils.textparser(message)
    if inputshiz is None:
        logger.write_log("none", message)
        return

    logger.write_log(inputshiz, message)

    try:
        counter = int(utils.extract_arg(message.text, 1))
    except (ValueError, TypeError):
        utils.bot.reply_to(message, "Ошибка, число не распознано")
        return

    if counter > max_inits or counter < 1:
        utils.bot.reply_to(message, "Ошибка, укажите значение от 1 до " + str(max_inits))
        return

    randlangs_list = ""

    if utils.extract_arg(message.text, 2) is not None:
        endlang = utils.extract_arg(utils.lang_autocorr(message.text), 2)
        if interlayer.lang_list.get(endlang) is None:
            utils.bot.reply_to(message, "Указан неверный код/название яыка")
            return
    else:
        endlang = interlayer.extract_lang(inputshiz)

    tmpmessage = utils.bot.reply_to(message, "Генерация начата, ожидайте")
    idc = tmpmessage.chat.id
    idm = tmpmessage.message_id
    lastlang = interlayer.extract_lang(inputshiz)
    randlang = random.choice(list(interlayer.lang_list))

    for i in range(counter):
        while randlang == lastlang:
            randlang = random.choice(list(interlayer.lang_list))

        randlangs_list += randlang + "; "

        try:
            inputshiz = interlayer.get_translate(inputshiz, randlang, True)
        except interlayer.TooManyRequestException:
            utils.bot.edit_message_text("Слишком много запросов к API, пожалуйста, попробуйте позже.", idc, idm)
            return
        except interlayer.TooLongMsg:
            utils.bot.edit_message_text("Ошибка: текст слишком большой для перевода.", idc, idm)
            return
        except interlayer.UnkTransException:
            utils.bot.edit_message_text("Ошибка искажения текста. Обратитесь к авторам бота\n"
                                        "Информация для отладки сохранена в логах бота.", idc, idm)
            return

        lastlang = randlang

    try:
        inputshiz = interlayer.get_translate(inputshiz, endlang)
    except (interlayer.UnkTransException, interlayer.TooLongMsg, interlayer.TooManyRequestException,
            interlayer.BadTrgLangException):
        utils.bot.reply_to(message, "К сожалению, на итоговый язык не удалось перевести.\n"
                                    "Информация для отладки сохранена в логах бота.")

    utils.bot.edit_message_text(inputshiz + "\n\nИспользовались искажения: " + randlangs_list, idc, idm)
