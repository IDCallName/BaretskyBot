import mysql.connector as mysql

import functools as ft

# =========================
#
# Constants
#
# =========================

CLUB_ID = -1001591691963

# =========================
#
# MYSQL Functions
#
# =========================


def mysql_makeSelectQuery(connection, query: str) -> tuple:
    """
    Makes a query and sends back a result tuple
    """

    assert type(query) == str

    with connection.cursor() as cursor:
        cursor.execute(query)
        mysql_result = cursor.fetchall()

    return mysql_result

def mysql_makeUpdateQuery(connection, query: str) -> None:
    """
    Makes a query and commits it
    """

    assert type(query) == str

    with connection.cursor() as cursor:
        cursor.execute(query)
        connection.commit()


# =========================
#
# Decorators
#
# =========================


def chat_check(func):

    @ft.wraps(func)
    def inner(update, context):

        # tell anyone who is using bot out of baretsky club to heck off
        if(update.message.chat.id != CLUB_ID):
            msg = "Бот не предназначен для использования вне Барецкого Клуба!"
            context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

        # else do command
        else:
            func(update, context)

    return inner



# =========================
#
# Tracks
#
# =========================


class Track:

    def __init__(self, connection, track_name):
        """Loads an epic track from database."""

        # checks for a possible injection
        if (not "'" in track_name):
            self.track_name = track_name.lower()
        else:
            self.track_name = "У меня тяжелая зависимоть от вставления одинарных кавычек куда не просят, прошу скинуться мне на лечение"

        # makes query
        mysql_query = f"SELECT * FROM tracks WHERE track_name = '{track_name}' LIMIT 1"
        mysql_result = mysql_makeSelectQuery(connection, mysql_query)

        # sets attributes from the query result
        if(len(mysql_result) == 1):
            self.track_id, _, self.track_msg, self.track_description, self.track_author = mysql_result[0]

        # else sets every attribute to zero
        else:
            self.track_id = None
            self.track_msg = None
            self.track_description = "Unknown track"
            self.track_author = "Unknown"



    @staticmethod
    def create_track(connection, name: str, message: int, description: str, author: str) -> str:
        """Adds an epic track to the database"""

        # an injection test
        if "'" in name or "'" in description or "'" in author:
            return "Я запрещаю Вам использовать одинарные кавычки"

        # inserts new data into DB otherwise
        else:
            mysql_query = f"INSERT INTO tracks (track_name, track_msg, track_description, track_author) VALUES ('{name}', {str(message)}, '{description}', '{author}')"
            mysql_makeUpdateQuery(connection, mysql_query)

            return "Трек был добавлен в плейлист Барецкого клуба (наверное)"


