import sys
import time
import traceback
import logging

import httpcore
from googletrans import Translator, LANGUAGES

json_key = ""
project_name = ""
translator: Translator
lang_list = {}


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

    return config


def api_init(config):

    version = "1.0.1 for py-googletrans 4.0.0rc1 (freeapi)"
    build = "1"
    version_polyglot = "1.2 alpha/beta/release"
    build_polyglot = "- any"
    logging.info("Interlayer version {}, build {}".format(version, build))
    logging.info("Compatible with version of Polyglot {}, build {}".format(version_polyglot, build_polyglot))

    return config


def translate_init():

    global translator
    try:
        translator = Translator()
    except Exception as e:
        logging.error("translator object wasn't created successful! Bot will close!")
        logging.error(str(e) + "\n" + traceback.format_exc())
        sys.exit(1)


def extract_lang(text):
    try:
        return translator.detect(text).lang.lower()
    except (AttributeError, httpcore._exceptions.ReadError):
        logging.error("GOOGLE_API_REJECT (in lang extract)")
    except Exception as e:
        logging.error(str(e) + "\n" + traceback.format_exc())
    raise UnkTransException


def list_of_langs():
    global lang_list

    lang_list = LANGUAGES


def get_translate(input_text: str, target_lang: str, distorting=False, src_lang=None):
    if src_lang is None:
        src_lang = "auto"
    if target_lang is None:
        raise BadTrgLangException

    try:
        trans_result = translator.translate(input_text, target_lang, src_lang).text
    except (AttributeError, httpcore._exceptions.ReadError):
        if distorting:
            time.sleep(10)
            try:
                trans_result = translator.translate(input_text, target_lang, src_lang).text
            except (AttributeError, httpcore._exceptions.ReadError):
                logging.error("GOOGLE_API_REJECT")
                raise TooManyRequestException
        else:
            logging.error("GOOGLE_API_REJECT")
            raise TooManyRequestException
    except Exception as e:
        if str(e) in "invalid destination language":
            raise BadTrgLangException
        if str(e) in "invalid source language":
            raise BadSrcLangException
        else:
            logging.error(str(e) + "\n" + traceback.format_exc())
            raise UnkTransException

    if len(trans_result) > 4096 and distorting is False:
        logging.warning("too long message for sending.")
        raise TooLongMsg

    return trans_result
