from flask import render_template, request, make_response, Blueprint
from database import team_management_api, course_management_api
from Utility import get_email_and_type, USER, render_error
from database.TableSchema import *

team_app = Blueprint('team_app', __name__)

@team_app.route('/<course_id>/<sec_no>/<team_id>', methods=['GET', 'POST'])
def get_team_data(course_id, sec_no, team_id):
    user_email, user_type = get_email_and_type(request)

    if user_email is not None:
        if request.method == "POST":
            if request.form["action"] == "add":
                handle_add_team_member(course_id, sec_no, team_id, request.form)
            elif request.form["action"] == "drop":
                handle_drop_team_member(course_id, sec_no, team_id, request.form)

        return render_team_data(user_type, course_id, sec_no, team_id)

    return render_error("Not logged in")

def render_team_data(user_type, course_id, sec_no, team_id):
    team_members = team_management_api.get_team_members(course_id, sec_no, team_id)
    students_in_class = course_management_api.get_students_in_section(course_id, sec_no)

    return make_response(render_template("team/team_info.html",
                                         team_members=team_members,
                                         course_id=course_id,
                                         sec_no=sec_no,
                                         team_id=team_id,
                                         students=students_in_class,
                                         user_type=user_type
                                         )
                         )

def handle_add_team_member(course_id, sec_no, team_id, form):
    email = form["email"]
    team_member = Capstone_Team_Members(email, team_id, course_id, sec_no)
    team_management_api.insert_team_member(team_member)
def handle_drop_team_member(course_id, sec_no, team_id, form):
    pass