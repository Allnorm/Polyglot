import telebot
import sql_worker
import utils


def mailing(message):
    sql_worker.update_premium_list()
    chat_list = sql_worker.get_chat_list()
    print(chat_list)
    for current_chat in chat_list:
        if current_chat[3] == "no" and current_chat[0] != str(message.chat.id):
            try:
                utils.bot.copy_message(current_chat[0], message.chat.id, message.id)
            except telebot.apihelper.ApiTelegramException:
                pass
