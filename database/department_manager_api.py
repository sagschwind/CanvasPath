import sqlite3 as sql
from Utility import DATABASE_NAME

def get_all_department_information():
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Department.dept_id, Department.dept_name
    FROM Department
    ORDER BY Department.dept_id;
    """

    cursor = connection.execute(statement)
    course_info = cursor.fetchall()
    connection.close()
    results = {
        "headers": ("Department", "Name"),
        "course_info": course_info
    }
    return results

def get_department_information(department_id):
    dictionary = {
        "department_id": department_id
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Professor.name, Professor.email, Professor.office_address, Department.dept_id, Department.dept_name
    FROM Department, Professor
    WHERE Department.dept_head = Professor.email
    AND Department.dept_id = :department_id;
    """

    cursor = connection.execute(statement, dictionary)
    dept_head = cursor.fetchone()
    dept_info = dept_head[3:]
    dept_head = dept_head[:3]
    statement = """
    SELECT Professor.name, Professor.email, Professor.office_address
    FROM Department, Professor
    WHERE Department.dept_id = :department_id
    AND Department.dept_head != Professor.email
    AND Professor.department = Department.dept_id
    ORDER BY Professor.name;
    """

    cursor = connection.execute(statement, dictionary)
    professors = cursor.fetchall()
    connection.close()

    return {
        "dept_info": dept_info,
        "dept_head": dept_head,
        "headers": ("Name", "Email", "Office Address"),
        "professors": professors
    }


