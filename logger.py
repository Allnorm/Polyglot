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
            f = open(current_log, 'w', encoding="utf-8")
            f.close()
        except Exception:
            print("ERR: File " + current_log + " is not writable!")
            traceback.print_exc()
            return

    try:
        f = open(current_log, 'a', encoding="utf-8")
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
