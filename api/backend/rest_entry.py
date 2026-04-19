from flask import Flask
from dotenv import load_dotenv
import os
import logging

from backend.db_connection import init_app as init_db
from backend.students.student_routes import students
from backend.professors.professor_routes import professors
from backend.advisors.advisor_routes import advisors
from backend.admin.admin_routes import admin


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

    app.logger.info('create_app(): registering blueprints')
    app.register_blueprint(students,   url_prefix='/students')
    app.register_blueprint(professors, url_prefix='/professors')
    app.register_blueprint(advisors,   url_prefix='/advisors')
    app.register_blueprint(admin,      url_prefix='/admin')

    return app
