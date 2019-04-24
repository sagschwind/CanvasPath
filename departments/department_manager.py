from flask import render_template, make_response, Blueprint
from database import department_manager_api

department_app = Blueprint('department_app', __name__)

@department_app.route('/', methods=['GET'])
def all_departments():
    data = department_manager_api.get_all_department_information()

    return make_response(render_template("table_listing.html",
                              headers=data["headers"],
                              link_prefix="departments",
                              data_2d=data["course_info"]
                              )
                         )

@department_app.route('/<department_id>', methods=['GET'])
def render_department(department_id):
    data = department_manager_api.get_department_information(department_id)

    return make_response(render_template("departments/department.html",
                                         dept_info=data["dept_info"],
                                         dept_head=data["dept_head"],
                                         headers=data["headers"],
                                         data_2d=data["professors"]
                                         )
                         )