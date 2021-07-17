from telebot import types

import interlayer
import logger
import utils


def translate_query(inline_query):
    logger.write_log("LOG: user " + logger.username_parser(inline_query) + " sent an INLINE: " + inline_query.query)

    inline_query.query = utils.lang_autocorr(inline_query.query, True)
    lang = utils.extract_arg(inline_query.query, 0)

    try:
        inputtext = inline_query.query.split(' ', 1)[1].lstrip()
    except IndexError:
        return "Введите код/название языка и текст"

    if lang is None:
        return "Укажите код/название языка"

    try:
        inputtext = interlayer.get_translate(inputtext, lang)
        return inputtext
    except interlayer.BadTrgLangException:
        return "Указан неверный код/название языка"
    except interlayer.TooManyRequestException:
        return "Слишком много запросов к API, пожалуйста, попробуйте позже."
    except interlayer.UnkTransException:
        return "Ошибка перевода. Обратитесь к авторам бота.\nИнформация для отладки сохранена в логах бота."


def query_text_main(inline_query):
    text_result = translate_query(inline_query)
    output = types.InlineQueryResultArticle(
        id='1', title="Перевод",
        description=text_result,
        input_message_content=types.InputTextMessageContent(message_text=text_result))
    utils.bot.answer_inline_query(inline_query.id, [output])
