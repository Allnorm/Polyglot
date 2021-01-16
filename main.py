from googletrans import LANGUAGES

from distort import distort_main
from logger import write_log, clear_log, download_clear_log, key_reader, BLOB_TEXT
from qwerty import qwerty_main
from translate import translate_main
from utils import bot, layouts

clear_log()
write_log("Polyglot was started")
key_reader()


@bot.message_handler(commands=['qwerty', 'q'])
def qwerty(message):

    qwerty_main(message)


@bot.message_handler(commands=['d', 'distort'])
def distort(message):

    distort_main(message)

@bot.message_handler(commands=['translate', 'trans', 't'])
def translate(message):

    translate_main(message)


@bot.message_handler(commands=['start'])
def send_welcome(message):

    write_log(BLOB_TEXT, message)
    bot.reply_to(message, "Привет. Я бот - переводчик. "
                          "Работаю на основе Google Translate API, и могу переводить сообщения в чате на лету.\n\n"
                          "Для этого добавь меня в чат, и при необходимости перевести чьё-то "
                          "сообщение 'Ответь' на него, и напиши команду: /t <код языка>. "
                          "Исходный язык перевода бот определит автоматически.\n\n"
                          "Остальные команды можно узнать командой /help.\n\n"
                          "Также я могу работать в личных сообщениях, как обычный переводчик.")


@bot.message_handler(commands=['help', 'h'])
def send_help(message):

    write_log(BLOB_TEXT, message)
    bot.reply_to(message, "[/t, /trans, /translate] <язык> - перевести сообщение. Исходный язык определяется "
                          "автоматически. Коды языков можно узнать с помощью команды /langs или /l\n"
                          "[/l, /langs] - список доступных языковых кодов и раскладок клавиатуры\n"
                          "[/d, /distort] <количество итераций> <итоговый язык> - Перевести сообщение на заданное количество "
                          "рандомных языков и вывести результат на нужном вам языке. "
                          "Если оставить параметр <итоговый язык> пустым, результат будет выведен на языке "
                          "оригинала\n"
                          "[/q, /qwerty] <исходный язык> <итоговый язык> ИЛИ "
                          "/q <итоговый язык> - смена раскладки текста. Исходный язык может определяться "
                          "автоматически. Список доступных раскладок можно посмотреть с помощью команды /langs")


@bot.message_handler(commands=['langs', 'l'])
def send_list(message):

    write_log(BLOB_TEXT, message)

    output = "`Список всех кодов и соответствующих им языков:\n"

    for key, value in LANGUAGES.items():
        output = output + key + " - " + value + "\n"

    output = output + "\nСписок всех доступных раскладок клавиатуры: "

    for key, value in layouts.items():
        output = output + key + " "

    bot.reply_to(message, output + "`", parse_mode="markdown")


@bot.message_handler(commands=['downloadlog'])
def download_log(message):

    write_log(BLOB_TEXT, message)
    download_clear_log(message, True)

@bot.message_handler(commands=['clearlog'])
def clear_log(message):

    write_log(BLOB_TEXT, message)
    download_clear_log(message, False)

bot.polling(none_stop=True)
