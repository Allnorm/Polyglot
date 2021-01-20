import random
import time
import traceback

from googletrans import LANGUAGES

from logger import write_log, BLOB_TEXT
from utils import textparser, extract_arg, bot, extract_lang, translator


def distort_main(message):

    cooldown = 10

    inputshiz = textparser(message)
    if inputshiz == None:
        write_log("none", message)
        return

    write_log(inputshiz, message)

    try:
        counter = int(extract_arg(message.text, 1))
    except ValueError:
        bot.reply_to(message, "Ошибка, число не распознано")
        return
    except TypeError:
        bot.reply_to(message, "Ошибка, число не распознано")
        return

    if counter > 100 or counter < 1:
        bot.reply_to(message, "Ошибка, укажите значение от 1 до 100")
        return

    randlangs = ""

    if extract_arg(message.text, 2) != None and extract_arg(message.text, 3) != None:
        endlang = extract_arg(message.text, 2) + " " + extract_arg(message.text, 3)
    elif extract_arg(message.text, 2) != None:
        endlang = extract_arg(message.text, 2)
    else:
        endlang = extract_lang(inputshiz)

    tmpmessage = bot.reply_to(message, "Генерация начата, осталось " + str(counter * cooldown) + " секунд")
    idc = tmpmessage.chat.id
    idm = tmpmessage.message_id

    for i in range(counter):
        randlang = random.choice(list(LANGUAGES))

        randlangs += randlang + "; "

        for iteration in range(2):
            inputshizchecker = inputshiz
            try:
                inputshiz = translator.translate(inputshiz, randlang).text
                break
            except Exception as e:
                if str(e) in "invalid destination language":
                    pass
                else:
                    bot.edit_message_text("Ошибка: " + str(e) + ".\n"
                        "Сообщите администратору.\nСодержимое переменной inputtext: " + str(inputshiz), idc, idm)
                    write_log("ERR: " + str(e) +"\n")
                    traceback.print_exc()

            if iteration == 2:
                bot.edit_message_text("Неизвестная ошибка перевода. Повторите попытку позже.\n"
                                      "Содержимое переменной inputtext: " + str(inputshiz), idc, idm)
                return

            if inputshizchecker == inputshiz:
                bot.edit_message_text("Ошибка обращения к Google Api. Сервис отклонил запрос, "
                                      "повторите попытку позже", idc, idm)
                return

        time.sleep(cooldown)

        outstr = "Готова итерация " + str(i + 1) + "/" + str(counter) + "\n" \
            "Осталось " + str((counter - i - 1) * cooldown) + " секунд"
        bot.edit_message_text(outstr, idc, idm)

    try:
        inputshiz = translator.translate(inputshiz, endlang).text
    except Exception as e:
        if str(e) in "invalid destination language":
            endlang = extract_lang(textparser(message))
            inputshiz = translator.translate(inputshiz, endlang).text

    bot.edit_message_text(inputshiz + "\n\nИспользовались искажения: " + randlangs, idc, idm)