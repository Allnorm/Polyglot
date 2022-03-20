import configparser
import logging
import sys
import traceback

import ad_module
import utils
from locales import LOCALES_REPO_DEFAULT


def init_dialog():
    token = ""
    while token == "":
        token = input("Please, write your bot token: ")

    config = configparser.ConfigParser()
    config.add_section("Polyglot")
    config.set("Polyglot", "token", token)
    config.set("Polyglot", "max-inits", "100")
    config.set("Polyglot", "locales-repository", LOCALES_REPO_DEFAULT)
    config.set("Polyglot", "msg-logging", "true")
    config.set("Polyglot", "enable-auto", "true")
    config.set("Polyglot", "pytesseract", "")
    config = utils.translator.init_dialog_api(config)
    config = ad_module.init_dialog_api(config)
    # This is a default configuration of Polyglot bot
    try:
        config.write(open("polyglot.ini", "w"))
        logging.info("new config file was created successful")
    except IOError as e:
        logging.error("bot cannot write new config file and will close")
        logging.error(str(e) + "\n" + traceback.format_exc())
        sys.exit(1)
