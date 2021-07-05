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
        translated = utils.translator.translate_text(parent=utils.project_name,
                                                     contents=[inputtext], target_language_code=lang,
                                                     mime_type="text/plain").translations[0].translated_text
        if translated == inputtext and translate_verify is True:
            logger.write_log("ERR: GOOGLE_API_REJECT")
            utils.bot.reply_to(message, "Исходный и итоговый текст совпадают. Возможно, Google Api отклонил запрос. "
                                        "Если вы уверены, что так быть не должно, повторите попытку позже")
            return

        utils.bot.reply_to(message, translated)

    except Exception as e:
        if str(e) in "400 Target language is invalid.":
            utils.bot.reply_to(message, "Указан неверный код языка/название страны")
        else:
            logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
            utils.bot.reply_to(message, "Ошибка перевода. Обратитесь к авторам бота\n"
                                        "Информация для отладки сохранена в логах бота.")
