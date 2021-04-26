import traceback

import logger
import utils


def translate_main(message):

    lang = utils.extract_arg(message.text, 1)
    if utils.extract_arg(message.text, 2) is not None:
        lang = lang + " " + utils.extract_arg(message.text, 2)

    inputtext = utils.textparser(message)
    if inputtext is None:
        logger.write_log("none", message)
        return

    logger.write_log(inputtext, message)

    if lang is None:
        utils.bot.reply_to(message, "Укажите код языка/название страны")
        return

    try:
        translated = utils.translator.translate(inputtext, lang).text
        if translated == inputtext:
            utils.bot.reply_to(message, "Исходный и итоговый текст совпадают. Возможно, Google Api отклонил запрос. "
                                        "Если вы уверены, что так быть не должно, повторите попытку позже")
            return
        utils.bot.reply_to(message, translated)

    except Exception as e:
        if str(e) in "invalid destination language":
            utils.bot.reply_to(message, "Указан неверный код языка/название страны")
        else:
            utils.bot.reply_to(message, "Ошибка: " + str(e) + ".\n"
                                        "Сообщите администратору.\nСодержимое переменной inputtext: " + str(inputtext))
            logger.write_log("ERR: " + str(e))
            traceback.print_exc()
