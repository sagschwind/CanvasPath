import sqlite3 as sql
import os
from TableSchema import *
import csv

DATABASE_NAME = 'database.db'
DEBUG = True
GENERATE_TABLE_SCHEMA = False

TABLE_COMMANDS = {"Department": """
    CREATE TABLE Department(
    dept_id TEXT PRIMARY KEY NOT NULL,
    dept_name TEXT NOT NULL,
    dept_head TEXT NOT NULL
    );
    """,
                  "Zipcode": """
    CREATE TABLE Zipcode(
    zipcode INT PRIMARY KEY NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL
    );
    """,
                  "Student": """
    CREATE TABLE Student(
    email TEXT PRIMARY KEY NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    age INT NOT NULL,
    gender CHAR NOT NULL,
    major TEXT NOT NULL,
    street TEXT NOT NULL,
    zipcode INT NOT NULL,
    FOREIGN KEY(zipcode) REFERENCES Zipcode(zipcode)
    );
    """,
                  "Professor": """
    CREATE TABLE Professor(
    email TEXT PRIMARY KEY NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    age INT NOT NULL,
    gender CHAR NOT NULL,
    office_address TEXT NOT NULL,
    department TEXT NOT NULL,
    title TEXT NOT NULL,
    FOREIGN KEY(department) REFERENCES Department(dept_id)
    );
    """,
                  "Course": """
CREATE TABLE Course(
course_id TEXT PRIMARY KEY NOT NULL,
course_name TEXT NOT NULL,
course_description TEXT NOT NULL
);
""",
                  "Prof_teams": """
    CREATE TABLE Prof_teams(
    team_id TEXT PRIMARY KEY NOT NULL
    );
    """,
                  "Prof_team_members": """
                  CREATE TABLE Prof_team_members(
                  prof_email TEXT NOT NULL,
                  team_id TEXT NOT NULL,
                  PRIMARY KEY(prof_email, team_id),
                  FOREIGN KEY(prof_email) REFERENCES Professor(email),
                  FOREIGN KEY(team_id) REFERENCES Prof_teams(team_id)
                  );
                  """,

                  # TODO: implement a constraint for enroll_limit
                  "Sections":"""
                  CREATE TABLE Sections(
                  course_id TEXT NOT NULL,
                  sec_no INT NOT NULL,
                  section_type TEXT NOT NULL,
                  enroll_limit INT NOT NULL,
                  prof_team_id TEXT NOT NULL,
                  PRIMARY KEY(course_id, sec_no),
                  FOREIGN KEY (course_id) REFERENCES Course(course_id),
                  FOREIGN KEY (prof_team_id) REFERENCES Prof_teams(team_id)
                  );
                  """,
                  "Enrolls":"""
                  CREATE TABLE Enrolls(
                  student_email TEXT NOT NULL,
                  course_id TEXT NOT NULL,
                  sec_no INT NOT NULL,
                  PRIMARY KEY(student_email, course_id, sec_no),
                  FOREIGN KEY(student_email) REFERENCES Student(email),
                  FOREIGN KEY(course_id, sec_no) REFERENCES Sections(course_id, sec_no)
                  );
                  """,
                  "Homework":"""
                  CREATE TABLE Homework(
                  course_id TEXT NOT NULL,
                  sec_no INT NOT NULL,
                  hw_no INT NOT NULL,
                  hw_details TEXT NOT NULL,
                  PRIMARY KEY(course_id, sec_no, hw_no),
                  FOREIGN KEY (course_id, sec_no) REFERENCES Sections(course_id, sec_no)
                  );
                  """,
                  "Homework_grades":"""
                  CREATE TABLE Homework_grades(
                  student_email TEXT NOT NULL,
                  course_id TEXT NOT NULL,
                  sec_no INT NOT NULL,
                  hw_no INT NOT NULL,
                  grade REAL NOT NULL,
                  PRIMARY KEY(student_email, course_id, sec_no, hw_no),
                  FOREIGN KEY (student_email) REFERENCES Student(email),
                  FOREIGN KEY (course_id, sec_no, hw_no) REFERENCES Homework(course_id, sec_no, hw_no)
                  );
                  """,
                  "Exams":"""
                  CREATE TABLE Exams(
                  course_id TEXT NOT NULL,
                  sec_no INT NOT NULL,
                  exam_no INT NOT NULL,
                  exam_details TEXT NOT NULL,
                  PRIMARY KEY(course_id, sec_no, exam_no),
                  FOREIGN KEY (course_id, sec_no) REFERENCES Sections(course_id, sec_no)
                  );
                  """,
                  "Exam_grades":"""
                  CREATE TABLE Exam_grades(
                  student_email TEXT NOT NULL,
                  course_id TEXT NOT NULL,
                  sec_no INT NOT NULL,
                  exam_no INT NOT NULL,
                  grades REAL NOT NULL,
                  PRIMARY KEY(student_email, course_id, sec_no, exam_no),
                  FOREIGN KEY (student_email) REFERENCES Student(email),
                  FOREIGN KEY (course_id, sec_no, exam_no) REFERENCES Exams(course_id, sec_no, exam_no)
                  );
                  """,
                  "Capstone_section":"""
                  CREATE TABLE Capstone_section(
                  course_id TEXT NOT NULL,
                  sec_no INT NOT NULL,
                  project_no INT NOT NULL,
                  sponsor_id TEXT NOT NULL,
                  PRIMARY KEY(course_id, sec_no, project_no),
                  FOREIGN KEY (course_id, sec_no) REFERENCES Sections(course_id, sec_no),
                  FOREIGN KEY (sponsor_id) REFERENCES Professor(email)
                  );
                  """,
                  "Capstone_Team":"""
                  CREATE TABLE Capstone_Team(
                  course_id TEXT NOT NULL,
                  sec_no INT NOT NULL,
                  team_id TEXT NOT NULL,
                  project_no INT NOT NULL,
                  PRIMARY KEY(course_id, sec_no, team_id),
                  FOREIGN KEY (course_id, sec_no, project_no) References Capstone_section(course_id, sec_no, project_no)
                  );
                  """,
                  "Capstone_Team_Members":"""
                  CREATE TABLE Capstone_Team_Members(
                  student_email TEXT NOT NULL,
                  team_id TEXT NOT NULL,
                  course_id TEXT NOT NULL,
                  sec_no INT NOT NULL,
                  PRIMARY KEY(team_id, course_id, sec_no),
                  FOREIGN KEY (student_email) REFERENCES Student(email),
                  FOREIGN KEY (team_id, course_id, sec_no) REFERENCES Capstone_Team(team_id, course_id, sec_no)
                  );
                  """,
                  "Capstone_grades": """
                  CREATE TABLE Capstone_grades(
                  course_id TEXT NOT NULL,
                  sec_no INT NOT NULL,
                  team_id TEXT NOT NULL,
                  grade REAL NOT NULL,
                  PRIMARY KEY(course_id, sec_no, team_id),
                  FOREIGN KEY (course_id, sec_no, team_id) REFERENCES Capstone_Team(course_id, sec_no, team_id)
                  );
                  """}

# All tables in schema
NEEDED_TABLES = ["Student", "Zipcode", "Professor", "Department", "Course",
                 "Sections", "Enrolls", "Prof_teams", "Prof_team_members",
                 "Homework", "Homework_grades", "Exams", "Exam_grades",
                 "Capstone_section", "Capstone_Team", "Capstone_Team_Members",
                 "Capstone_grades"]

def start_database(db_name='database.db'):
    DATABASE_NAME = db_name

    if DEBUG:
        try:
            os.remove(DATABASE_NAME)
        except OSError:
            pass

    exists = os.path.isfile(DATABASE_NAME)
    if not exists:
        connection = sql.connect(DATABASE_NAME)
        create_tables(connection)
        upload_all_data_helper(connection)


"""
Creates all tables necessary for data base
Prints out debug information if DEBUG = True
Prints out table schema if GENERATE_TABLE_SCHEMA = True
"""
def create_tables(connection):
    for table_name, sql_command in TABLE_COMMANDS.items():
        create_table(connection, table_name, sql_command)
        NEEDED_TABLES.remove(table_name)

    # Check to see what tables need to be inserted
    if DEBUG:
        for table in NEEDED_TABLES:
            print(table, "- x made")
        print("Tables created\n")

    if GENERATE_TABLE_SCHEMA:
        generate_schema_data(connection)

"""
Creates a table named table_name by running create_command
"""
def create_table(connection, table_name, create_command):
    if DEBUG:
        print("Creating Table:", table_name, end=" ")
    connection.execute(create_command)
    connection.commit()

    if DEBUG:
         test_table_created(table_name, connection)
    # cursor = connection.execute("SELECT * FROM " +table_name)
    # print(table_name, [description[0] for description in cursor.description])

"""
Tests to see if table by the name of table_name exists
"""
def test_table_created(table_name, connection):
    cursor = connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=:table_name;",
                                {"table_name": table_name})
    if cursor.fetchone()[0]:
        print("✔")
    else:
        print("X")

"""
Generates schema data of all tables in TABLE_COMMANDS
"""
def generate_schema_data(connection):
    print("\n# Schema generated by bootup")
    for table_name in TABLE_COMMANDS.keys():
        generate_schema(table_name, connection)

"""
Generates schema of specific table table_name as a python class
"""
def generate_schema(table_name, connection):
    switch = {"TEXT": "#TEXT",
              "INT":"#INT",
              "REAL": "#REAL",
              "CHAR": "#CHAR"}

    cursor = connection.execute("PRAGMA TABLE_INFO("+table_name+")")
    print("\nclass " + table_name + "(base):")
    rows = []
    results = cursor.fetchall()
    for row in results:
        rows += [row[1]]
    print("    def __init__(self, " + ", ".join(rows) + "):")
    for row in results:
        print("        self." + row[1], "=", row[1], switch[row[2]])

def upload_all_data_helper(connection):
    upload_data_from("Bootfiles/Students.csv", upload_student_data, connection)
    upload_data_from("Bootfiles/Professors.csv", upload_professor_data, connection)
def upload_data_from(filename, upload_handler, connection):
    print("Uploading", filename, "datum")
    with open(filename) as students:
        csv_list = list(csv.reader(students))
        enum = enumerate(csv_list)

        headers = next(enum)[1]
        # Get a dict of all the column names
        header_dict = dict((y,x) for x,y in enumerate(headers))

        for entry in enum:
            upload_handler(header_dict, entry[1], connection)
    cursor = connection.execute("SELECT * FROM Sections;")

# This returns a function that gets the value of s_line
# according to the dict ket from h_dict, which maps excel
# column title to column index
def g_data(h_dict, s_line):
    def function(key):
        return s_line[h_dict[key]]
    return function

# Each student is in multiple courses
def handle_course(student_email, course_info, connection):
    course = Course(
        course_info[0],
        course_info[1],
        course_info[2]
    )
    course.bootup_insert(connection)
    # insert_course(course, connection)

    section = Sections(
        course.course_id,
        int(float(course_info[4])),
        course_info[3],
        course_info[5],
        "NULL" # Prof team not chosen yet
    )
    section.bootup_insert(connection)
    # insert_section(section, connection)

    # Handle homework
    if course_info[6] != '': # True if there is a homework assignment
        homework = Homework(
            course.course_id,
            section.sec_no,
            int(float(course_info[6])),
            course_info[7]
        )
        homework.bootup_insert(connection)
        # insert_homework(homework, connection)
        if course_info[8] != '': # True if there is no grade
            hw_grade = Homework_grades(
                student_email,
                homework.course_id,
                homework.sec_no,
                homework.hw_no,
                int(float(course_info[8]))
            )
            hw_grade.bootup_insert(connection)
            # insert_hw_grade(hw_grade, connection)

    # Handle course homework
    if course_info[9] != '':
        exam = Exams(
            course.course_id,
            section.sec_no,
            int(float(course_info[9])),
            course_info[10]
        )
        exam.bootup_insert(connection)
        # insert_exam(exam, connection)
        if course_info[11] != '':
            ex_grades = Exam_grades(
                student_email,
                exam.course_id,
                exam.sec_no,
                exam.exam_no,
                int(float(course_info[11]))
            )
            ex_grades.bootup_insert(connection)

def upload_student_data(h_dict, s_line, connection):
    get_value = g_data(h_dict, s_line)
    zipcode = Zipcode(
        get_value("Zip"),
        get_value("City"),
        get_value("State")
    )
    zipcode.bootup_insert(connection)

    student = Student(
        get_value("Email"),
        get_value("Password"),
        get_value("Full Name"),
        get_value("Age"),
        get_value("Gender"),
        get_value("Major"),
        get_value("Street"),
        get_value("Zip")
    )
    student.bootup_insert(connection)

    # ranges for each course
    # 11 - 22
    # 23 - 34
    # 34 - 45
    for i in range(11, 47, 12):
        handle_course(student.email, s_line[i:i+12], connection)

def upload_professor_data(h_dict, p_line, connection):
    # Data scrubbing since the office number got seperated from building number
    line = [i for i in p_line]
    item = line.pop(7)
    line[6] += "," + item
    line[6] = line[6].strip("\"")
    get_value = g_data(h_dict, line)

    if get_value("Title") == "Head":
        dept = Department(
            get_value("Department"),
            get_value("Department Name"),
            get_value("Email")
        )
        dept.bootup_insert(connection)

    prof = Professor(
        get_value("Email"),
        get_value("Password"),
        get_value("Name"),
        get_value("Age"),
        get_value("Gender"),
        get_value("Office"),
        get_value("Department"),
        get_value("Title")
    )
    prof.bootup_insert(connection)

    prof_team = Prof_teams(
        get_value("Team ID")
    )
    prof_team.bootup_insert(connection)

    prof_team_members = Prof_team_members(
        prof.email,
        prof_team.team_id
    )

    prof_team_members.bootup_insert(connection)



