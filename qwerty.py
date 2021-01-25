import traceback

from logger import write_log, BLOB_TEXT
from utils import extract_arg, extract_lang, textparser, bot, layouts
from googletrans import LANGUAGES


def qwerty_main(message):

    text = textparser(message)
    if text == None:
        write_log("none", message)
        return

    write_log(text, message)

    arg1, arg2 = extract_arg(message.text, 1), extract_arg(message.text, 2)

    if arg2 == None:
        tab1 = layouts.get(extract_lang(text))
        tab2 = layouts.get(arg1)
    else:
        tab1 = layouts.get(arg1)
        tab2 = layouts.get(arg2)

    if tab1 == None and arg2 == None:
        bot.reply_to(message, "Исходный язык не распознан. Неправильный аргумент или неверно распознан "
                                "язык? (" + LANGUAGES.get(extract_lang(text)) + ")\n"
                                "Попробуйте указать исходный язык вручную. Возможно, язык отсутствует в "
                                "словаре символов")
        return

    if tab1 == None or tab2 == None:
        bot.reply_to(message, "Неизвестная раскладка. Возможно, язык отсутствует в словаре символов")
        return

    try:
        translated_text = text.translate(str.maketrans(tab1, tab2))
        bot.reply_to(message, translated_text)
    except Exception as e:
        traceback.print_exc()
        write_log("ERR: " + str(e))
        bot.reply_to(message, "Неизвестная ошибка!")
