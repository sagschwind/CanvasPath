import sqlite3 as sql
from Utility import USER, DATABASE_NAME
from database.TableSchema import *

# Needed to call when professor are inserted into the table since
# The student's need to be uploaded first so the data set has no
# Idea the professor team is
def update_section_teaching_team(team_id, course_id, connection):
    dictionary = {
        "team_id": team_id,
        "course_id": course_id
    }

    statement = """
    UPDATE Sections
    SET prof_team_id = :team_id
    WHERE course_id = :course_id;
    """
    cursor = connection.execute(statement, dictionary)
    connection.commit()

# Get every single section and course the student is in
def get_students_sections(user_email):
    dictionary = {"email": user_email}
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Course.course_id, Sections.sec_no, Course.course_name
    FROM Enrolls, Sections, Course
    WHERE Enrolls.course_id = Sections.course_id
    AND Enrolls.sec_no = Sections.sec_no
    AND Sections.course_id = Course.course_id
    AND Enrolls.student_email = :email
    ORDER BY Course.course_id ASC, Sections.sec_no ASC;
    """
    cursor = connection.execute(statement, dictionary)
    courses = cursor.fetchall()
    connection.close()
    return {
        "headers" : ("Course", "Name"),
        "data" : courses
    }

def get_all_students():
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Student.name, Student.email
    FROM Student
    ORDER BY Student.name ASC;
    """

    cursor = connection.execute(statement)

    return cursor.fetchall()


# Drop a student's course section
def drop_student_section(student_email, course_id, sec_no):
    dictionary = {
        "email": student_email,
        "course_id": course_id,
        "sec_no": sec_no
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    DELETE FROM Enrolls
    WHERE Enrolls.student_email = :email
    AND Enrolls.course_id = :course_id
    AND Enrolls.sec_no = :sec_no;
    """
    cursor = connection.execute(statement, dictionary)
    result = cursor.rowcount

    if result > 1:
        print("Drop course:", dictionary, "\nDeleted:", result)

    connection.commit()
    connection.close()

def remove_professor_from_teaching_team(professor_email, course_id):
    pass

# Add student to a course section
def add_student_section(student_email, course_id, sec_no):
    enrollment = Enrolls(student_email, course_id, sec_no)
    return add_enroll_object(enrollment)

# Add a professor to the teaching team of the course
def add_professor_to_teaching_team(professor_email, team_id):
    team_member = Prof_team_members(professor_email, team_id)

    connection = sql.connect(DATABASE_NAME)
    team_member.bootup_insert(connection)
    connection.close()

def drop_professor_from_teaching_team(professor_email, team_id):
    dictionary = {
        "email": professor_email,
        "team_id": team_id
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    DELETE
    FROM Prof_team_members
    WHERE Prof_team_members.prof_email = :email
    AND Prof_team_members.team_id = :team_id;
    """

    connection.execute(statement, dictionary)
    connection.commit()
    connection.close()

# Add enrollment object to enroll table
def add_enroll_object(enrollment):
    dictionary = enrollment.__dict__

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Sections.enroll_limit
    FROM Sections
    WHERE Sections.course_id = :course_id
    AND Sections.sec_no = :sec_no;
    """
    cursor = connection.execute(statement, dictionary)
    limit = cursor.fetchone()


    if limit is None:
        raise Exception("Trying to add section of course that doesn't exist")

    limit = limit[0]

    statement = """
    SELECT Count(*)
    FROM Enrolls
    WHERE Enrolls.course_id = :course_id
    AND Enrolls.sec_no = :sec_no;
    """

    cursor = connection.execute(statement, dictionary)
    num_students = cursor.fetchone()

    if num_students is None:
        raise Exception("Trying to add section of course that doesn't exist")

    num_students = num_students[0]

    if num_students > limit:
        print("Error students exceed {} - {} seat limit".format(enrollment.course_id, enrollment.sec_no))

    if num_students >= limit:
        return "{} - {} is already full".format(enrollment.course_id, enrollment.sec_no)

    enrollment.insert(connection)
    connection.close()

# Get all courses for students to look at all courses
def get_all_courses():
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Course.course_id, Course.course_name, Course.course_description, Count(Sections.course_id)
    FROM Course
    LEFT JOIN Sections
    ON Sections.course_id = Course.course_id
    GROUP BY Course.course_id;
    """

    cursor = connection.execute(statement)
    course_info = cursor.fetchall()

    results = {
        "headers": ("Course ID", "Name", "Description", "Number of Sections"),
        "course_info": course_info
    }
    return results

# Get basic course info
def get_basic_section_info(course_id, sec_no):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Sections.course_id, Sections.sec_no, Sections.section_type, Sections.prof_team_id
    FROM Sections, Course
    WHERE Sections.course_id = Course.course_id
    AND Sections.course_id = :course_id
    AND Sections.sec_no = :sec_no
    ORDER BY Sections.course_id;
    """

    cursor = connection.execute(statement, dictionary)
    course_info = cursor.fetchone()
    team_id = course_info[-1]

    dictionary = {
        "team_id": team_id
    }
    print("Team id:", team_id)
    statement = """
    SELECT Professor.name, Professor.email
    FROM Prof_team_members, Professor
    WHERE Prof_team_members.prof_email = Professor.email
    AND Prof_team_members.team_id = :team_id;
    """

    cursor = connection.execute(statement, dictionary)
    professors = cursor.fetchall()

    course_info_string = course_info[0] + " - " + str(course_info[1])
    if course_info[2] == "Cap":
        course_info_string += " (Capstone)"

    if len(professors) == 0:
        print("Changing professors")
        professors = None

    return {
        "course_info": course_info_string,
        "professors": professors
    }

def get_team_id(course_id, sec_no):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Sections.prof_team_id
    FROM Sections
    WHERE Sections.course_id = :course_id
    AND Sections.sec_no = :sec_no;
    """

    cursor = connection.execute(statement, dictionary)

    return cursor.fetchone()[0]

def check_student_in_section(student_email, course_id, sec_no):
    dictionary = {
        "student_email": student_email,
        "course_id": course_id,
        "sec_no": sec_no
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT *
    FROM Enrolls
    WHERE Enrolls.student_email = :student_email
    AND Enrolls.course_id = :course_id
    AND Enrolls.sec_no = :sec_no;
    """
    cursor = connection.execute(statement, dictionary)
    grades = cursor.fetchall()
    return len(grades) != 0

# Get a student homework grades for a specfic class section
def get_homework_grades(student_email, course_id, sec_no):
    dictionary = {
        "email": student_email,
        "course_id": course_id,
        "sec_no": sec_no
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Homework_grades.hw_no, Homework.hw_details, Homework_grades.grade
    FROM Homework_grades, Homework
    WHERE Homework.sec_no = Homework_grades.sec_no

    AND Homework.course_id = Homework_grades.course_id
    AND Homework_grades.student_email = :email
    AND Homework.course_id = :course_id
    AND Homework.sec_no = :sec_no;
    """
    cursor = connection.execute(statement, dictionary)
    grades = cursor.fetchall()
    return None if len(grades) == 0 else grades

# Get a student exams grades for a specfic class section
def get_exam_grades(student_email, course_id, sec_no):
    dictionary = {
        "email": student_email,
        "course_id": course_id,
        "sec_no": sec_no
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Exams.exam_no, Exams.exam_details, Exam_grades.grades
    FROM Exam_grades, Exams
    WHERE Exams.sec_no = Exam_grades.sec_no
    AND Exams.exam_no = Exam_grades.exam_no
    AND Exams.course_id = Exam_grades.course_id

    AND Exam_grades.student_email = :email
    AND Exam_grades.course_id = :course_id
    AND Exam_grades.sec_no = :sec_no
    ORDER BY Exams.exam_no
    """
    cursor = connection.execute(statement, dictionary)
    grades = cursor.fetchall()
    return None if len(grades) == 0 else grades

# Get student's grades on capstone projects, returns None if no projects
def get_capstone_grade(student_email, course_id, sec_no):
    dictionary = {
        "email": student_email,
        "course_id": course_id,
        "sec_no": sec_no
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Capstone_section.project_no, Capstone_Team.team_id, Capstone_grades.grade, Capstone_section.sponsor_id, Professor.name
    FROM Capstone_section, Capstone_grades, Capstone_Team, Capstone_Team_Members, Professor

    /* START: Match variables */
    WHERE Capstone_section.course_id = :course_id
    AND Capstone_section.sec_no = :sec_no
    AND Capstone_Team_Members.student_email = :email
    /* END: Match Variable */

    /* Link Capstone <-> Capstone_team */
    AND Capstone_section.course_id = Capstone_team.course_id
    AND Capstone_section.sec_no = Capstone_team.sec_no
    AND Capstone_section.project_no = Capstone_team.project_no

    /* Link Capstone_Team <-> Capstone_Team_Members */
    AND Capstone_Team.team_id = Capstone_Team_Members.team_id
    AND Capstone_Team.course_id = Capstone_Team_Members.course_id
    AND Capstone_Team.sec_no = Capstone_Team_Members.sec_no

    /* Link Capstone_Team_Members <-> Capstone_grades */
    AND Capstone_Team_Members.team_id = Capstone_grades.team_id
    AND Capstone_Team_Members.sec_no = Capstone_grades.sec_no
    AND Capstone_Team_Members.course_id = Capstone_grades.course_id

    /* Link Capstone_section <-> Professor */
    AND Capstone_section.sponsor_id = Professor.email
    ORDER BY Capstone_section.project_no
    """
    cursor = connection.execute(statement, dictionary)
    grades = cursor.fetchall()
    return None if len(grades) == 0 else grades

# Get all section's information
def get_course_section_infomation(user_email, user_type, course_id):
    dictionary = {
        "course_id": course_id
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Course.course_id, Course.course_name, Course.course_description
    FROM Course
    WHERE Course.course_id = :course_id;
    """

    cursor = connection.execute(statement, dictionary)
    course_info = cursor.fetchone()

    #  Sections.enroll_limit - Count(*) AS Seats_open
    statement = """
    SELECT Sections.sec_no,
    case when Sections.section_type = "Reg" then "Regular" else "Capstone" end,
    case when Count(*) = Sections.enroll_limit then "Full" else Sections.enroll_limit - Count(Enrolls.sec_no) end,
    Sections.enroll_limit
    FROM Sections
    LEFT JOIN Enrolls
    ON Sections.course_id = Enrolls.course_id
    AND Sections.sec_no = Enrolls.sec_no
    WHERE Sections.course_id = :course_id
    GROUP BY Sections.sec_no;
    """

    cursor = connection.execute(statement, dictionary)
    sections = cursor.fetchall()

    dictionary = {
        "student_email": user_email,
        "course_id": course_id
    }

    statement = """
    SELECT Enrolls.sec_no
    FROM Enrolls
    WHERE Enrolls.course_id = :course_id
    AND Enrolls.student_email = :student_email;
    """

    cursor = connection.execute(statement, dictionary)
    enrolled_in = cursor.fetchone()
    if enrolled_in is not None:
        enrolled_in = enrolled_in[0]

    def get_modified_sections(user_type, sections, enrolled_in):
        def get_student_action(user_type, section, enrolled_in):
            if user_type == USER.PROFESSOR:
                return None
            # Needs to be before 'Full' or else someone in a full class can't drop
            if section[0] == enrolled_in:
                return "Drop"
            elif section[2] == "Full":
                return "Full"
            elif enrolled_in is None:
                return "Add"
            else:
                return "Already in Section {}".format(enrolled_in)


        return [list(section) + [get_student_action(user_type, section, enrolled_in)]
                for section in sections]

    data = {
        "course_info": course_info,
        "sections": get_modified_sections(user_type, sections, enrolled_in)
    }
    return data

def get_professor_courses(prof_email):
    dictionary = {
        "email": prof_email
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Sections.course_id, Sections.sec_no, COUNT(*)
    FROM Prof_team_members, Sections, Enrolls
    WHERE Prof_team_members.team_id = Sections.prof_team_id
    AND Sections.course_id = Enrolls.course_id
    AND Sections.sec_no = Enrolls.sec_no
    AND Prof_team_members.prof_email = :email
    GROUP BY Sections.course_id, Sections.sec_no;
    """

    cursor = connection.execute(statement, dictionary)
    sections = cursor.fetchall()

    return {
        "headers": ("Sections", "Students"),
        "data": sections
    }

def check_professor_teaches_section(professor_email, course_id):
    dictionary = {
        "professor_email": professor_email,
        "course_id": course_id
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT *
    FROM Prof_team_members, Sections
    WHERE Prof_team_members.team_id = Sections.prof_team_id
    AND Prof_team_members.prof_email = :professor_email
    AND Sections.course_id = :course_id;
    """
    cursor = connection.execute(statement, dictionary)
    grades = cursor.fetchall()

    return len(grades) != 0

def get_section_type(course_id, sec_no):
    dictionary = {
        "sec_no": sec_no,
        "course_id": course_id
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Sections.section_type
    FROM Sections
    WHERE Sections.course_id = :course_id
    AND Sections.sec_no = :sec_no;
    """

    cursor = connection.execute(statement, dictionary)
    type = cursor.fetchone()
    return type[0]

def get_homework_assignments(course_id, sec_no):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Homework.hw_no, Homework.hw_details
    FROM Homework
    WHERE Homework.course_id = :course_id
    AND Homework.sec_no = :sec_no
    ORDER BY Homework.hw_no;
    """
    cursor = connection.execute(statement, dictionary)
    homeworks = cursor.fetchall()
    return None if len(homeworks) == 0 else homeworks

def get_exams(course_id, sec_no):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Exams.exam_no, Exams.exam_details
    FROM Exams
    WHERE Exams.course_id = :course_id
    AND Exams.sec_no = :sec_no
    ORDER BY Exams.exam_no;
    """
    cursor = connection.execute(statement, dictionary)
    exams = cursor.fetchall()
    return None if len(exams) == 0 else exams

def get_capstone_projects(course_id, sec_no):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Capstone_section.project_no, Capstone_section.sponsor_id, COUNT(Capstone_Team.project_no)
    FROM Capstone_section
    LEFT JOIN Capstone_Team
    ON Capstone_section.course_id = Capstone_Team.course_id
    AND Capstone_section.sec_no = Capstone_Team.sec_no
    AND Capstone_section.project_no = Capstone_Team.project_no
    WHERE Capstone_section.course_id = :course_id
    AND Capstone_section.sec_no = :sec_no
    GROUP BY Capstone_section.project_no
    ORDER BY Capstone_section.project_no;
    """
    cursor = connection.execute(statement, dictionary)
    projects = cursor.fetchall()

    return None if len(projects) == 0 else projects

def get_homework_information(course_id, sec_no, assignment_number):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no,
        "assignment_number": assignment_number
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Homework.hw_no, Homework.hw_details
    FROM Homework
    WHERE Homework.course_id = :course_id
    AND Homework.sec_no = :sec_no
    AND Homework.hw_no = :assignment_number;
    """
    cursor = connection.execute(statement, dictionary)
    homework = cursor.fetchone()
    return homework

def get_exam_information(course_id, sec_no, assignment_number):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no,
        "assignment_number": assignment_number
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Exams.exam_no, Exams.exam_details
    FROM Exams
    WHERE Exams.course_id = :course_id
    AND Exams.sec_no = :sec_no
    AND Exams.exam_no = :assignment_number;
    """
    cursor = connection.execute(statement, dictionary)
    exam = cursor.fetchone()
    return exam

def get_homework_grades_for_professor(course_id, sec_no, assignment_number):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no,
        "assignment_number": assignment_number
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Student.name, Homework_grades.grade, Student.email
    FROM Student, Enrolls
    LEFT JOIN Homework_grades
    ON Student.email = Homework_grades.student_email
    AND Homework_grades.course_id = :course_id
    AND Homework_grades.sec_no = :sec_no
    AND Homework_grades.hw_no = :assignment_number
    WHERE Student.email = Enrolls.student_email
    AND Enrolls.course_id = :course_id
    AND Enrolls.sec_no = :sec_no
    ORDER BY Student.name;
    """
    cursor = connection.execute(statement, dictionary)
    homework_grades = cursor.fetchall()
    return homework_grades

def get_exam_grades_for_professor(course_id, sec_no, assignment_number):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no,
        "assignment_number": assignment_number
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Student.name, Exam_grades.grades, Student.email
    FROM Student, Enrolls
    LEFT JOIN Exam_grades
    ON Student.email = Exam_grades.student_email
    AND Exam_grades.course_id = :course_id
    AND Exam_grades.sec_no = :sec_no
    AND Exam_grades.exam_no = :assignment_number
    WHERE Student.email = Enrolls.student_email
    AND Enrolls.course_id = :course_id
    AND Enrolls.sec_no = :sec_no
    ORDER BY Student.name;
    """

    cursor = connection.execute(statement, dictionary)
    exam_grades = cursor.fetchall()
    return exam_grades

def get_next_homework_number(course_id, sec_no):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Max(Homework.hw_no)
    FROM Homework
    WHERE Homework.course_id = :course_id
    AND Homework.sec_no = :sec_no;
    """

    cursor = connection.execute(statement, dictionary)
    homework_num = cursor.fetchone()

    if homework_num is None:
        return 1
    else:
        return homework_num[0] + 1

def insert_homework(homework):
    connection = sql.connect(DATABASE_NAME)
    homework.insert(connection)
    connection.close()

def get_next_exam_number(course_id, sec_no):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Max(Exams.exam_no)
    WHERE Exams.course_id = :course_id
    AND Exams.sec_no = :sec_no;
    """

    cursor = connection.execute(statement, dictionary)
    exam_num = cursor.fetchone()
    if exam_num is None:
        return 1
    return exam_num[0]

def insert_exam(exam):
    connection = sql.connect(DATABASE_NAME)
    exam.insert(connection)
    connection.close()

def get_next_capstone_number(course_id, sec_no):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no
    }
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Capstone_section.project_no
    FROM Capstone_section
    WHERE Capstone_section.course_id = :course_id
    AND Capstone_section.sec_no = :sec_no
    ORDER BY Capstone_section.project_no DESC;
    """

    cursor = connection.execute(statement, dictionary)
    cs_num = cursor.fetchone()

    if cs_num is None:
        return 1
    return cs_num[0]

def update_homework_grade(homework_grade):
    connection = sql.connect(DATABASE_NAME)
    homework_grade.bootup_insert(connection)
    connection.close()

def update_exam_grade(exam_grade):
    connection = sql.connect(DATABASE_NAME)
    exam_grade.bootup_insert(connection)
    connection.close()

def get_all_professor_emails():
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Professor.email
    FROM Professor
    ORDER BY Professor.email ASC;
    """

    cursor = connection.execute(statement)
    return [val[0] for val in cursor.fetchall()]

def get_all_professors():
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Professor.name, Professor.email
    FROM Professor
    ORDER BY Professor.email ASC;
    """

    cursor = connection.execute(statement)
    return cursor.fetchall()

def insert_capstone_section(section):
    connection = sql.connect(DATABASE_NAME)
    section.insert(connection)
    connection.close()

def get_capstone_project_information(course_id, sec_no, project_no):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no,
        "project_no": project_no
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Capstone_section.project_no, Capstone_section.sponsor_id, Professor.name
    FROM Capstone_section, Professor
    WHERE Capstone_section.course_id = :course_id
    AND Capstone_section.sec_no = :sec_no
    AND Capstone_section.project_no = :project_no
    AND Capstone_section.sponsor_id = Professor.email;
    """

    cursor = connection.execute(statement, dictionary)
    info = cursor.fetchone()
    return info

def get_capstone_project_team_grades(course_id, sec_no, project_no):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no,
        "project_no": project_no
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Capstone_Team.team_id, Capstone_grades.grade
    FROM Capstone_Team

    LEFT JOIN Capstone_grades
    ON Capstone_grades.team_id = Capstone_Team.team_id
    AND Capstone_grades.course_id = Capstone_Team.course_id
    AND Capstone_grades.sec_no = Capstone_Team.sec_no

    WHERE Capstone_Team.course_id = :course_id
    AND Capstone_Team.sec_no = :sec_no
    AND Capstone_Team.project_no = :project_no;
    """

    cursor = connection.execute(statement, dictionary)
    info = cursor.fetchall()

    return info

def get_next_capstone_team(course_id, sec_no, project_no):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no,
        "project_no": project_no
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Capstone_Team.team_id
    FROM Capstone_Team
    WHERE Capstone_Team.course_id = :course_id
    AND Capstone_Team.sec_no = :sec_no
    AND Capstone_Team.project_no = :project_no
    ORDER BY Capstone_Team.team_id DESC;
    """

    cursor = connection.execute(statement, dictionary)

    team_num = cursor.fetchone()

    if team_num is None:
        return 1
    return int(team_num[0]) + 1

def insert_capstone_team(team):
    connection = sql.connect(DATABASE_NAME)
    team.insert(connection)
    connection.close()

def update_capstone_team_grade(capstone_grade):
    connection = sql.connect(DATABASE_NAME)
    capstone_grade.bootup_insert(connection)
    connection.close()

def get_students_in_section(course_id, sec_no):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Student.name, Student.email
    FROM Student
    JOIN Enrolls
    ON Student.email = Enrolls.student_email
    WHERE Enrolls.course_id = :course_id
    AND Enrolls.sec_no = :sec_no
    ORDER BY Student.name;
    """

    cursor = connection.execute(statement, dictionary)

    students = cursor.fetchall()

    return students

def delete_course(course_id):
    dictionary = {
        "course_id": course_id
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    DELETE
    FROM Course
    WHERE Course.course_id = :course_id;
    """

    connection.execute(statement, dictionary)
    connection.commit()
    connection.close()

def insert_course(course):
    connection = sql.connect(DATABASE_NAME)
    course.bootup_insert(connection)
    connection.close()

def insert_section(section):
    connection = sql.connect(DATABASE_NAME)
    section.bootup_insert(connection)
    connection.close()

def get_next_section_number(course_id):
    dictionary = {
        "course_id": course_id
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Max(Sections.sec_no)
    FROM Sections
    WHERE Sections.course_id = :course_id;
    """

    cursor = connection.execute(statement, dictionary)

    val = cursor.fetchone()[0]
    if val is None:
        return 1
    return val + 1