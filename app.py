from flask import Flask, render_template, request, make_response, redirect
from Utility import host, DATABASE_NAME, render_error, logout_extension, USER, get_email_and_type

from database import department_manager_api, user_manager_api
from database.bootup import start_database

from courses.course_manager import course_app
from departments.department_manager import department_app
from team.team_manager import team_app
from admin.admin_manager import admin_app


def start_app():
    app = Flask(__name__)
    app.register_blueprint(course_app, url_prefix="/courses")
    app.register_blueprint(department_app, url_prefix="/departments")
    app.register_blueprint(team_app, url_prefix="/team")
    app.register_blueprint(admin_app, url_prefix="/admin")
    start_database(DATABASE_NAME)

    return app

app = start_app()

@app.route('/', methods=['POST', 'GET'])
def home_page():
    error = None

    user_email, user_type = get_email_and_type(request)
    # User logged in already
    if user_email is not None:
        if user_email == "NULL":
            return render_template('login.html', error="Email invalid")
        return render_private_user_info(user_email, user_type)

    # Login request
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['Password']
        user_type, login_error = user_manager_api.valid_login(email, password)

        print(email, password, user_type, login_error)
        if login_error is not None:
            return render_template('login.html', error=login_error, url=host)
        else:
            return render_private_user_info(email, user_type)
    return render_template('login.html', error="Email invalid")

@app.route('/user/change_information', methods=['POST', 'GET'])
def present_user_change_page():
    user_email, user_type = get_email_and_type(request)
    # User logged in already
    if user_email is not None:
        if user_email == "NULL":
            return render_error("Email invalid, please logout")

        error = None
        if request.method == "POST":
            error = handle_change_information_request(user_email, user_type, request.form)
        return render_change_user_information(user_email, user_type, error)
    else:
        return redirect(host)

@app.route("/user/<user_id>", methods=['POST', 'GET'])
def user_info(user_id):
    user_email, user_type = get_email_and_type(request)
    # User logged in already
    if user_email is not None:
        if user_email == "NULL":
            return render_error("Email invalid, please logout")
        return render_public_user_info(user_id)
    else:
        return redirect(host)

@app.route(logout_extension, methods=['POST', 'GET'])
def logout():
    response = redirect(host)
    response.set_cookie("user_email", "NULL", expires=0)
    response.set_cookie("user_type", "NULL", expires=0)
    return response

def render_private_user_info(email, user_type):
    response = None
    print(user_type)
    if user_type == USER.STUDENT:
        response = render_student_info(email)
    elif user_type == USER.PROFESSOR:
        response = render_professor_info(email)
    elif user_type == USER.ADMIN:
        response = redirect(host + "/admin")
    else:
        return render_error("Not properly logged in")

    response.set_cookie("user_email", email)
    response.set_cookie("user_type", user_type)
    return response
def render_student_info(email):
    student = user_manager_api.get_private_user_info(email, USER.STUDENT)
    response = make_response(render_template('student_info.html',
                               url=host,
                               user=student))
    return response
def render_professor_info(email):
    professor = user_manager_api.get_private_user_info(email, USER.PROFESSOR)
    response = make_response(render_template('student_info.html',
                               url=host,
                               user=professor,
                               logout_url=host+logout_extension))
    return response

def render_change_user_information(user_email, user_type, error):
    student = user_manager_api.get_private_user_info(user_email, user_type)
    majors = department_manager_api.get_all_department_information()
    if user_type == USER.STUDENT:
        response = make_response(render_template('student_info_modify.html',
                                                 user=student,
                                                 majors=majors["course_info"],
                                                 error=error
                                                 )
                                 )
    else:
        response = make_response(render_template('professor_info_modify.html',
                                                 user=student,
                                                 error=error
                                                 )
                                 )

    return response

def handle_change_information_request(user_email, user_type, form):
    if user_type == USER.STUDENT or user_type == USER.PROFESSOR:
        return user_manager_api.change_student_information(user_email, user_type, form)
    else:
        return "User Type"

def render_public_user_info(user_email):
    user_info, user_type = user_manager_api.get_public_user_info(user_email)

    return make_response(render_template('user_public_info.html',
                         user=user_info,
                         user_type=user_type)
    )

