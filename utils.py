import logging
import os
import traceback

import telebot
import configparser

import initdialog
import locales
import logger
import interlayer

proxy_port = ""
proxy_type = ""
bot: telebot.TeleBot
whitelist = []
enable_auto = True

layouts = {'en': "qwertyuiop[]asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?`~",
           'ru': "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,ёЁ",
           'uk': "йцукенгшщзхїфівапролджєячсмитьбю.ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮ,'₴",
           'be': "йцукенгшўзх'фывапролджэячсмітьбю.ЙЦУКЕНГШЎЗХ'ФЫВАПРОЛДЖЭЯЧСМІТЬБЮ,ёЁ"}

iso = {'ab': 'abk',
       'av': 'ava',
       'ae': 'ave',
       'az': 'aze',
       'ay': 'aym',
       'ak': 'aka',
       'sq': 'sqi',
       'am': 'amh',
       'en': 'eng',
       'ar': 'ara',
       'hy': 'hye',
       'as': 'asm',
       'aa': 'aar',
       'af': 'afr',
       'bm': 'bam',
       'eu': 'eus',
       'ba': 'bak',
       'be': 'bel',
       'bn': 'ben',
       'my': 'mya',
       'bi': 'bis',
       'bg': 'bul',
       'bs': 'bos',
       'br': 'bre',
       'cy': 'cym',
       'hu': 'hun',
       've': 'ven',
       'vo': 'vol',
       'wo': 'wol',
       'vi': 'vie',
       'gl': 'glg',
       'lg': 'lug',
       'hz': 'her',
       'kl': 'kal',
       'el': 'ell',
       'ka': 'kat',
       'gn': 'grn',
       'gu': 'guj',
       'gd': 'gla',
       'da': 'dan',
       'dz': 'dzo',
       'dv': 'div',
       'zu': 'zul',
       'he': 'heb',
       'ig': 'ibo',
       'yi': 'yid',
       'id': 'ind',
       'ia': 'ina',
       'ie': 'ile',
       'iu': 'iku',
       'ik': 'ipk',
       'ga': 'gle',
       'is': 'isl',
       'es': 'spa',
       'it': 'ita',
       'yo': 'yor',
       'kk': 'kaz',
       'kn': 'kan',
       'kr': 'kau',
       'ca': 'cat',
       'ks': 'kas',
       'qu': 'que',
       'ki': 'kik',
       'kj': 'kua',
       'ky': 'kir',
       'zh': 'zho',
       'kv': 'kom',
       'kg': 'kon',
       'ko': 'kor',
       'kw': 'cor',
       'co': 'cos',
       'xh': 'xho',
       'ku': 'kur',
       'km': 'khm',
       'lo': 'lao',
       'la': 'lat',
       'lv': 'lav',
       'ln': 'lin',
       'lt': 'lit',
       'lu': 'lub',
       'lb': 'ltz',
       'mk': 'mkd',
       'mg': 'mlg',
       'ms': 'msa',
       'ml': 'mal',
       'mt': 'mlt',
       'mi': 'mri',
       'mr': 'mar',
       'mh': 'mah',
       'me': 'mer',
       'mo': 'mol',
       'mn': 'mon',
       'gv': 'glv',
       'nv': 'nav',
       'na': 'nau',
       'nd': 'nde',
       'nr': 'nbl',
       'ng': 'ndo',
       'de': 'deu',
       'ne': 'nep',
       'nl': 'nld',
       'no': 'nor',
       'ny': 'nya',
       'nn': 'nno',
       'oj': 'oji',
       'oc': 'oci',
       'or': 'ori',
       'om': 'orm',
       'os': 'oss',
       'pi': 'pli',
       'pa': 'pan',
       'fa': 'fas',
       'pl': 'pol',
       'pt': 'por',
       'ps': 'pus',
       'rm': 'roh',
       'rw': 'kin',
       'ro': 'ron',
       'rn': 'run',
       'ru': 'rus',
       'sm': 'smo',
       'sg': 'sag',
       'sa': 'san',
       'sc': 'srd',
       'ss': 'ssw',
       'sr': 'srp',
       'si': 'sin',
       'sd': 'snd',
       'sk': 'slk',
       'sl': 'slv',
       'so': 'som',
       'st': 'sot',
       'sw': 'swa',
       'su': 'sun',
       'tl': 'tgl',
       'tg': 'tgk',
       'th': 'tha',
       'ty': 'tah',
       'ta': 'tam',
       'tt': 'tat',
       'tw': 'twi',
       'te': 'tel',
       'bo': 'bod',
       'ti': 'tir',
       'to': 'ton',
       'tn': 'tsn',
       'ts': 'tso',
       'tr': 'tur',
       'tk': 'tuk',
       'uz': 'uzb',
       'ug': 'uig',
       'uk': 'ukr',
       'ur': 'urd',
       'fo': 'fao',
       'fj': 'fij',
       'fl': 'fil',
       'fi': 'fin',
       'fr': 'fra',
       'fy': 'fry',
       'ff': 'ful',
       'ha': 'hau',
       'hi': 'hin',
       'ho': 'hmo',
       'hr': 'hrv',
       'cu': 'chu',
       'ch': 'cha',
       'ce': 'che',
       'cs': 'ces',
       'za': 'zha',
       'cv': 'chv',
       'sv': 'swe',
       'sn': 'sna',
       'ee': 'ewe',
       'eo': 'epo',
       'et': 'est',
       'jv': 'jav',
       'ja': 'jpn'}


def config_init():
    global proxy_port, proxy_type, bot, enable_auto

    if not os.path.isfile("polyglot.ini"):
        logging.warning("config file isn't created, trying to create it now")
        print("Hello, mr. new user!")
        initdialog.init_dialog()

    config = configparser.ConfigParser()

    while True:
        try:
            config.read("polyglot.ini")
            token = config["Polyglot"]["token"]
            if token == "":
                raise ValueError("Token is unknown!")
            config = interlayer.api_init(config)
            break
        except Exception as e:
            logging.error(str(e) + "\n" + traceback.format_exc())
            logging.error("incorrect config file! Trying to remake!")
            initdialog.init_dialog()

    try:
        enable_auto_set = config["Polyglot"]["enable-auto"].lower()
    except KeyError:
        logging.error("incorrect enable-auto configuration, auto translate will be available by default\n"
                      + traceback.format_exc())
        enable_auto_set = "true"
    if enable_auto_set == "true":
        pass
    elif enable_auto_set == "false":
        enable_auto = False
    else:
        logging.error("incorrect enable-auto configuration, auto translate will be available by default")

    bot = telebot.TeleBot(token)

    return config


def textparser(message):
    if message.reply_to_message is None:
        bot.reply_to(message, locales.get_text(message.chat.id, "pleaseAnswer"))
        return

    if message.reply_to_message.text is not None:
        inputtext = message.reply_to_message.text
    elif message.reply_to_message.caption is not None:
        inputtext = message.reply_to_message.caption
    elif hasattr(message.reply_to_message, 'poll'):
        inputtext = message.reply_to_message.poll.question + "\n\n"
        for option in message.reply_to_message.poll.options:
            inputtext += "☑️ " + option.text + "\n"
    else:
        bot.reply_to(message, locales.get_text(message.chat.id, "textNotFound"))
        return

    return inputtext


def extract_arg(text, num):
    try:
        return text.split()[num]
    except IndexError:
        pass


def download_clear_log(message, down_clear_check):
    if user_admin_checker(message) is False:
        return

    if down_clear_check:
        try:
            f = open(logger.current_log, 'r', encoding="utf-8")
            bot.send_document(message.chat.id, f)
            f.close()
            logging.info("log was downloaded successful by " + logger.username_parser(message))
        except FileNotFoundError:
            logging.info("user " + logger.username_parser(message)
                         + " tried to download empty log\n" + traceback.format_exc())
            bot.send_message(message.chat.id, locales.get_text(message.chat.id, "logNotFound"))
        except IOError:
            logging.error("user " + logger.username_parser(message) +
                          " tried to download log, but something went wrong!\n" + traceback.format_exc())
            bot.send_message(message.chat.id, locales.get_text(message.chat.id, "logUploadError"))
    else:
        if logger.clear_log():
            logging.info("log was cleared by user " + logger.username_parser(message) + ". Have fun!")
            bot.send_message(message.chat.id, locales.get_text(message.chat.id, "logClearSuccess"))
        else:
            logging.error("user " + logger.username_parser(message) +
                          " tried to clear log, but something went wrong\n!")
            bot.send_message(message.chat.id, locales.get_text(message.chat.id, "logClearError"))


def list_of_langs():
    output = "List of all codes and their corresponding languages:\n"
    interlayer.list_of_langs()
    for key, value in interlayer.lang_list.items():
        output = output + value + " - " + key + "\n"

    output = output + "\nList of all available keyboard layouts: "

    for key, value in layouts.items():
        output = output + key + " "

    try:
        file = open("langlist.txt", "w")
        file.write(output)
        file.close()
        logging.info("langlist updated successful")
    except Exception as e:
        logging.error("langlist file isn't available")
        logging.error(str(e) + "\n" + traceback.format_exc())


def lang_autocorr(langstr, inline=False):
    if inline is False:
        langstr = langstr.lower()
        for key, value in interlayer.lang_list.items():
            langstr = langstr.replace(value.lower(), key)
    elif (extract_arg(langstr, 1)) is not None and inline is True:
        for key, value in interlayer.lang_list.items():
            if (extract_arg(langstr, 0) + " " + extract_arg(langstr, 1)).lower() == value.lower():
                args = extract_arg(langstr, 0) + " " + extract_arg(langstr, 1)
                langstr = langstr.replace(args, args.lower(), 1)
                langstr = langstr.replace(value.lower(), key, 1)
                break
            elif (extract_arg(langstr, 0)).lower() == value.lower():
                args = extract_arg(langstr, 0)
                langstr = langstr.replace(args, args.lower(), 1)
                langstr = langstr.replace(value.lower(), key, 1)
                break

    return langstr


def whitelist_init():
    global whitelist

    try:
        file = open("whitelist.txt", 'r', encoding="utf-8")
        whitelist = file.readlines()
    except FileNotFoundError:
        logging.warning("file \"whitelist.txt\" not found. Working without admin privileges.")
        return
    except IOError:
        logging.error("file \"whitelist.txt\" isn't readable. Working without admin privileges.")
        return
    if not whitelist:
        logging.warning("whitelist is empty. Working without admin privileges.")


def user_admin_checker(message):
    global whitelist

    for checker in whitelist:
        if "@" + str(message.from_user.username) == checker.rstrip("\n") or \
                str(message.from_user.id) == checker.rstrip("\n"):
            return True

    return False
