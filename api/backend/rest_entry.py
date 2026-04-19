from flask import Flask
from dotenv import load_dotenv
import os
import logging

from backend.db_connection import init_app as init_db
#from backend.simple.simple_routes import simple_routes
#from backend.ngos.ngo_routes import ngos

from backend.courses.course_routes import courses
from backend.students.student_routes import students
#from backend._x_students.student_routes import students
#from backend._x_professors.professor_routes import professors
#from backend._x_advisors.advisor_routes import advisors
#from backend._x_admin.admin_routes import admin


def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('UniScope API startup')

    load_dotenv()

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['MYSQL_DATABASE_USER'] = os.getenv('DB_USER').strip()
    app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_ROOT_PASSWORD').strip()
    app.config['MYSQL_DATABASE_HOST'] = os.getenv('DB_HOST').strip()
    app.config['MYSQL_DATABASE_PORT'] = int(os.getenv('DB_PORT').strip())
    app.config['MYSQL_DATABASE_DB'] = os.getenv('DB_NAME').strip()

    app.logger.info('create_app(): initializing database connection')
    init_db(app)

    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each.
    app.logger.info("create_app(): registering blueprints")
    #app.register_blueprint(simple_routes)
    #app.register_blueprint(ngos, url_prefix="/ngo")

    app.register_blueprint(courses)
    app.register_blueprint(students)
    #app.register_blueprint(students, url_prefix='/students')
    #app.register_blueprint(professors, url_prefix='/professors')
    #app.register_blueprint(advisors, url_prefix='/advisors')
    #app.register_blueprint(admin, url_prefix='/admin')

    return app