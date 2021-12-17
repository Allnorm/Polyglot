import os
import traceback
import datetime

BLOB_TEXT = "not_needed"
current_log = "polyglot.log"
logger = True
logger_message = False


def logger_init(config):
    global logger, logger_message
    try:
        get_log_set = config["Polyglot"]["msg-logging"].lower()
    except (ValueError, KeyError):
        write_log("ERR: incorrect logging configuration, logging will be work by default\n" + traceback.format_exc())
        return
    if get_log_set == "true":
        return
    elif get_log_set == "false":
        logger = False
        write_log("INFO: user messages logging was disabled")
    elif get_log_set == "debug":
        logger_message = True
        write_log("WARN: debug mode enabled - the content of messages is logging")
    else:
        write_log("ERR: incorrect logging configuration, logging will be work by default\n" + traceback.format_exc())


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

    if logger is False and message is not None:
        return

    if logger_message is False and message is not None:
        text = BLOB_TEXT

    if message is not None:
        log = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " LOG: user " + username_parser(message) + \
              " sent a command " + str(message.text) + \
              ". Reply message: " + text
    else:
        log = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " " + text

    print(log)

    if not os.path.isfile(current_log):
        try:
            f = open(current_log, 'w', encoding="utf-8")
            f.close()
        except Exception as e:
            print("ERR: file " + current_log + " is not writable!")
            print(e)
            traceback.print_exc()
            return

    try:
        f = open(current_log, 'a', encoding="utf-8")
        f.write(log + "\n")
        f.close()
    except Exception as e:
        print("ERR: file " + current_log + " is not writable!")
        print(e)
        traceback.print_exc()
        return


def clear_log():

    if os.path.isfile(current_log):
        try:
            os.remove(current_log)
        except Exception as e:
            print("ERR: file " + current_log + " wasn't removed")
            print(e)
            traceback.print_exc()
            return False

    return True
