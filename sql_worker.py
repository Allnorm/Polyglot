import sqlite3

dbname = "chatlist.db"


def table_init():
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    cursor.execute('''CREATE TABLE if not exists chats (
                                    chat_id TEXT NOT NULL PRIMARY KEY,
                                    lang TEXT NOT NULL,
                                    premium TEXT NOT NULL);''')
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()


def get_chat_info(chat_id):
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    cursor.execute("""SELECT * FROM chats WHERE chat_id = ?""", (chat_id,))
    record = cursor.fetchall()
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()
    if not record:
        return None
    return record


def write_chat_info(chat_id, lang="en", premium="not"):
    sqlite_connection = sqlite3.connect(dbname)
    cursor = sqlite_connection.cursor()
    cursor.execute("""SELECT * FROM chats WHERE chat_id = ?""", (chat_id,))
    record = cursor.fetchall()
    if not record:
        cursor.execute("""INSERT INTO chats VALUES (?,?,?);""", (chat_id, lang, premium))
    else:
        cursor.execute("""UPDATE chats SET lang = ?, premium = ? WHERE chat_id = ?""", (lang, premium, chat_id))
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()