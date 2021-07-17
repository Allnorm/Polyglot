import json
import os
import sys
import threading
import traceback

from google.cloud import translate

import logger

json_key = ""
project_name = ""
translator: translate.TranslationServiceClient
lang_list = {}


class BadTrgLangException(Exception):
    pass


class TooManyRequestException(Exception):
    pass


class EqalLangsException(Exception):
    pass


class BadSrcLangException(Exception):
    pass


class TooLongMsg(Exception):
    pass


class UnkTransException(Exception):
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
    except KeyError:
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

    return config


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


def list_of_langs():

    global lang_list
    que = []
    lang_buffer: translate.SupportedLanguages
    lang_check = threading.Thread(target=lambda queue: queue.append(translator.get_supported_languages
                                  (parent=project_name, display_language_code="en")), args=(que,), daemon=True)
    lang_check.start()
    lang_check.join(15)
    if lang_check.is_alive():
        logger.write_log("ERR: langlist-gen timed out! Please check your JSON key or Google Cloud settings!")
        sys.exit(1)

    lang_buffer = que.pop(0)
    for lang in lang_buffer.languages:
        lang_list.update({lang.language_code: lang.display_name})


def get_translate(input_text: str, target_lang: str, distorting=False, src_lang=None):
    try:
        trans_result = translator.translate_text(parent=project_name, contents=[input_text], target_language_code=target_lang,
                                         source_language_code=src_lang,
                                         mime_type="text/plain").translations[0].translated_text
    except Exception as e:
        if str(e) in "400 Target language is invalid.":
            raise BadTrgLangException
        if str(e) in "400 Target language can't be equal to source language.":
            return "Невозможно сделать перевод с языка на тот же язык"
        if str(e) in "400 Source language is invalid.":
            raise BadSrcLangException
        else:
            logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
            raise UnkTransException

    if len(trans_result) > 4096:
        raise TooLongMsg

    return trans_result
