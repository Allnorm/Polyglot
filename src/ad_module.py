import datetime
import logging
import random
import time
import traceback

import locales
import sql_worker
import utils

enable_ad = True
ad_percent = 50


def init_dialog_api(config):
    config.set("Polyglot", "enable-ad", "true")
    config.set("Polyglot", "ad-percent", "50")
    return config


def ad_module_init(config):
    global enable_ad, ad_percent

    try:
        enable_ad_set = config["Polyglot"]["enable-ad"].lower()
    except KeyError:
        logging.error("incorrect enable-ad configuration, ad module will be work by default\n"
                      + traceback.format_exc())
        enable_ad_set = "true"
    if enable_ad_set == "true":
        pass
    elif enable_ad_set == "false":
        enable_ad = False
    else:
        logging.error("incorrect enable-ad configuration, ad module will be work by default")

    try:
        ad_percent = int(config["Polyglot"]["ad-percent"])
    except (ValueError, KeyError):
        logging.error("incorrect ad-percent configuration, reset to default (50%)\n"
                      + traceback.format_exc())
    if ad_percent < 0 or ad_percent > 100:
        logging.error("incorrect ad-percent value, reset to default (50%). Should to be in range 0-100%")


def status_premium(message):
    if not enable_ad:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "adDisabled"))
        return

    chat_user_id = message.chat.id
    is_user = False

    if message.reply_to_message is not None:
        chat_user_id = message.reply_to_message.from_user.id
        is_user = True

    sql_worker.actualize_chat_premium(chat_user_id)
    current_chat = sql_worker.get_chat_info(chat_user_id)
    if not current_chat:
        try:
            sql_worker.write_chat_info(chat_user_id, "premium", "no")
        except sql_worker.SQLWriteError:
            utils.bot.reply_to(message, locales.get_text(chat_user_id, "premiumError"))
            return
        current_chat = sql_worker.get_chat_info(chat_user_id)

    if utils.extract_arg(message.text, 1) == "force":
        # Usage: /premium force [time_in_hours (optional argument)]
        force_premium(message, current_chat, is_user)
        return

    added_text = locales.get_text(message.chat.id, "premiumChat")
    if is_user or message.chat.type == "private":
        added_text = locales.get_text(message.chat.id, "premiumUser")

    if current_chat[0][3] == "no":
        premium_status = locales.get_text(message.chat.id, "premiumStatusDisabled")
    else:
        if current_chat[0][4] != 0:
            premium_status = locales.get_text(message.chat.id, "premiumStatusTime") + " " + \
                             datetime.datetime.fromtimestamp(current_chat[0][4]).strftime("%d.%m.%Y %H:%M:%S")
        else:
            premium_status = locales.get_text(message.chat.id, "premiumStatusInfinity")

    utils.bot.reply_to(message, locales.get_text(message.chat.id, "premiumStatus").format(added_text)
                       + " <b>" + premium_status + "</b>", parse_mode="html")


def force_premium(message, current_chat, is_user):

    if utils.user_admin_checker(message) is False:
        return

    added_text = locales.get_text(message.chat.id, "premiumChat")
    if is_user or message.chat.type == "private":
        added_text = locales.get_text(message.chat.id, "premiumUser")

    if current_chat[0][3] == "no":
        timer = "0"
        if utils.extract_arg(message.text, 2) is not None:
            try:
                timer = str(int(time.time()) + int(utils.extract_arg(message.text, 2)) * 86400)
            except ValueError:
                utils.bot.reply_to(message, locales.get_text(message.chat.id, "parseTimeError"))
                return
        try:
            sql_worker.write_chat_info(current_chat[0][0], "premium", "yes")
            sql_worker.write_chat_info(current_chat[0][0], "expire_time", timer)
        except sql_worker.SQLWriteError:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "premiumError"))
            return
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "forcePremium").format(added_text))
    else:
        try:
            sql_worker.write_chat_info(current_chat[0][0], "premium", "no")
            sql_worker.write_chat_info(current_chat[0][0], "expire_time", "0")
        except sql_worker.SQLWriteError:
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "premiumError"))
            return
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "forceUnPremium").format(added_text))


def module_add_task(message):
    if utils.user_admin_checker(message) is False:
        return

    if not enable_ad:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "adDisabled"))
        return

    text = utils.textparser(message)
    if text is None:
        return

    if utils.extract_arg(message.text, 1) is None or utils.extract_arg(message.text, 2) is None:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "taskerArguments"))
        return

    try:
        expire_time = int(time.time()) + int(utils.extract_arg(message.text, 2)) * 86400
    except (TypeError, ValueError):
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "taskerArguments"))
        return

    lang_code = utils.extract_arg(message.text, 1)

    if sql_worker.write_task(message.reply_to_message.id, text, lang_code, expire_time, message.chat.id) is False:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "taskerFail"))
    else:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "taskerSuccess").
                           format(lang_code,
                                  datetime.datetime.fromtimestamp(expire_time).strftime("%d.%m.%Y %H:%M:%S")))


def module_rem_task(message):
    if utils.user_admin_checker(message) is False:
        return

    if not enable_ad:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "adDisabled"))
        return

    text = utils.textparser(message)
    if text is None:
        return

    try:
        sql_worker.rem_task(message.reply_to_message.id, message.chat.id)
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "taskerRemSuccess"))
    except sql_worker.SQLWriteError:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "taskerRemError"))


def add_ad(chat_id, user_id=None):
    if enable_ad is False:
        return ""
    lang_chat_code = "en"

    if user_id is None:
        chat_info = sql_worker.get_chat_info(chat_id)
    else:
        chat_info = sql_worker.get_chat_info(user_id)

    if chat_info:
        if chat_info[0][3] == "yes":
            return ""  # Return for premium
        lang_chat_code = chat_info[0][1]
    list_ad = sql_worker.get_tasks(lang_chat_code)
    if not list_ad:
        return ""
    for current_ad in list_ad:
        if int(current_ad[3]) < int(time.time()):
            try:
                sql_worker.rem_task(current_ad[0], current_ad[4])
            except sql_worker.SQLWriteError:
                pass
    percent = random.randint(1, 100)
    if percent > ad_percent:
        return ""
    random_index = random.randint(0, len(list_ad) - 1)
    if list_ad[random_index][2] != lang_chat_code:
        return ""
    return "\n---------------\n" + list_ad[random_index][1]
