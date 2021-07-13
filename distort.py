import random
import traceback

import interlayer
import logger
import utils

MAX_INITS_DEFAULT = 10
max_inits = MAX_INITS_DEFAULT


def distort_init():
    global max_inits
    try:
        max_inits = int(max_inits)
    except (ValueError, TypeError):
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

    if utils.extract_arg(message.text, 2) is not None and utils.extract_arg(message.text, 3) is not None:
        endlang = utils.extract_arg(message.text, 2) + " " + utils.extract_arg(message.text, 3)
    elif utils.extract_arg(message.text, 2) is not None:
        endlang = utils.extract_arg(message.text, 2)
    else:
        endlang = interlayer.extract_lang(inputshiz)

    tmpmessage = utils.bot.reply_to(message, "Генерация начата, ожидайте")
    idc = tmpmessage.chat.id
    idm = tmpmessage.message_id
    lastlang = interlayer.extract_lang(inputshiz)
    randlang = random.choice(list(interlayer.langlist.languages)).language_code

    for i in range(counter):
        while randlang == lastlang:
            randlang = random.choice(list(interlayer.langlist.languages)).language_code

        randlangs_list += randlang + "; "

        try:
            inputshiz = interlayer.get_translate(inputshiz, randlang, True)
        except interlayer.TooManyRequestException:
            utils.bot.edit_message_text("Слишком много запросов к API, пожалуйста, попробуйте позже.", idc, idm)
            return
        except Exception:
            utils.bot.edit_message_text("Ошибка искажения текста. Обратитесь к авторам бота\n"
                                        "Информация для отладки сохранена в логах бота.", idc, idm)
            return

        lastlang = randlang

    while True:
        try:
            inputshiz = interlayer.get_translate(inputshiz, endlang)
            break
        except interlayer.BadTrgLangException:
            endlang = interlayer.extract_lang(utils.textparser(message))
        except interlayer.TooManyRequestException:
            utils.bot.edit_message_text("Слишком много запросов к API, пожалуйста, попробуйте позже.", idc, idm)
            return

    utils.bot.edit_message_text(inputshiz + "\n\nИспользовались искажения: " + randlangs_list, idc, idm)
