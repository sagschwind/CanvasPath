import sqlite3 as sql
from database.TableSchema import *
from Utility import DATABASE_NAME, USER
from werkzeug.security import generate_password_hash, check_password_hash

# Validate login
def valid_login(email, password):
    dictionary = {"email": email}
    connection = sql.connect(DATABASE_NAME)

    cursor = connection.execute('SELECT Student.password FROM Student WHERE Student.email = :email', dictionary)
    value = cursor.fetchall()

    print()
    if len(value) > 1:
        raise Exception("Only one Student should have the same email and password")
    elif len(value) == 1:
        if check_password_hash(value[0][0], password):
            connection.close()
            return USER.STUDENT, None
        return None, "login_error"

    cursor = connection.execute('SELECT Professor.password FROM Professor WHERE Professor.email = :email', dictionary)
    value = cursor.fetchall()
    if len(value) > 1:
        raise Exception("Only one Professor should have the same email and password")
    elif len(value) == 1:
        if check_password_hash(value[0][0], password):
            connection.close()
            return USER.PROFESSOR, None
        return None, "login_error"

    cursor = connection.execute('SELECT Admin_Info.password FROM Admin_Info WHERE Admin_Info.user_name = :email', dictionary)
    value = cursor.fetchall()
    if len(value) > 1:
        raise Exception("Only one Admin should have the same email and password")
    elif len(value) == 1:
        if check_password_hash(value[0][0], password):
            connection.close()
            return USER.ADMIN, None
        return None, "login_error"

    connection.close()
    return None, "login_error"

# Gets a user's private information from the Student or Professor Table
def get_private_user_info(user_email, user_type):
    dictionary = {"email": user_email}
    connection = sql.connect(DATABASE_NAME)

    statement = None
    if user_type == USER.STUDENT:
        statement = 'SELECT email, name, age, gender, major, street, zipcode FROM Student WHERE Student.email = :email;'
    elif user_type == USER.PROFESSOR:
        statement = 'SELECT email, name, age, gender FROM Professor WHERE Professor.email = :email;'
    else:
        raise Exception("User not a professor or student")
    cursor = connection.execute(statement, dictionary)
    value = cursor.fetchall()
    connection.close()

    if len(value) > 1:
        raise Exception("Only one user should have the email (" + user_email + ")")

    data = value[0]
    print(data)
    if user_type == USER.STUDENT:
        return Student(data[0], None, data[1], data[2], data[3], data[4], data[5], data[6])
    else:
        return Professor(data[0], None, data[1], data[2], data[3], None, None, None)

def get_public_user_info(user_email):
    dictionary = {"email": user_email}
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Student.name, Student.major, Student.email
    FROM Student
    WHERE Student.email = :email;"""
    cursor = connection.execute(statement, dictionary)
    value = cursor.fetchall()

    if len(value) > 1:
        raise Exception("Only one Student should have the same email and password")
    elif len(value) == 1:
        connection.close()
        return value[0], USER.STUDENT

    statement = """
    SELECT Professor.name, Professor.department, Professor.title, Professor.office_address, Professor.email
    FROM Professor
    WHERE Professor.email = :email
    """
    cursor = connection.execute(statement, dictionary)
    value = cursor.fetchall()

    if len(value) > 1:
        raise Exception("Only one Professor should have the same email and password")
    elif len(value) == 1:
        connection.close()
        return value[0], USER.PROFESSOR

    connection.close()
    return None, None

def change_student_information(user_email, user_type, form):
    if user_type == USER.UNKNOWN:
        return "UserType"

    if "new_password" in form and "old_password" in form:
        return _handle_password_change(user_email,
                                               form["old_password"],
                                               form["new_password"]
                                               )

    connection = sql.connect(DATABASE_NAME)

    statement = """
    UPDATE {}
    SET {}
    WHERE {}.email = "{}";
    """

    update_pairs = ["{} = :{}".format(key, key) for key in form.keys()]
    statement = statement.format(user_type, ", ".join(update_pairs), user_type, user_email)

    cursor = connection.execute(statement, form)
    connection.commit()

def _handle_password_change(user_email, old_password, new_password):
    dictionary = {
        "user_email": user_email,
        "old_password": old_password,
        "new_password": new_password
    }

    user_type, _ = valid_login(user_email, old_password)

    if user_type is None or len(new_password) < 8:
        return {"error": "Login Error"}

    connection = sql.connect(DATABASE_NAME)

    statement = """
    UPDATE {user_type}
    SET password = "{new_password}"
    WHERE email = "{user_email}";
    """.format(user_type=user_type,
               new_password=generate_password_hash(new_password),
               user_email=user_email)
    print(statement)
    cursor = connection.execute(statement)
    connection.commit()

def delete_user(email, user_type):
    dictionary = {
        "user_email": email
    }

    connection = sql.connect(DATABASE_NAME)

    statement = None
    if user_type == USER.STUDENT:
        statement = """
        DELETE
        FROM Student
        WHERE Student.email = :user_email;
        """
    elif user_type == USER.PROFESSOR:
        statement = """
        DELETE
        FROM Professor
        WHERE Professor.email = :user_email;
        """
    else:
        return

    connection.execute(statement, dictionary)
    connection.commit()
