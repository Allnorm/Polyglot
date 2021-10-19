import sqlite3
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
                                    expire_time INTEGER);''')
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.write_log("ERR: write mySQL DB failed!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()


def get_chat_info(chat_id):
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    try:
        cursor.execute("""SELECT * FROM chats WHERE chat_id = ?""", (chat_id,))
        record = cursor.fetchall()
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.write_log("ERR: read mySQL DB failed!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        record = []
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()
    if not record:
        return None
    return record


def write_chat_info(chat_id, key, value):
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    try:
        cursor.execute("""SELECT * FROM chats WHERE chat_id = ?""", (chat_id,))
        record = cursor.fetchall()
        if not record:
            cursor.execute("""INSERT INTO chats VALUES (?,?,?,?,?);""",
                           (chat_id, "en", "no", "no", "0"))
        cursor.execute("""UPDATE chats SET {} = ? WHERE chat_id = ?""".format(key), (value, chat_id))
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        logger.write_log("ERR: write mySQL DB failed!")
        logger.write_log("ERR: " + str(e) + "\n" + traceback.format_exc())
        raise SQLWriteError
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()
