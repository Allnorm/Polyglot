import importlib

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


trans_api = importlib.import_module("trans_api")


def init_dialog_api(config):

    return trans_api.init_dialog_api(config)


def api_init(config):

    return trans_api.api_init(config)


def translate_init():

    trans_api.translate_init()


def extract_lang(text):

    return trans_api.extract_lang(text)


def list_of_langs():
    global lang_list
    trans_api.list_of_langs()
    lang_list = trans_api.lang_list


def get_translate(input_text: str, target_lang: str, distorting=False, src_lang=None):

    try:
        return trans_api.get_translate(input_text, target_lang, distorting, src_lang)
    except:
        raise
