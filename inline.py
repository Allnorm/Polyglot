import logging

from telebot import types

import ad_module
import locales
import logger
import utils


def translate_query(inline_query):
    if logger.logger_message is True:
        logging.info("user " + logger.username_parser(inline_query) + " sent an INLINE: " + inline_query.query)
    elif logger.logger is True:
        logging.info("user " + logger.username_parser(inline_query) + " sent an INLINE")

    if len(inline_query.query) > 250:
        return locales.get_text_inline(inline_query, "tooLongInline")

    if 0 < utils.len_limit < len(inline_query.query):
        return locales.get_text_inline(inline_query, "maxLength").format(utils.len_limit)

    inline_query.query = utils.lang_autocorr(inline_query.query, True)
    lang = utils.extract_arg(inline_query.query, 0)

    try:
        inputtext = inline_query.query.split(' ', 1)[1].lstrip()
    except IndexError:
        return locales.get_text_inline(inline_query, "inlineInstruction")

    if lang is None:
        return locales.get_text_inline(inline_query, "inlineInstructionTwo")

    try:
        inputtext = utils.translator.get_translate(inputtext, lang)
        return inputtext
    except utils.translator.BadTrgLangException:
        return locales.get_text_inline(inline_query, "badTrgLangException")
    except utils.translator.TooManyRequestException:
        return locales.get_text_inline(inline_query, "tooManyRequestException")
    except utils.translator.UnkTransException:
        return locales.get_text_inline(inline_query, "unkTransException")


def query_text_main(inline_query):
    text_result = translate_query(inline_query)
    output = types.InlineQueryResultArticle(
        id='1', title=locales.get_text_inline(inline_query, "inlineTitle"),
        description=text_result,
        input_message_content=types.InputTextMessageContent
        (message_text=text_result + ad_module.add_ad("", inline_query.from_user.id)))
    utils.bot.answer_inline_query(inline_query.id, [output])
