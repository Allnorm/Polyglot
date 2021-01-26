import random
import time
import traceback

import logger
import utils

from googletrans import LANGUAGES

ATTEMPTS = 1000
COOLDOWN = 10

def distort_main(message):

    inputshiz = utils.textparser(message)
    if inputshiz is None:
        logger.write_log("none", message)
        return

    logger.write_log(inputshiz, message)

    try:
        counter = int(utils.extract_arg(message.text, 1))
    except ValueError:
        utils.bot.reply_to(message, "Ошибка, число не распознано")
        return
    except TypeError:
        utils.bot.reply_to(message, "Ошибка, число не распознано")
        return

    if counter > 100 or counter < 1:
        utils.bot.reply_to(message, "Ошибка, укажите значение от 1 до 100")
        return

    randlangs = ""

    if utils.extract_arg(message.text, 2) != None and utils.extract_arg(message.text, 3) != None:
        endlang = utils.extract_arg(message.text, 2) + " " + utils.extract_arg(message.text, 3)
    elif utils.extract_arg(message.text, 2) != None:
        endlang = utils.extract_arg(message.text, 2)
    else:
        endlang = utils.extract_lang(inputshiz)

    tmpmessage = utils.bot.reply_to(message, "Генерация начата, осталось " + str(counter * COOLDOWN) + " секунд")
    idc = tmpmessage.chat.id
    idm = tmpmessage.message_id

    for i in range(counter):
        randlang = random.choice(list(LANGUAGES))

        randlangs += randlang + "; "

        for iteration in range(ATTEMPTS):  # three tries
            inputshizchecker = inputshiz

            try:
                inputshiz = utils.translator.translate(inputshiz, randlang).text
                if inputshizchecker != inputshiz: break

            except Exception as e:
                if str(e) in "invalid destination language":
                    pass
                else:
                    utils.bot.edit_message_text("Ошибка: " + str(e) + ".\n"
                        "Сообщите администратору.\nСодержимое переменной inputtext: " + str(inputshiz), idc, idm)
                    logger.write_log("ERR: " + str(e))
                    traceback.print_exc()
                    return

            if iteration == ATTEMPTS:
                utils.bot.edit_message_text("Неизвестная ошибка перевода. Повторите попытку позже.\n"
                    "Возможно, запрос был заблокирован Google Api", idc, idm)
                return

        time.sleep(COOLDOWN)

        outstr = "Готова итерация " + str(i + 1) + "/" + str(counter) + "\n" \
            "Осталось " + str((counter - i - 1) * COOLDOWN) + " секунд"
        utils.bot.edit_message_text(outstr, idc, idm)

    try:
        inputshiz = utils.translator.translate(inputshiz, endlang).text
    except Exception as e:
        if str(e) in "invalid destination language":
            endlang = utils.extract_lang(utils.textparser(message))
            inputshiz = utils.translator.translate(inputshiz, endlang).text

    utils.bot.edit_message_text(inputshiz + "\n\nИспользовались искажения: " + randlangs, idc, idm)