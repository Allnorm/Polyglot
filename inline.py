import traceback

from telebot import types

import logger
import utils


def translate_query(inline_query):

    lang = utils.extract_arg(inline_query.query, 0)

    try:
        inputtext = inline_query.query.split(' ', 1)[1].lstrip()
    except IndexError:
        return "Введите код языка и текст"

    logger.write_log("LOG: user " + logger.username_parser(inline_query) + " sent an INLINE: " + inputtext)

    if lang is None:
        return "Укажите код языка/название страны"

    try:
        translated = utils.translator.translate_text(parent=utils.project_name,
                                                     contents=[inputtext], target_language_code=lang,
                                                     mime_type="text/plain").translations[0].translated_text
        if translated == inputtext:
            return ("Исходный и итоговый текст совпадают. Возможно, Google Api отклонил запрос. "
                    "Если вы уверены, что так быть не должно, повторите попытку позже")
        return translated

    except Exception as e:
        if str(e) in "400 Target language is invalid.":
            return "Указан неверный код языка/название страны"
        else:
            logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
            return ("Ошибка перевода. Обратитесь к авторам бота\n"
                    "Информация для отладки сохранена в логах бота.")


def query_text_main(inline_query):

    text_result = translate_query(inline_query)
    output = types.InlineQueryResultArticle(
        id='1', title="Перевод",
        description="{!s}".format(text_result),
        input_message_content=types.InputTextMessageContent(message_text="{!s}".format(text_result)))
    utils.bot.answer_inline_query(inline_query.id, [output])
    print(text_result)