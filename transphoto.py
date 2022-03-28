import io
import logging
import traceback

import PIL.Image
from pytesseract import pytesseract

import locales
import logger
import utils
from ad_module import add_ad

pytesseract_func = True


def photo_main(message):
    if not pytesseract_func:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "pyTesseractDisabled"))
        return

    logger.write_log(message, "not_needed")

    if message.reply_to_message is None:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "pleaseAnswer"))
        return

    lang = "eng"
    if utils.extract_arg(message.text, 0) == '/scan' and utils.extract_arg(message.text, 1) is not None:
        lang = utils.iso.get(utils.lang_autocorr(utils.extract_arg(message.text, 1)))
    elif utils.extract_arg(message.text, 2) is not None:
        lang = utils.iso.get(utils.lang_autocorr(utils.extract_arg(message.text, 1)))

    if lang is None:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "badSrcLangException"))
        return

    if message.reply_to_message.photo is not None:
        file_buffer = io.BytesIO(utils.bot.download_file
                                 (utils.bot.get_file(message.reply_to_message.photo[-1].file_id).file_path))
    elif message.reply_to_message.document is not None:
        if not message.reply_to_message.document.mime_type == "image/png" and \
                not message.reply_to_message.document.mime_type == "image/jpeg":
            utils.bot.reply_to(message, locales.get_text(message.chat.id, "photoNotFound"))
            return
        file_buffer = io.BytesIO(utils.bot.download_file
                                 (utils.bot.get_file(message.reply_to_message.document.file_id).file_path))
    else:
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "photoNotFound"))
        return

    try:
        img = PIL.Image.open(file_buffer)
    except Exception as e:
        logging.error(str(e) + "\n" + traceback.format_exc())
        utils.bot.reply_to(message, locales.get_text(message.chat.id, "photoDetectErr"))
        return

    tmpmessage = utils.bot.reply_to(message, locales.get_text(message.chat.id, "scanStarted"))
    idc = tmpmessage.chat.id
    idm = tmpmessage.message_id

    try:
        text = pytesseract.image_to_string(img, lang=lang)
    except Exception as e:
        logging.error(str(e) + "\n" + traceback.format_exc())
        utils.bot.edit_message_text(locales.get_text(message.chat.id, "photoDetectErr"), idc, idm)
        return

    if text == "":
        utils.bot.edit_message_text(locales.get_text(message.chat.id, "textNotFound"), idc, idm)
        logging.info(logger.username_parser(message) + ": text from photo wasn't scanned")
        return

    if logger.logger_message is True:
        logging.info("user " + logger.username_parser(message) + ": text from photo scanned successfully\n" + text)
    elif logger.logger is True:
        logging.info(logger.username_parser(message) + ": text from photo scanned successfully")

    if 0 < utils.len_limit < len(text):
        utils.bot.edit_message_text(locales.get_text(message.chat.id, "maxLength").format(utils.len_limit), idc, idm)
        return

    if utils.extract_arg(message.text, 0) == '/scan':
        utils.bot.edit_message_text(text + add_ad(message.chat.id), idc, idm)
        return

    if utils.extract_arg(message.text, 2) is not None:
        trg_lang = utils.extract_arg(message.text, 2)
    elif utils.extract_arg(message.text, 1) is not None:
        trg_lang = utils.extract_arg(message.text, 1)
    else:
        utils.bot.edit_message_text(locales.get_text(message.chat.id, "badTrgLangException"), idc, idm)
        return

    try:
        utils.bot.edit_message_text(utils.translator.get_translate(text, trg_lang)
                                    + add_ad(message.chat.id), idc, idm)
    except utils.translator.BadTrgLangException:
        utils.bot.edit_message_text(locales.get_text(message.chat.id, "badTrgLangException"), idc, idm)
    except utils.translator.BadSrcLangException:
        utils.bot.edit_message_text(locales.get_text(message.chat.id, "badSrcLangException"), idc, idm)
    except utils.translator.TooManyRequestException:
        utils.bot.edit_message_text(locales.get_text(message.chat.id, "tooManyRequestException"), idc, idm)
    except utils.translator.TooLongMsg:
        utils.bot.edit_message_text(locales.get_text(message.chat.id, "tooLongMsg"), idc, idm)
    except utils.translator.EqualLangsException:
        utils.bot.edit_message_text(locales.get_text(message.chat.id, "equalLangsException"), idc, idm)
    except utils.translator.UnkTransException:
        utils.bot.edit_message_text(locales.get_text(message.chat.id, "unkTransException"), idc, idm)


def transphoto_config_init(config):
    global pytesseract_func
    try:
        path = config["Polyglot"]["pytesseract"]
        if path == "":
            raise KeyError
    except KeyError:
        logging.warning("Pytesseract path isn't found. It's may be normal if you use Linux "
                        "or added Pytesseract in Path on Windows")
        return

    if path.lower() == "disable":
        logging.info("Pytesseract function disabled")
        pytesseract_func = False
        return

    pytesseract.tesseract_cmd = path
