import sqlite3
import time
import traceback

import logger

dbname = "chatlist.db"


class SQLWriteError(Exception):
    pass


def table_init():
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    try:
        cursor.execute('''CREATE TABLE if not exists chats (
                                    chat_id TEXT NOT NULL PRIMARY KEY,
                                    lang TEXT NOT NULL,
                                    is_locked TEXT,
                                    premium TEXT NOT NULL,
                                    expire_time INTEGER,
                                    user_id TEXT,
                                    target_lang TEXT);''')
        cursor.execute('''CREATE TABLE if not exists tasks (
                                    message_id TEXT NOT NULL,
                                    body TEXT NOT NULL,
                                    region TEXT NOT NULL,
                                    expire_time INTEGER,
                                    chat_id TEXT NOT NULL);''')
        sqlite_connection.commit()
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.write_log("ERR: write mySQL DB failed!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
    cursor.close()
    sqlite_connection.close()


def get_chat_info(chat_id, user_id=None):
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    try:
        if user_id is not None:
            cursor.execute("""SELECT * FROM chats WHERE user_id = ?""", (user_id,))
        else:
            cursor.execute("""SELECT * FROM chats WHERE chat_id = ?""", (chat_id,))
        record = cursor.fetchall()
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.write_log("ERR: read mySQL DB failed!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        record = []
    cursor.close()
    sqlite_connection.close()
    return record


def get_chat_list():
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    try:
        cursor.execute("""SELECT * FROM chats WHERE premium = 'no'""")
        record = cursor.fetchall()
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.write_log("ERR: read mySQL DB failed!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        record = []
    cursor.close()
    sqlite_connection.close()
    return record


def update_premium_list():
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    try:
        cursor.execute("""SELECT * FROM chats WHERE premium = 'yes'""")
        record = cursor.fetchall()
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.write_log("ERR: read mySQL DB failed!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        record = []
    if record:
        for current_chat in record:
            if current_chat[4] < time.time() and current_chat[4] != 0:
                try:
                    write_chat_info(current_chat[0], "premium", "no")
                    write_chat_info(current_chat[0], "expire_time", "0")
                except SQLWriteError:
                    break
    cursor.close()
    sqlite_connection.close()


def actualize_chat_premium(chat_id):
    current_chat = get_chat_info(chat_id)
    if not current_chat:
        return
    if current_chat[0][3] == "yes":
        if current_chat[0][4] < time.time() and current_chat[0][4] != 0:
            try:
                write_chat_info(current_chat[0][0], "premium", "no")
                write_chat_info(current_chat[0][0], "expire_time", "0")
            except SQLWriteError:
                return


def write_chat_info(chat_id, key, value):
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    try:
        cursor.execute("""SELECT * FROM chats WHERE chat_id = ?""", (chat_id,))
        record = cursor.fetchall()
        if not record:
            cursor.execute("""INSERT INTO chats VALUES (?,?,?,?,?,?,?);""",
                           (chat_id, "en", "no", "no", "0", "", "disable"))
        cursor.execute("""UPDATE chats SET {} = ? WHERE chat_id = ?""".format(key), (value, chat_id))
        sqlite_connection.commit()
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.write_log("ERR: write mySQL DB failed!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        cursor.close()
        sqlite_connection.close()
        raise SQLWriteError
    cursor.close()
    sqlite_connection.close()


def write_task(message_id, body, region, expire_time, chat_id):
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    try:
        cursor.execute("""SELECT * FROM tasks WHERE message_id = ? AND chat_id = ?""", (message_id, chat_id,))
        record = cursor.fetchall()
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.write_log("ERR: read mySQL DB failed!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        record = []
    if record:
        return False
    try:
        cursor.execute("""INSERT INTO tasks VALUES (?,?,?,?,?);""", (message_id, body, region, expire_time, chat_id))
        sqlite_connection.commit()
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.write_log("ERR: write mySQL DB failed!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        cursor.close()
        sqlite_connection.close()
        raise SQLWriteError
    cursor.close()
    sqlite_connection.close()


def get_tasks(lang_code):
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    try:
        cursor.execute("""SELECT * FROM tasks WHERE region = ?""", (lang_code,))
        record = cursor.fetchall()
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.write_log("ERR: read mySQL DB failed!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        record = []
    cursor.close()
    sqlite_connection.close()
    return record


def rem_task(message_id, chat_id):
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    try:
        cursor.execute("""DELETE FROM tasks WHERE message_id = ? AND chat_id = ?""", (message_id, chat_id,))
        sqlite_connection.commit()
        cursor.close()
        sqlite_connection.close()
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.write_log("ERR: write mySQL DB failed!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        cursor.close()
        sqlite_connection.close()
        raise SQLWriteError
