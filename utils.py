import traceback
import telebot
from googletrans import Translator

# proxy = {'http':'ip:port'}
# translator = Translator(service_urls=['translate.googleapis.com'], proxies=proxy)
# try it if bot was banned in Google Api
# usually unban happens in about half an hour

translator = Translator(service_urls=['translate.googleapis.com'])

layouts = {'en': "qwertyuiop[]asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?`~",
           'ru': "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,ёЁ",
           'uk': "йцукенгшщзхїфівапролджєячсмитьбю.ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮ,'₴",
           'be': "йцукенгшўзх'фывапролджэячсмітьбю.ЙЦУКЕНГШЎЗХ'ФЫВАПРОЛДЖЭЯЧСМІТЬБЮ,ёЁ"}


def current_token():

    token = ""
    try:
        file = open("token", 'r')
        token = file.read()
        file.close()
    except Exception as e:
        print("ERR: Token file not found or not readable! Bot will close!")
        print(e)
        traceback.print_exc()
        exit(1)

    return token

bot = telebot.TeleBot(current_token())

def textparser(message):

    if message.reply_to_message is None:
        bot.reply_to(message, "Пожалуйста, используйте эту команду как ответ на сообщение")
        return

    if message.reply_to_message.text is not None:
        inputtext = message.reply_to_message.text
    elif message.reply_to_message.caption is not None:
        inputtext = message.reply_to_message.caption
    elif hasattr(message.reply_to_message, 'poll'):
        inputtext = message.reply_to_message.poll.question + "\n\n"
        for option in message.reply_to_message.poll.options:
            inputtext += "☑️ " + option.text + "\n"
    else:
        bot.reply_to(message, "Перевод не выполнен. В сообщении не обнаружен текст.\n")
        return

    if len(inputtext) >= 3000:
        bot.reply_to(message, "Ошибка. В сообщении более 3000 символов!")
        return

    return inputtext


def extract_arg(arg, num):

    try:
        return arg.split()[num]
    except Exception:
        pass

def extract_lang(lang):

    return translator.detect(lang).lang
