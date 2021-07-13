import json
import os
import sys
import threading
import time
import traceback

from google.cloud import translate

import logger

json_key = ""
project_name = ""

layouts = {'en': "qwertyuiop[]asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?`~",
           'ru': "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,ёЁ",
           'uk': "йцукенгшщзхїфівапролджєячсмитьбю.ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮ,'₴",
           'be': "йцукенгшўзх'фывапролджэячсмітьбю.ЙЦУКЕНГШЎЗХ'ФЫВАПРОЛДЖЭЯЧСМІТЬБЮ,ёЁ"}


class BadTrgLangException(Exception):
    pass


class TooManyRequestException(Exception):
    pass


def init_dialog_api(config):
    keypath = input("Please, write path to your JSON Google API Key (optional, key.json as default): ")
    if keypath == "":
        keypath = "key.json"
    config.set("Polyglot", "keypath", keypath)
    return config


def api_init(config):
    global project_name, json_key
    try:
        json_key = config["Polyglot"]["keypath"]
    except:
        raise

    if not os.path.isfile(json_key):
        logger.write_log("ERR: JSON file wasn't found! Bot will close!")
        sys.exit(1)
    try:
        project_name = "projects/" + json.load(open(json_key, 'r')).get("project_id")
    except Exception as e:
        logger.write_log("ERR: Project name isn't readable from JSON! Bot will close!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        sys.exit(1)

    return


def translate_init():
    global translator
    try:
        translator = translate.TranslationServiceClient.from_service_account_json(json_key)
    except Exception as e:
        logger.write_log("ERR: Translator object wasn't created successful! Bot will close! "
                         "Please check your JSON key or Google Cloud settings.")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        sys.exit(1)


def extract_lang(text):
    return translator.detect_language(parent=project_name, content=text).languages[0].language_code


def lang_frozen_checker():
    time.sleep(15)
    if lang_frozen is True:
        logger.write_log("ERR: langlist-gen timed out! Please check your JSON key or Google Cloud settings!")
        os._exit(1)


def list_of_langs():
    global langlist, lang_frozen
    threading.Thread(target=lang_frozen_checker).start()
    output = "Список всех кодов и соответствующих им языков:\n"
    langlist = translator.get_supported_languages(parent=project_name, display_language_code="en")
    lang_frozen = False
    for lang in langlist.languages:
        output = output + lang.display_name + " - " + lang.language_code + "\n"

    output = output + "\nСписок всех доступных раскладок клавиатуры: "

    for key, value in layouts.items():
        output = output + key + " "

    try:
        file = open("langlist.txt", "w")
        file.write(output)
        file.close()
        logger.write_log("INFO: langlist updated successful")
    except Exception as e:
        logger.write_log("ERR: langlist file isn't available")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())


def get_translate(input_text: str, target_lang: str, distorting=False, src_lang=None):
    try:
        return translator.translate_text(parent=project_name, contents=[input_text], target_language_code=target_lang,
                                    mime_type="text/plain").translations[0].translated_text
    except Exception as e:
        if str(e) in "400 Target language is invalid.":
            raise BadTrgLangException
        else:
            logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
            raise
