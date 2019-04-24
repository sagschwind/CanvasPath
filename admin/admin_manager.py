from flask import render_template, request, make_response, Blueprint, redirect
from database import team_management_api, course_management_api, admin_management_api, user_manager_api
from Utility import get_email_and_type, USER, render_error, host
from database.TableSchema import *

admin_app = Blueprint('admin_app', __name__)

@admin_app.route('/', methods=['GET'])
def render_admin_home():
    user_name, user_type = get_email_and_type(request)
    if not admin_management_api.validate_admin(user_name, user_type):
        return redirect(host + "/logout")
    else:
        return make_response(render_template("admin/home.html"))

@admin_app.route('/student', methods=['GET', 'POST'])
def render_admin_students():
    user_name, user_type = get_email_and_type(request)
    if not admin_management_api.validate_admin(user_name, user_type):
        return redirect(host + "/logout")
    else:
        return render_admin_students_page()

@admin_app.route('/professor', methods=['GET'])
def render_admin_professors():
    user_name, user_type = get_email_and_type(request)
    if not admin_management_api.validate_admin(user_name, user_type):
        return redirect(host + "/logout")
    else:
        return render_admin_professors_page()

@admin_app.route('/courses', methods=['GET'])
def render_admin_courses():
    user_name, user_type = get_email_and_type(request)
    if not admin_management_api.validate_admin(user_name, user_type):
        return redirect(host + "/logout")
    else:
        return render_admin_courses_page()

@admin_app.route('/courses/drop_course/<course_id>', methods=['POST'])
def admin_drop_course(course_id):
    user_name, user_type = get_email_and_type(request)
    if not admin_management_api.validate_admin(user_name, user_type):
        return redirect(host + "/logout")
    else:
        course_management_api.delete_course(course_id)
        return redirect(host + "/admin/courses")

@admin_app.route('/courses/add_course', methods=['POST'])
def admin_add_course():
    user_name, user_type = get_email_and_type(request)
    if not admin_management_api.validate_admin(user_name, user_type):
        return redirect(host + "/logout")
    else:
        handle_add_course(request.form)
        return redirect(host + "/admin/courses")

@admin_app.route('/courses/<course_id>', methods=['GET'])
def render_admin_course(course_id):
    user_name, user_type = get_email_and_type(request)
    if not admin_management_api.validate_admin(user_name, user_type):
        return redirect(host + "/logout")
    else:
        return render_admin_single_course(course_id)

@admin_app.route('/courses/<course_id>/<sec_no>', methods=['GET'])
def render_admin_section(course_id, sec_no):
    user_name, user_type = get_email_and_type(request)
    if not admin_management_api.validate_admin(user_name, user_type):
        return redirect(host + "/logout")
    else:
        return render_admin_single_section(course_id, sec_no)

@admin_app.route('/courses/<course_id>/<sec_no>/<action>', methods=['POST'])
def handle_section_action(course_id, sec_no, action):
    user_name, user_type = get_email_and_type(request)
    if not admin_management_api.validate_admin(user_name, user_type):
        return redirect(host + "/logout")
    elif action == "add_professor":
        team_id = course_management_api.get_team_id(course_id, sec_no)
        course_management_api.add_professor_to_teaching_team(request.form["email"], team_id)
    elif action == "drop_professor":
        team_id = course_management_api.get_team_id(course_id, sec_no)
        course_management_api.drop_professor_from_teaching_team(request.form["email"], team_id)
    elif action == "add_student":
        course_management_api.add_student_section(request.form["email"],
                                                  course_id,
                                                  sec_no)
    elif action == "drop_student":
        course_management_api.drop_student_section(request.form["email"],
                                                   course_id,
                                                   sec_no)
    return redirect("/".join([host, "admin/courses", course_id, sec_no]))

@admin_app.route('/courses/<course_id>/add_section', methods=['POST'])
def add_section(course_id):
    user_name, user_type = get_email_and_type(request)
    if not admin_management_api.validate_admin(user_name, user_type):
        return redirect(host + "/logout")
    handle_add_section(course_id, request.form)
    return redirect("/".join([host, "admin/courses", course_id]))

@admin_app.route('/<user_type>/drop/<student_id>', methods=['POST'])
def drop_student(user_type, student_id):
    user_name, _ = get_email_and_type(request)
    if not admin_management_api.validate_admin(user_name, user_type):
        return redirect(host + "/logout")

    _type = "X"
    if user_type == "student":
        _type = USER.STUDENT
    else:
        return redirect(host + "/logout")

    user_manager_api.delete_user(student_id, _type)
    return redirect(host + "/admin/" + user_type)

def render_admin_students_page():
    all_students = course_management_api.get_all_students()

    return make_response(render_template('admin/students.html',
                                         all_students=all_students
                                         )
                         )

def render_admin_professors_page():
    all_students = course_management_api.get_all_professors()

    return make_response(render_template('admin/professors.html',
                                         all_students=all_students
                                         )
                         )

def render_admin_courses_page():
    data = course_management_api.get_all_courses()
    return make_response(render_template("admin/courses.html",
                                         headers=data["headers"],
                                         link_prefix="admin/courses",
                                         data_2d=data["course_info"]
                                         )
                         )

def handle_add_course(form):
    course_id = form["course_id"]
    course_name = form["course_name"]
    course_description = form["course_description"]

    new_course = Course(course_id, course_name, course_description)
    course_management_api.insert_course(new_course)

def handle_add_section(course_id, form):
    section_type = form['type']
    prof_email = form['email']
    enroll_limit = form['enroll_limit']

    next_section = course_management_api.get_next_section_number(course_id)
    team = Prof_teams(course_id)
    team_management_api.insert_team(team)

    member = Prof_team_members(prof_email, course_id)
    team_management_api.insert_team_member(member)

    section = Sections(course_id, next_section, section_type, enroll_limit, course_id)
    course_management_api.insert_section(section)

def render_admin_single_course(course_id):
    data = course_management_api.get_course_section_infomation("admin@lionstate.edu", USER.ADMIN, course_id)
    all_profs = course_management_api.get_all_professor_emails()

    return make_response(render_template("admin/course_listing.html",
                                         course_info=data["course_info"],
                                         sections=data["sections"],
                                         user_type=USER.ADMIN,
                                         teaching=False,
                                         professor_emails=all_profs
                                         )
                         )

def render_admin_single_section(course_id, sec_no):
    section_info = course_management_api.get_basic_section_info(course_id, sec_no)
    all_profs = course_management_api.get_all_professor_emails()
    section_students = course_management_api.get_students_in_section(course_id, sec_no)
    all_student_emails = [student[1] for student in course_management_api.get_all_students()]

    return make_response(render_template('admin/section_listing.html',
                                         course_info=section_info["course_info"],
                                         professors=section_info["professors"],
                                         professor_emails=all_profs,
                                         students=section_students,
                                         student_emails=all_student_emails,
                                         course_id=course_id,
                                         sec_no=sec_no
                                         )
                         )
