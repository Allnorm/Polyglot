import os
import traceback
import datetime

BLOB_TEXT = "not_needed"
current_log = "polyglot.log"
key = ""


def username_parser(message):
    if message.from_user.username is None:
        if message.from_user.last_name is None:
            username = str(message.from_user.first_name)
        else:
            username = str(message.from_user.first_name) + " " + str(message.from_user.last_name)
    else:
        if message.from_user.last_name is None:
            username = str(message.from_user.first_name) + " (@" + str(message.from_user.username) + ")"
        else:
            username = str(message.from_user.first_name) + " " + str(message.from_user.last_name) + \
                       " (@" + str(message.from_user.username) + ")"

    return username


def write_log(text=BLOB_TEXT, message=None):
    if message is not None:
        log = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " LOG: user " + username_parser(message) + \
              " sent a command " + str(message.text) + \
              ". Reply message: " + text
    else:
        log = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " " + text

    if key != "":
        log = log.replace(key, "###SECRET KEY###")

    print(log)

    if not os.path.isfile(current_log):
        try:
            f = open(current_log, 'w')
            f.close()
        except Exception:
            print("ERR: File " + current_log + " is not writable!")
            traceback.print_exc()
            return

    try:
        f = open(current_log, 'a')
        f.write(log + "\n")
        f.close()
    except Exception:
        print("ERR: File " + current_log + " is not writable!")
        traceback.print_exc()
        return


def clear_log():
    if os.path.isfile(current_log):
        try:
            os.remove(current_log)
            write_log("INFO: log was cleared successful")
        except Exception:
            write_log("ERR: File " + current_log + " wasn't removed\n" + traceback.format_exc())
            return False

    return True


def download_clear_log(message, down_clear_check):
    import utils
    if utils.extract_arg(message.text, 1) != key and key != "":
        utils.bot.reply_to(message, "Неверный ключ доступа")
        return

    if down_clear_check:
        try:
            f = open(current_log, 'r')
            utils.bot.send_document(message.chat.id, f)
            f.close()
            write_log("INFO: log was downloaded successful by " + username_parser(message))
        except FileNotFoundError:
            write_log("INFO: user " + username_parser(message)
                      + " tried to download empty log\n" + traceback.format_exc())
            utils.bot.send_message(message.chat.id, "Лог-файл не найден!")
        except Exception:
            write_log("ERR: user " + username_parser(message) +
                      " tried to download log, but something went wrong!\n" + traceback.format_exc())
            utils.bot.send_message(message.chat.id, "Ошибка выгрузки лога!")
    else:
        if clear_log():
            write_log("INFO: log was cleared by user " + username_parser(message) + ". Have fun!")
            utils.bot.send_message(message.chat.id, "Очистка лога успешна")
        else:
            write_log("ERR: user " + username_parser(message) +
                      " tried to clear log, but something went wrong\n!")
            utils.bot.send_message(message.chat.id, "Ошибка очистки лога")
