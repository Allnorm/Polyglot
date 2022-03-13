import json
import logging
import os
import sys
import traceback

from google.cloud import translate

json_key = ""
project_name = ""
translator: translate.TranslationServiceClient
lang_list = {}
len_limit = 0


class BadTrgLangException(Exception):
    pass


class TooManyRequestException(Exception):
    pass


class EqualLangsException(Exception):
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
    config.set("Polyglot", "len-limit", 0)
    return config


def api_init(config):
    global project_name, json_key, len_limit

    version = "1.0.2 for googleapi 3.6.1"
    build = "1"
    version_polyglot = "1.3 alpha/beta/release"
    build_polyglot = "- any"
    logging.info("Interlayer version {}, build {}".format(version, build))
    logging.info("Compatible with version of Polyglot {}, build {}".format(version_polyglot, build_polyglot))

    try:
        json_key = config["Polyglot"]["keypath"]
    except KeyError:
        raise

    if not os.path.isfile(json_key):
        logging.error("JSON file wasn't found! Bot will close!")
        sys.exit(1)

    try:
        project_name = "projects/" + json.load(open(json_key, 'r')).get("project_id")
    except Exception as e:
        logging.error("Project name isn't readable from JSON! Bot will close!")
        logging.error(str(e) + "\n" + traceback.format_exc())
        sys.exit(1)

    try:
        len_limit = int(config["Polyglot"]["len-limit"])
        if len_limit < 0 or len_limit > 4096:
            len_limit = 0
    except (KeyError, ValueError):
        pass

    return config


def translate_init():
    global translator
    try:
        translator = translate.TranslationServiceClient.from_service_account_json(json_key)
    except Exception as e:
        logging.error("Translator object wasn't created successful! Bot will close! "
                      "Please check your JSON key or Google Cloud settings.")
        logging.error(str(e) + "\n" + traceback.format_exc())
        sys.exit(1)


def extract_lang(text):
    try:
        return translator.detect_language(parent=project_name, content=text, timeout=10).languages[0].language_code
    except Exception as e:
        logging.error(str(e) + "\n" + traceback.format_exc())
        raise UnkTransException


def list_of_langs():
    global lang_list
    lang_buffer = translator.get_supported_languages(parent=project_name, display_language_code="en", timeout=10)
    for lang in lang_buffer.languages:
        lang_list.update({lang.language_code: lang.display_name})


def get_translate(input_text: str, target_lang: str, distorting=False, src_lang=None):
    global len_limit

    if 0 < len_limit < len(input_text):
        raise TooLongMsg

    try:
        trans_result = translator.translate_text(parent=project_name, contents=[input_text],
                                                 target_language_code=target_lang, source_language_code=src_lang,
                                                 mime_type="text/plain", timeout=10).translations[0].translated_text
    except Exception as e:
        if "400 Target language is invalid." in str(e):
            raise BadTrgLangException
        if "400 Target language can't be equal to source language." in str(e):
            raise EqualLangsException
        if "400 Source language is invalid." in str(e):
            raise BadSrcLangException
        else:
            logging.error(str(e) + "\n" + traceback.format_exc())
            raise UnkTransException

    if len(trans_result) > 4096 and distorting is False:
        logging.warning("too long message for sending.")
        raise TooLongMsg

    return trans_result
