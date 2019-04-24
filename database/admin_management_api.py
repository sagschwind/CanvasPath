import sqlite3 as sql
from Utility import USER, DATABASE_NAME
from database.TableSchema import *

def validate_admin(user_name, user_type):
    if user_type != USER.ADMIN:
        return False

    dictionary = {
        "user_name": user_name
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT * FROM Admin_Info
    WHERE Admin_Info.user_name = :user_name;
    """

    cursor = connection.execute(statement, dictionary)
    value = cursor.fetchall()

    return len(value) != 0