import interlayer
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
        utils.bot.reply_to(message, "Укажите код/название языка на английском")
        return

    try:
        inputtext = interlayer.get_translate(inputtext, lang)
        utils.bot.reply_to(message, inputtext)
    except interlayer.BadTrgLangException:
        utils.bot.reply_to(message, "Указан неверный код/название яыка")
    except Exception:
        utils.bot.reply_to(message, "Ошибка перевода. Обратитесь к авторам бота\n"
                                    "Информация для отладки сохранена в логах бота.")
