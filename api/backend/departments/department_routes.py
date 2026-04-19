from flask import Blueprint, jsonify, make_response, current_app
from backend.db_connection import get_db

departments = Blueprint('departments', __name__)


def _rows(cursor):
    headers = [x[0] for x in cursor.description]
    return [dict(zip(headers, row)) for row in cursor.fetchall()]


# GET /departments
# Returns all departments (id + name) for use in frontend dropdowns.
# Used by: any persona that lets users filter or browse by department
@departments.route('/departments', methods=['GET'])
def get_departments():
    current_app.logger.info('GET /departments')
    cursor = get_db().cursor()
    cursor.execute('SELECT department_id, department_name FROM Department ORDER BY department_name')
    return make_response(jsonify(_rows(cursor)), 200)


# GET /departments/{departmentID}/courses
# Returns all courses in a department with aggregated review metrics.
@departments.route('/departments/<int:department_id>/courses', methods=['GET'])
def get_department_courses(department_id):
    current_app.logger.info(f'GET /departments/{department_id}/courses')
    cursor = get_db().cursor()
    query = '''
        SELECT  c.course_id,
                c.course_code,
                c.course_name,
                c.credits,
                c.description,
                ROUND(AVG(r.difficulty_score),   2) AS avg_difficulty,
                ROUND(AVG(r.workload_score),     2) AS avg_workload,
                ROUND(AVG(r.clarity_score),      2) AS avg_clarity,
                ROUND(AVG(r.satisfaction_score), 2) AS avg_satisfaction,
                COUNT(r.review_id)                  AS review_count
        FROM Course c
        LEFT JOIN CourseOffering co ON c.course_id   = co.course_id
        LEFT JOIN Review r          ON co.offering_id = r.offering_id
                                    AND r.status = 'approved'
        WHERE c.department_id = %s
        GROUP BY c.course_id, c.course_code, c.course_name, c.credits, c.description
        ORDER BY c.course_code
    '''
    cursor.execute(query, (department_id,))
    data = _rows(cursor)
    if not data:
        return make_response(jsonify({'error': 'Department not found or has no courses'}), 404)
    return make_response(jsonify(data), 200)
