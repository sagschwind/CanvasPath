from flask import Flask, render_template, request
from bootup import start_database
import sqlite3 as sql


host = 'http://127.0.0.1:5000/'
DATABASE_NAME = 'database.db'

def start_app():
    app = Flask(__name__)

    start_database(DATABASE_NAME)

    return app

app = start_app()



@app.route('/', methods=['POST', 'GET'])
def name():
    error = None
    if request.method == 'POST':
        user_type, user_data = valid_name(request.form['Email'], request.form['Password'])
        print(user_type, user_data)
        if user_type != "Error":
            return render_template('input.html', error=error, url=host, user_type=user_type, user_data=user_data)
        else:
            return render_template('input.html', error=error, url=host, user_error=user_data)
    return render_template('input.html', error=error, url=host)


def valid_name(email, password):
    dictionary = {"email": email, "password": password}
    connection = sql.connect('database.db')

    cursor = connection.execute('SELECT * FROM Student WHERE Student.email = :email AND Student.password = :password;', dictionary)
    value = cursor.fetchall()

    print(value)

    if len(value) > 1:
        raise Exception("Only one Student should have the same email and password")
    elif len(value) == 1:
        return "Student", value[0]

    cursor = connection.execute('SELECT * FROM Professor WHERE Professor.email = :email AND Professor.password = :password;', dictionary)
    value = cursor.fetchall()
    if len(value) > 1:
        raise Exception("Only one Professor should have the same email and password")
    elif len(value) == 1:
        return "Professor", value[0]

    return "Error", "login_error"

if name == "__main__":
    app.run()