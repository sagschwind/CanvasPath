from flask import make_response, render_template

host = 'http://127.0.0.1:5000'
DATABASE_NAME = 'database.db'
logout_extension = "/logout"

# Defines different user types
class USER:
    PROFESSOR = "Professor"
    STUDENT = "Student"
    UNKNOWN = "Unknown"
    ADMIN = "Admin"

def get_email_and_type(request):
    print(request.cookies)
    if "user_email" in request.cookies and "user_type" in request.cookies:
        return request.cookies["user_email"], request.cookies["user_type"]
    return None, None

def render_error(error_text):
    return make_response(render_template("error_page.html",
                                            error_text=error_text))