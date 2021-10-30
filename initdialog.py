import configparser
import sys
import traceback

import interlayer
import logger


def init_dialog():
    token = ""
    while token == "":
        token = input("Please, write your bot token: ")

    config = configparser.ConfigParser()
    config.add_section("Polyglot")
    config.set("Polyglot", "token", token)
    config.set("Polyglot", "max-inits", "100")
    config.set("Polyglot", "locales-repository",
               "https://raw.githubusercontent.com/Allnorm/Polyglot/freeapi/locales-list.json")
    config = interlayer.init_dialog_api(config)
    # This is an default configuration of Polyglot bot
    try:
        config.write(open("polyglot.ini", "w"))
        logger.write_log("INFO: New config file was created successful")
    except IOError as e:
        logger.write_log("ERR: Bot cannot write new config file and will close")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        sys.exit(1)
