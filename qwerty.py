import traceback

import logger
import utils
from googletrans import LANGUAGES


def qwerty_main(message):

    text = utils.textparser(message)
    if text == None:
        logger.write_log("none", message)
        return

    logger.write_log(text, message)

    arg1, arg2 = utils.extract_arg(message.text, 1), utils.extract_arg(message.text, 2)

    if arg2 == None:
        tab1 = utils.layouts.get(utils.extract_lang(text))
        tab2 = utils.layouts.get(arg1)
    else:
        tab1 = utils.layouts.get(arg1)
        tab2 = utils.layouts.get(arg2)

    if tab1 == None and arg2 == None:
        utils.bot.reply_to(message, "Исходный язык не распознан. Неправильный аргумент или неверно распознан "
                                "язык? (" + LANGUAGES.get(utils.extract_lang(text)) + ")\n"
                                "Попробуйте указать исходный язык вручную. Возможно, язык отсутствует в "
                                "словаре символов")
        return

    if tab1 == None or tab2 == None:
        utils.bot.reply_to(message, "Неизвестная раскладка. Возможно, язык отсутствует в словаре символов")
        return

    try:
        translated_text = text.translate(str.maketrans(tab1, tab2))
        utils.bot.reply_to(message, translated_text)
    except Exception as e:
        traceback.print_exc()
        logger.write_log("ERR: " + str(e))
        utils.bot.reply_to(message, "Неизвестная ошибка!")
