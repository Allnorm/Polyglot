import json
import os
import sys
import traceback

import certifi
import urllib3

import logger
import sql_worker

locale_data: dict
LOCALES_REPO_DEFAULT = "https://raw.githubusercontent.com/Allnorm/Polyglot/newapi/locales-list.json"


def locales_check_integrity(config):
    global locale_data
    if not os.path.isfile("locales-list.json"):
        logger.write_log("WARN: locales-list is empty, trying to download it from repos")
        locales_download_list(config)
    try:
        with open("locales-list.json", "r", encoding='utf-8') as read_file:
            locale_data = json.load(read_file)
    except IOError as e:
        logger.write_log("ERR: impossible to read locales file! Bot will close\n"
                         "Try to remove locales-list.json, it should to download automatically.")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        sys.exit(1)
    except json.decoder.JSONDecodeError as e:
        logger.write_log("ERR: impossible to parse locales file! Bot will close.\n"
                         "Try to remove locales-list.json, it should to download automatically.")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        sys.exit(1)
    logger.write_log("INFO: locales loaded successful")
    sql_worker.table_init()


def locales_download_list(config):
    global LOCALES_REPO_DEFAULT
    try:
        locales_repo = config["Polyglot"]["locales-repository"]
    except KeyError:
        logger.write_log("ERR: incorrect locales-repository configurations, reset to default repo ("
                         + LOCALES_REPO_DEFAULT + ")\n"
                         + traceback.format_exc())
        locales_repo = LOCALES_REPO_DEFAULT

    http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())
    try:
        r = http.request('GET', locales_repo)
        logger.write_log("INFO: locales file downloaded successful from repository " + locales_repo)
    except Exception as e:
        logger.write_log("ERR: impossible to download locales file! Bot will close. "
                         "You can to try download it manually.")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        sys.exit(1)
    if r.status != 200:
        logger.write_log("ERR: impossible to download locales file! You can try download it manually. Bot will close")
        sys.exit(1)
    try:
        f = open('locales-list.json', 'wb')
        f.write(r.data)
    except IOError as e:
        logger.write_log("ERR: impossible to write new locales file! Bot will close")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        sys.exit(1)


def get_text(chat_id, string_name):
    chat_info = sql_worker.get_chat_info(chat_id)
    if not chat_info:
        chat_lang = "en"
    else:
        chat_lang = chat_info[0][1]
    try:
        if locale_data.get(chat_lang).get(string_name) is not None:
            return locale_data.get(chat_lang).get(string_name)
        else:
            raise AttributeError("Key isn't found!")
    except AttributeError as e:
        logger.write_log("ERR: lang parsing failed! Lang code - " + chat_lang)
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        return "Lang parsing failed! Please check bot logs."


def get_text_inline(message, string_name):
    chat_info = sql_worker.get_chat_info("", message.from_user.id)
    if not chat_info:
        lang_code = "en"
    else:
        lang_code = chat_info[0][1]
    try:
        if locale_data.get(lang_code).get(string_name) is not None:
            return locale_data.get(lang_code).get(string_name)
        else:
            raise AttributeError("Key isn't found!")
    except AttributeError as e:
        logger.write_log("ERR: lang parsing failed! (inline). Lang code - " + lang_code)
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        return "LOCALE_ERR"


def get_chat_lang(chat_id):
    chat_info = sql_worker.get_chat_info(chat_id)
    if not chat_info:
        return "en"
    else:
        return chat_info[0][1]