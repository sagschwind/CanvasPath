from flask import render_template, request, make_response, Blueprint, redirect
from Utility import host, render_error, USER, get_email_and_type
from database import course_management_api
from database.TableSchema import *

course_app = Blueprint('course_app', __name__)

@course_app.route('/', methods=["GET"])
def my_courses():
    # User logged in already
    user_email, user_type = get_email_and_type(request)
    if user_email is not None:
        if user_email == "NULL":
            return render_error("Email invalid")
        return render_user_courses(user_email, user_type)

    return render_error("Not logged in properly")

@course_app.route('/<course_id>/<sec_no>', methods=["GET"])
def course_information(course_id, sec_no):
    user_email, user_type = get_email_and_type(request)

    if user_email is not None:
        return render_user_course(user_email, user_type, course_id, sec_no)

    return render_error(request.url, "Not logged in properly")

@course_app.route('/<course_id>/<sec_no>/add_assignment', methods=["GET", "POST"])
def add_assignment(course_id, sec_no):
    user_email, user_type = get_email_and_type(request)
    if user_email is not None:
        if request.method == "POST":
            handle_add_assignment(course_id, sec_no, request.form)
            url = "/".join([host, "courses", course_id, sec_no])
            return redirect(url)
        else:
            return render_add_assignment_info(user_email, course_id, sec_no)

    return render_error("You do not have access to the page")

@course_app.route('/<course_id>/<sec_no>/<assignment_type>/<number>', methods=["GET", "POST"])
def assignment_information(course_id, sec_no, assignment_type, number):
    user_email, user_type = get_email_and_type(request)
    if user_email is not None:
        grade_id = None # For POST To identify if the grade was successful
        if request.method == "POST":
            grade_id = handle_add_course_grade(user_email,
                                    course_id,
                                    sec_no,
                                    assignment_type,
                                    number,
                                    request.form)
        if user_type == USER.PROFESSOR:
            return render_assignment_info(user_email,
                                          course_id,
                                          sec_no,
                                          assignment_type,
                                          number,
                                          grade_id
                                    )
        elif user_type == USER.STUDENT and assignment_type == "project":
            return render_student_capstone_project_information(course_id, sec_no, number)

    return render_error("You do not have access to the page")

@course_app.route('/<course_id>/<sec_no>/project/<number>/add_team', methods=["POST"])
def add_project_team(course_id, sec_no, number):
    user_email, user_type = get_email_and_type(request)
    if user_email is not None:
        if request.method == "POST":
            handle_add_project_team(course_id, sec_no, number)
        return redirect("/".join([host, "courses", course_id, sec_no, "project", number]))

    return render_error("You do not have access to the page")

@course_app.route('/<course_id>', methods=['GET', 'POST'])
def display_course_info(course_id):
    user_email, user_type = get_email_and_type(request)

    if user_email is not None:
        response = render_course_info(user_email, user_type, course_id)
        if response is not None:
            return response

    return render_error("Not logged in properly")

@course_app.route('/listings', methods=["GET"])
def display_all_course_listings():
    return render_all_courses()

def render_user_courses(email, user_type):
    if user_type == USER.STUDENT:
        response = render_student_courses(email)
    elif user_type == USER.PROFESSOR:
        response = render_professor_courses(email)
    else:
        return render_error("Not properly logged in")
    return response
def render_student_courses(email):
    courses = course_management_api.get_students_sections(email)

    response = make_response(render_template('courses/my_courses.html',
                                             url=host,
                                             courses=courses["data"],
                                             headers=courses["headers"])
    )
    return response
def render_professor_courses(email):
    courses = course_management_api.get_professor_courses(email)
    response = make_response(render_template('courses/my_courses.html',
                                             url=host,
                                             courses=courses["data"],
                                             headers=courses["headers"])
    )
    return response
def render_user_course(user_email, user_type, course_id, sec_no):
    if user_type == USER.STUDENT:
        response = render_student_course(user_email, course_id, sec_no)
    elif user_type == USER.PROFESSOR:
        response = render_professor_course(user_email, course_id, sec_no)
    else:
        return render_error("Not properly logged in")
    return response

def render_student_course(user_email, course_id, sec_no):
    enrolled = course_management_api.check_student_in_section(user_email, course_id, sec_no)

    if not enrolled:
        return make_response(render_template("courses/student_course_grades.html",
                                             enrolled=enrolled,
                                             course_id=course_id
                                             )
                             )

    course_info = course_management_api.get_basic_section_info(course_id, sec_no)

    hw_grades = course_management_api.get_homework_grades(user_email, course_id, sec_no)
    exam_grades = course_management_api.get_exam_grades(user_email, course_id, sec_no)
    capstone_grades = course_management_api.get_capstone_grade(user_email, course_id, sec_no)
    grades = {
        "hw_assignments": hw_grades,
        "exam_grades": exam_grades,
        "capstone_grades": capstone_grades
    }

    total_grade, count = 0.0, 0
    for _, grade_section in grades.items():
        if grade_section is not None:
            for grade in grade_section:
                total_grade += float(grade[2])
                count += 1

    total_grade /= count
    grades["total_grade"] = "{:3.2f}%".format(total_grade)

    print(course_info)
    return make_response(render_template("courses/student_course_grades.html",
                                         enrolled=enrolled,
                                         student_grades=grades,
                                         course_info=course_info,
                                         course_id=course_id,
                                         sec_no=sec_no
                                         )
                         )
def render_professor_course(user_email, course_id, sec_no):
    teaches = course_management_api.check_professor_teaches_section(user_email, course_id)

    course_info = course_management_api.get_basic_section_info(course_id, sec_no)

    hw_assignments = course_management_api.get_homework_assignments(course_id, sec_no)
    exams = course_management_api.get_exams(course_id, sec_no)
    capstone_projects = course_management_api.get_capstone_projects(course_id, sec_no)
    assignments = {
        "hw_assignments": hw_assignments,
        "exams": exams,
        "capstone_projects": capstone_projects
    }
    print(course_info)
    return make_response(render_template("courses/course_assignments.html",
                                         teaches=teaches,
                                         student_grades=assignments,
                                         course_info=course_info,
                                         course_id=course_id,
                                         sec_no=sec_no
                                         )
                         )

def render_assignment_info(professor_email,
                           course_id,
                           sec_no,
                           assignment_type,
                           assignment_number,
                           grade_id):
    teaches = course_management_api.check_professor_teaches_section(professor_email, course_id)
    if not teaches:
        return render_error("You are not allowed to access this page")

    switch = {
        "homework": render_homework_information,
        "exam": render_exam_information,
        "project": render_capstone_project_information
    }

    assignment_handler = switch.get(assignment_type, None)

    if assignment_handler is None:
        return render_error("Something went wrong")

    return assignment_handler(course_id, sec_no, assignment_number, grade_id)
def handle_add_course_grade(professor_email,
                            course_id,
                            sec_no,
                            assignment_type,
                            assignment_number,
                            form):
    teaches = course_management_api.check_professor_teaches_section(professor_email, course_id)
    if not teaches:
        return


    student_email, student_grade = form["email"], form["grade"]

    if assignment_type == "exam":
        exam_grade = Exam_grades(student_email,
                           course_id,
                           sec_no,
                           assignment_number,
                           student_grade)
        course_management_api.update_exam_grade(exam_grade)
    elif assignment_type == "homework":
        homework_grade = Homework_grades(student_email,
                                   course_id,
                                   sec_no,
                                   assignment_number,
                                   student_grade)
        course_management_api.update_homework_grade(homework_grade)
    elif assignment_type == "project":
        team_id = student_email
        capstone_grade = Capstone_grades(course_id, sec_no, student_email, student_grade)
        course_management_api.update_capstone_team_grade(capstone_grade)
    else:
        student_email = None

    return student_email

def render_homework_information(course_id, sec_no, assignment_number, grade_id):
    hw_info = course_management_api.get_homework_information(course_id,
                                                             sec_no,
                                                             assignment_number)
    hw_grades = course_management_api.get_homework_grades_for_professor(course_id,
                                                                        sec_no,
                                                                        assignment_number)

    dictionary = {
        "information": hw_info,
        "headers": ("Student", "Grade"),
        "grades": hw_grades,
        "course_id":course_id,
        "sec_no":sec_no
    }


    return make_response(render_template('courses/student_grades.html',
                                         assignment=dictionary,
                                         assignment_type="Homework",
                                         grade_id=grade_id))

def render_exam_information(course_id, sec_no, assignment_number, grade_id):
    exam_info = course_management_api.get_exam_information(course_id,
                                                             sec_no,
                                                             assignment_number)

    exam_grades = course_management_api.get_exam_grades_for_professor(course_id,
                                                                      sec_no,
                                                                      assignment_number)

    dictionary = {
        "information": exam_info,
        "headers": ("Student", "Grade"),
        "grades": exam_grades,
        "course_id":course_id,
        "sec_no":sec_no
    }

    return make_response(render_template('courses/student_grades.html',
                                         assignment=dictionary,
                                         assignment_type="Exam",
                                         grade_id=grade_id))

def render_capstone_project_information(course_id, sec_no, assignment_number, grade_id):
    course_info = course_management_api.get_capstone_project_information(course_id,
                                                                         sec_no,
                                                                         assignment_number)

    team_grades = course_management_api.get_capstone_project_team_grades(course_id,
                                                                         sec_no,
                                                                         assignment_number)

    dictionary = {
        "information": course_info,
        "headers": ("Team", "Grade"),
        "grades": team_grades,
        "course_id":course_id,
        "sec_no":sec_no
    }

    return make_response(render_template('courses/team_capstone_grades.html',
                                         assignment=dictionary,
                                         assignment_type="capstone",
                                         grade_id=grade_id))

def render_student_capstone_project_information(course_id, sec_no, project_no):
    course_info = course_management_api.get_capstone_project_information(course_id,
                                                                         sec_no,
                                                                         project_no)
    dictionary = {
        "information": course_info,
        "course_id":course_id,
        "sec_no":sec_no
    }

    return make_response(render_template('courses/capstone_project_info.html',
                                         assignment=dictionary,
                                         assignment_type="capstone"))


def render_all_courses():
    data = course_management_api.get_all_courses()
    return make_response(render_template("table_listing.html",
                                         headers=data["headers"],
                                         link_prefix="courses",
                                         data_2d=data["course_info"]
                                         )
                         )

def render_course_info(user_email, user_type, course_id):
    data = course_management_api.get_course_section_infomation(user_email, user_type, course_id)
    teaching = False
    if user_type == USER.PROFESSOR:
        teaching = course_management_api.check_professor_teaches_section(user_email, course_id)

    return make_response(render_template("courses/course_listing_single_course.html",
                                         course_info=data["course_info"],
                                         sections=data["sections"],
                                         user_type=user_type,
                                         teaching=teaching
                                         )
                         )

def render_add_assignment_info(user_email, course_id, sec_no):
    teaches = course_management_api.check_professor_teaches_section(user_email, course_id)
    if not teaches:
        return render_error("You are not allowed to access this page")

    section_type = course_management_api.get_section_type(course_id, sec_no)
    professor_emails = None
    if section_type == "Cap":
        professor_emails = course_management_api.get_all_professor_emails()
    return make_response(render_template('courses/add_assignment.html',
                                         course_id=course_id,
                                         sec_no=sec_no,
                                         professor_emails=professor_emails
                                         )
                         )

def handle_add_assignment(course_id, sec_no, form):
    assignment_type = form["type"]

    if assignment_type == "homework":
        description = form["description"]
        return handle_add_homework(course_id, sec_no, description)
    elif assignment_type == "exam":
        description = form["description"]
        return handle_add_exam(course_id, sec_no, description)
    else:
        mentor_email = form["email"]
        return handle_add_capstone(course_id, sec_no, mentor_email)

def handle_add_homework(course_id, sec_no, description):
    hw_num = course_management_api.get_next_homework_number(course_id, sec_no)

    new_homework = Homework(course_id, sec_no, hw_num, description)
    course_management_api.insert_homework(new_homework)
def handle_add_exam(course_id, sec_no, description):
    exam_num = course_management_api.get_next_exam_number(course_id, sec_no)

    new_exam = Exams(course_id, sec_no, exam_num, description)
    course_management_api.insert_exam(new_exam)

def handle_add_capstone(course_id, sec_no, mentor_email):
    cs_num = course_management_api.get_next_capstone_number(course_id, sec_no)
    project = Capstone_section(course_id, sec_no, cs_num, mentor_email)
    course_management_api.insert_capstone_section(project)

def handle_add_project_team(course_id, sec_no, project_number):
    next_team_number = course_management_api.get_next_capstone_team(course_id, sec_no, project_number)
    team = Capstone_Team(course_id, sec_no, next_team_number, project_number)
    course_management_api.insert_capstone_team(team)

def redirect_to_login():
    return redirect(host)