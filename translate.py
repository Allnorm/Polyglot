import traceback

import logger
import utils

translate_verify = True


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
        translated = utils.syms2spaces(utils.translator.translate(utils.spaces2syms(inputtext), lang).text)
        # A workaround before fixing by Google. Remove as soon as possible
        # translated = utils.translator.translate(inputtext, lang).text
        if translated == inputtext and translate_verify is True:
            logger.write_log("ERR: GOOGLE_API_REJECT")
            utils.bot.reply_to(message, "Исходный и итоговый текст совпадают. Возможно, Google Api отклонил запрос. "
                                        "Если вы уверены, что так быть не должно, повторите попытку позже")
            return
        utils.bot.reply_to(message, translated)

    except Exception as e:
        if str(e) in "invalid destination language":
            utils.bot.reply_to(message, "Указан неверный код языка/название страны")
        else:
            logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
            utils.bot.reply_to(message, "Ошибка перевода. Обратитесь к авторам бота\n"
                                        "Информация для отладки сохранена в логах бота.")
