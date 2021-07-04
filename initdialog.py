import sys
import traceback

import logger


def init_dialog():
    token = ""
    logger.write_log("WARN: Config file isn't created, trying to create it now")
    while token == "":
        token = input("Hello, mr. new user! Please, write your bot token: ")
    key = input("Please, write your secret key for working with log (optional): ")
    try:
        file = open("polyglot.ini", "w")
        file.write("[Polyglot]\n"
                    "token=" + token + "\n"
                    "key=" + key + "\n"
                    "translate-verify=true\n"
                    "proxy=\n"
                    "proxy-type=\n"
                    "[Distort]\n"
                    "max-inits=10\n"
                    "attempts=3\n"
                    "cooldown=10\n"
                    "[GoogleAPI]\n"
                    "keypath=key.json\n"
                    "projectname=")  # This is an default configuration of Polyglot bot
    except IOError as e:
        logger.write_log("ERR: Bot cannot write new config file and will close")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        sys.exit(1)
