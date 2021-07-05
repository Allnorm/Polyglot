import sys
import traceback

import logger


def init_dialog():
    token = ""
    while token == "":
        token = input("Please, write your bot token: ")
    key = input("Please, write your secret key for working with log (optional): ")
    keypath = input("Please, write path to your JSON Google API Key (optional, key.json as default): ")
    if keypath == "":
        keypath = "key.json"
    try:
        file = open("polyglot.ini", "w")
        file.write("[Polyglot]\n"
                    "token=" + token + "\n"
                    "key=" + key + "\n"
                    "proxy=\n"
                    "proxy-type=\n"
                    "keypath=" + keypath + "\n"
                    "[Distort]\n"
                    "max-inits=10\n"
                    "attempts=3\n"
                    "cooldown=10")  # This is an default configuration of Polyglot bot
        logger.write_log("INFO: New config file was created successful")
    except IOError as e:
        logger.write_log("ERR: Bot cannot write new config file and will close")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        sys.exit(1)
