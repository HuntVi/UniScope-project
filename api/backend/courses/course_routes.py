from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import get_db

courses = Blueprint('courses', __name__)

# Get all courses from the DB
@courses.route('/courses', methods=['GET'])
def get_courses():
    current_app.logger.info('course_routes.py: GET /courses')

    cursor = get_db().cursor()
    cursor.execute('select * from Course')

    row_headers = [x[0] for x in cursor.description]
    json_data = []

    theData = cursor.fetchall()
    for row in theData:
        json_data.append(dict(zip(row_headers, row)))

    the_response = make_response(jsonify(json_data))
    the_response.status_code = 200
    the_response.mimetype = 'application/json'
    return the_response


# Get one course by courseID
@courses.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    current_app.logger.info(f'course_routes.py: GET /courses/{course_id}')

    cursor = get_db().cursor()
    query = 'select * from Course where course_id = %s'
    cursor.execute(query, (course_id,))

    row_headers = [x[0] for x in cursor.description]
    json_data = []

    theData = cursor.fetchall()
    for row in theData:
        json_data.append(dict(zip(row_headers, row)))

    the_response = make_response(jsonify(json_data))
    the_response.status_code = 200
    the_response.mimetype = 'application/json'
    return the_response