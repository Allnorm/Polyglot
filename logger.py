import os
import sys
import traceback
import logging
from importlib import reload

import telebot

BLOB_TEXT = "not_needed"
current_log = "polyglot.log"
logger = True
logger_message = False


def logger_init():
    log_cleared = clear_log()
    reload(logging)
    logging.basicConfig(
        handlers=[
            logging.FileHandler(current_log, 'w', 'utf-8'),
            logging.StreamHandler(sys.stdout)
        ],
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt="%d-%m-%Y %H:%M:%S")

    return log_cleared


def logger_config_init(config):
    global logger, logger_message

    try:
        get_log_set = config["Polyglot"]["msg-logging"].lower()
    except (ValueError, KeyError):
        logging.error("incorrect logging configuration, logging will be work by default\n" + traceback.format_exc())
        return
    if get_log_set == "true":
        return
    elif get_log_set == "false":
        logger = False
        logging.info("user messages logging was disabled")
    elif get_log_set == "debug":
        logger_message = True
        logging.warning("debug mode enabled - the content of messages is logging")
    else:
        logging.error("incorrect logging configuration, logging will be work by default\n" + traceback.format_exc())


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


def write_log(message: telebot.types.Message, text=BLOB_TEXT):
    if logger is False:
        return

    if logger_message is False:
        text = BLOB_TEXT

    logging.info("user " + username_parser(message) + " sent a command " + str(message.text)
                 + ". Reply message: " + text)


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
