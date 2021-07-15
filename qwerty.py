import traceback

import interlayer
import logger
import utils


def qwerty_main(message):

    text = utils.textparser(message)
    if text is None:
        logger.write_log("none", message)
        return

    logger.write_log(text, message)

    arg1, arg2 = utils.extract_arg(message.text, 1), utils.extract_arg(message.text, 2)

    if arg2 is None:
        tab1 = utils.layouts.get(interlayer.extract_lang(text))
        tab2 = utils.layouts.get(arg1)
    else:
        tab1 = utils.layouts.get(arg1)
        tab2 = utils.layouts.get(arg2)

    if tab1 is None and arg2 is None:
        utils.bot.reply_to(message, "Исходный язык не распознан. Неправильный аргумент или неверно распознан язык? (" +
                                    interlayer.get_translate(interlayer.lang_list.get
                                                             (interlayer.extract_lang(text)), "ru") + ")\n"
                                    "Попробуйте указать исходный язык вручную. Возможно, язык отсутствует в "
                                    "словаре символов")
        return

    if tab1 is None or tab2 is None:
        utils.bot.reply_to(message, "Неизвестная раскладка. Возможно, язык отсутствует в словаре символов")
        return

    try:
        translated_text = text.translate(str.maketrans(tab1, tab2))
        utils.bot.reply_to(message, translated_text)
    except Exception as e:
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        utils.bot.reply_to(message, "Ошибка смены раскладки текста. Обратитесь к авторам бота\n"
                                    "Информация для отладки сохранена в логах бота.")
