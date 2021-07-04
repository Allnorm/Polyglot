import random
import sys
import time
import traceback

import logger
import utils

MAX_INITS_DEFAULT = 10
ATTEMPTS_DEFAULT = 3
COOLDOWN_DEFAULT = 10

max_inits = MAX_INITS_DEFAULT
attempts = ATTEMPTS_DEFAULT
cooldown = COOLDOWN_DEFAULT


def distort_init():
    global max_inits, attempts, cooldown
    try:
        max_inits = int(max_inits)
        attempts = int(attempts)
        cooldown = int(cooldown)
    except (ValueError, TypeError):
        logger.write_log("ERR: Incorrect distort configuration, values will be set to defaults " + "\n"
                         + traceback.format_exc())
        max_inits = MAX_INITS_DEFAULT
        attempts = ATTEMPTS_DEFAULT
        cooldown = COOLDOWN_DEFAULT
        return

    if max_inits < 0 or max_inits > sys.maxsize:
        logger.write_log("ERR: Too broad \"max_inits\" value, value will be set to default")
        max_inits = MAX_INITS_DEFAULT
    if attempts < 0 or attempts > sys.maxsize:
        logger.write_log("ERR: Too broad \"attempts\" value, value will be set to default")
        attempts = ATTEMPTS_DEFAULT
    if cooldown < 0 or cooldown > sys.maxsize:
        logger.write_log("ERR: Too broad \"cooldown\" value, value will be set to default")
        cooldown = COOLDOWN_DEFAULT


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

    randlangs = ""

    if utils.extract_arg(message.text, 2) is not None and utils.extract_arg(message.text, 3) is not None:
        endlang = utils.extract_arg(message.text, 2) + " " + utils.extract_arg(message.text, 3)
    elif utils.extract_arg(message.text, 2) is not None:
        endlang = utils.extract_arg(message.text, 2)
    else:
        endlang = utils.extract_lang(inputshiz)

    tmpmessage = utils.bot.reply_to(message, "Генерация начата, осталось " + str(counter * cooldown) + " секунд")
    idc = tmpmessage.chat.id
    idm = tmpmessage.message_id

    for i in range(counter):
        randlang = random.choice(list(utils.langlist.languages)).language_code

        randlangs += randlang + "; "

        for iteration in range(attempts):  # three tries as default, if = 0 => without checking
            inputshizchecker = inputshiz

            try:
                inputshiz = utils.translator.translate_text(parent=utils.project_name,
                                                             contents=[inputshiz], target_language_code=randlang,
                                                             mime_type="text/plain").translations[0].translated_text
                if inputshizchecker != inputshiz:
                    break

            except Exception as e:
                if str(e) in "invalid destination language":
                    pass
                else:
                    logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
                    utils.bot.edit_message_text("Ошибка искажения текста. Обратитесь к авторам бота\n"
                                                "Информация для отладки сохранена в логах бота.", idc, idm)
                    return

            if iteration == attempts - 1:
                logger.write_log("ERR GOOGLE_API_REJECT")
                utils.bot.edit_message_text("Неизвестная ошибка перевода. Повторите попытку позже.\n"
                                            "Возможно, запрос был заблокирован Google Api", idc, idm)
                return

        time.sleep(cooldown)

        outstr = "Готова итерация " + str(i + 1) + "/" + str(counter) + "\n" \
            "Осталось " + str((counter - i - 1) * cooldown) + " секунд"
        utils.bot.edit_message_text(outstr, idc, idm)

    try:
        inputshiz = utils.translator.translate_text(parent=utils.project_name,
                                                     contents=[inputshiz], target_language_code=endlang,
                                                     mime_type="text/plain").translations[0].translated_text
    except Exception as e:
        if str(e) in "invalid destination language":
            endlang = utils.extract_lang(utils.textparser(message))
            inputshiz = utils.translator.translate_text(parent=utils.project_name,
                                                        contents=[inputshiz], target_language_code=endlang,
                                                        mime_type="text/plain").translations[0].translated_text

    utils.bot.edit_message_text(inputshiz + "\n\nИспользовались искажения: " + randlangs, idc, idm)
