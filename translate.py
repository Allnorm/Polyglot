import traceback

from logger import write_log, BLOB_TEXT
from utils import extract_arg, textparser, bot, translator


def translate_main(message):

    lang = extract_arg(message.text, 1)
    if extract_arg(message.text, 2) != None:
        lang = lang + " " + extract_arg(message.text, 2)

    inputtext = textparser(message)
    if inputtext == None:
        write_log("none", message)
        return

    write_log(inputtext, message)

    if lang == None:
        bot.reply_to(message, "Укажите код языка/название страны")
        return

    try:
        translated = translator.translate(inputtext, lang).text
        if translated == inputtext:
            bot.reply_to(message, "Исходный и итоговый текст совпадают. Возможно, Google Api отклонил запрос. "
                                  "Если вы уверены, что так быть не должно, повторите попытку позже")
            return
        bot.reply_to(message, translated)

    except Exception as e:
        if str(e) in "invalid destination language":
            bot.reply_to(message, "Указан неверный код языка/название страны")
        else:
            bot.reply_to(message, "Ошибка: " + str(e) + ".\n"
                "Сообщите администратору.\nСодержимое переменной inputtext: " + str(inputtext))
            write_log("ERR: " + str(e))
            traceback.print_exc()
