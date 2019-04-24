import sqlite3 as sql
from Utility import DATABASE_NAME
from database.TableSchema import *

def get_team_members(course_id, sec_no, team_id):
    dictionary = {
        "course_id": course_id,
        "sec_no": sec_no,
        "team_id": team_id
    }

    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Student.name, Capstone_Team_Members.student_email
    FROM Student
    JOIN Capstone_Team_Members
    ON Student.email = Capstone_Team_Members.student_email
    WHERE Capstone_Team_Members.course_id = :course_id
    AND Capstone_Team_Members.sec_no = :sec_no
    AND Capstone_Team_Members.team_id = :team_id
    ORDER BY Student.name
    """

    cursor = connection.execute(statement, dictionary)
    return {
        "team_members": cursor.fetchall(),
        "headers": ("Student Name", "Email")
    }

def insert_team(team):
    connection = sql.connect(DATABASE_NAME)
    team.bootup_insert(connection)
    connection.close()

def insert_team_member(member):
    connection = sql.connect(DATABASE_NAME)
    member.bootup_insert(connection)
    connection.close()

def create_next_prof_team_num():
    connection = sql.connect(DATABASE_NAME)

    statement = """
    SELECT Max(Prof_teams.team_id)
    FROM Prof_teams;
    """

    cursor = connection.execute(statement)
    num = int(cursor.fetchone()[0])

    if num is None:
        num = 1
    else:
        num += 1

    team = Prof_teams(num)

    team.bootup_insert(connection)

    connection.close()
    return num