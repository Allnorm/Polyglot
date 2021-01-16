import os
import traceback
import datetime

from utils import extract_arg, bot

BLOB_TEXT = "not_needed"
current_log = "googator.log"
key = ""

def write_log(text = BLOB_TEXT, message = None):

    if message != None:
        log = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " LOG: user " + str(message.from_user.username) + " sent a command " + str(message.text) + \
            ". Reply message: " + text
    else: log = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " " + text

    if key != "": log = log.replace(key, "###SECRET KEY###")

    print(log)

    if not os.path.isfile(current_log):
        try:
            f = open(current_log, 'w')
            f.close()
        except Exception as e:
            print("ERR: File " + current_log + " is not writable!")
            traceback.print_exc()
            return

    try:
        f = open(current_log, 'a')
        f.write(log + "\n")
        f.close()
    except Exception as e:
        print("ERR: File " + current_log + " is not writable!")
        traceback.print_exc()
        return


def clear_log():

    if os.path.isfile(current_log):
        try:
            os.remove(current_log)
            write_log("INFO: log was cleared successful")
        except Exception as e:
            write_log("ERR: File " + current_log + " wasn't removed")
            traceback.print_exc()
            return False

    return True

def download_clear_log(message, down_clear_check):

    if extract_arg(message.text, 1) != key and key != "":
        bot.reply_to(message, "Неверный ключ доступа")
        return

    if down_clear_check:
        try:
            f = open(current_log, "rb")
            bot.send_document(message.chat.id, f)
        except FileNotFoundError:
            bot.send_message(message.chat.id, "Лог-файл не найден!")
        except Exception:
            bot.send_message(message.chat.id, "Ошибка выгрузки лога!")
            traceback.print_exc()
    else:
        if clear_log():
            bot.send_message(message.chat.id, "Очистка лога успешна")
        else:
            bot.send_message(message.chat.id, "Ошибка очистки лога")


def key_reader():

    global key
    try:
        file = open("key", 'r')
        key = file.read()
        file.close()
    except FileNotFoundError as e:
        write_log("ERR: Key file isn't found! Unsafe log download/clear!")
    except Exception as e:
        write_log("ERR: Key file isn't readable! Unsafe log download/clear!")
        traceback.print_exc()