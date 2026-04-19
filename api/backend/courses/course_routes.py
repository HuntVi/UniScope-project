from flask import Blueprint, jsonify, make_response, current_app
from backend.db_connection import get_db

courses = Blueprint('courses', __name__)


# ------------------------------------------------------------
# Helper function:
# converts SQL query results into a list of dictionaries
# ------------------------------------------------------------
def format_query_results(cursor):
    row_headers = [x[0] for x in cursor.description]
    json_data = []

    the_data = cursor.fetchall()
    for row in the_data:
        json_data.append(dict(zip(row_headers, row)))

    return json_data


# ------------------------------------------------------------
# Helper function:
# standardizes JSON API responses
# ------------------------------------------------------------
def build_response(data, status_code=200):
    the_response = make_response(jsonify(data))
    the_response.status_code = status_code
    the_response.mimetype = 'application/json'
    return the_response


# ------------------------------------------------------------
# GET /courses
# Returns all courses with aggregated metrics based on reviews.
# Rejected reviews are excluded, but flagged/pending reviews remain.
# ------------------------------------------------------------
@courses.route('/courses', methods=['GET'])
def get_courses():
    current_app.logger.info('course_routes.py: GET /courses')

    cursor = get_db().cursor()

    query = '''
        SELECT
            c.course_id,
            c.department_id,
            c.course_code,
            c.course_name,
            c.credits,
            c.description,
            ROUND(AVG(r.difficulty_score), 2) AS avg_difficulty,
            ROUND(AVG(r.workload_score), 2) AS avg_workload,
            ROUND(AVG(r.clarity_score), 2) AS avg_clarity,
            ROUND(AVG(r.satisfaction_score), 2) AS avg_satisfaction,
            COUNT(r.review_id) AS review_count
        FROM Course c
        LEFT JOIN CourseOffering co
            ON c.course_id = co.course_id
        LEFT JOIN Review r
            ON co.offering_id = r.offering_id
            AND r.status != 'rejected'
        GROUP BY
            c.course_id,
            c.department_id,
            c.course_code,
            c.course_name,
            c.credits,
            c.description
    '''

    cursor.execute(query)
    json_data = format_query_results(cursor)

    return build_response(json_data)


# ------------------------------------------------------------
# GET /courses/<course_id>
# Returns one course with summary-level review metrics.
# If the course does not exist, returns a 404.
# ------------------------------------------------------------
@courses.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    current_app.logger.info(f'course_routes.py: GET /courses/{course_id}')

    cursor = get_db().cursor()

    query = '''
        SELECT
            c.course_id,
            c.department_id,
            c.course_code,
            c.course_name,
            c.credits,
            c.description,
            ROUND(AVG(r.difficulty_score), 2) AS avg_difficulty,
            ROUND(AVG(r.workload_score), 2) AS avg_workload,
            ROUND(AVG(r.clarity_score), 2) AS avg_clarity,
            ROUND(AVG(r.satisfaction_score), 2) AS avg_satisfaction,
            COUNT(r.review_id) AS review_count
        FROM Course c
        LEFT JOIN CourseOffering co
            ON c.course_id = co.course_id
        LEFT JOIN Review r
            ON co.offering_id = r.offering_id
            AND r.status != 'rejected'
        WHERE c.course_id = %s
        GROUP BY
            c.course_id,
            c.department_id,
            c.course_code,
            c.course_name,
            c.credits,
            c.description
    '''

    cursor.execute(query, (course_id,))
    json_data = format_query_results(cursor)

    if not json_data:
        return build_response({'error': f'Course {course_id} not found'}, 404)

    return build_response(json_data)


# ------------------------------------------------------------
# GET /courses/<course_id>/reviews
# Returns all non-rejected reviews for a specific course.
# Includes semester and year from CourseOffering.
# ------------------------------------------------------------
@courses.route('/courses/<int:course_id>/reviews', methods=['GET'])
def get_course_reviews(course_id):
    current_app.logger.info(f'course_routes.py: GET /courses/{course_id}/reviews')

    cursor = get_db().cursor()

    query = '''
        SELECT
            r.review_id,
            r.student_id,
            r.offering_id,
            r.comment_text,
            r.review_date,
            r.difficulty_score,
            r.workload_score,
            r.clarity_score,
            r.satisfaction_score,
            r.fairness_score,
            r.attendance_required,
            r.weekly_hours,
            r.status,
            co.semester,
            co.year
        FROM Review r
        JOIN CourseOffering co
            ON r.offering_id = co.offering_id
        WHERE co.course_id = %s
          AND r.status != 'rejected'
        ORDER BY co.year DESC, co.semester DESC, r.review_id DESC
    '''

    cursor.execute(query, (course_id,))
    json_data = format_query_results(cursor)

    return build_response(json_data)


# ------------------------------------------------------------
# GET /courses/<course_id>/trends
# Returns trend data by semester/year for a specific course.
# Aggregates exclude rejected reviews.
# ------------------------------------------------------------
@courses.route('/courses/<int:course_id>/trends', methods=['GET'])
def get_course_trends(course_id):
    current_app.logger.info(f'course_routes.py: GET /courses/{course_id}/trends')

    cursor = get_db().cursor()

    query = '''
        SELECT
            co.year,
            co.semester,
            ROUND(AVG(r.difficulty_score), 2) AS avg_difficulty,
            ROUND(AVG(r.workload_score), 2) AS avg_workload,
            ROUND(AVG(r.satisfaction_score), 2) AS avg_satisfaction,
            COUNT(r.review_id) AS review_count
        FROM CourseOffering co
        LEFT JOIN Review r
            ON co.offering_id = r.offering_id
            AND r.status != 'rejected'
        WHERE co.course_id = %s
        GROUP BY co.year, co.semester
        ORDER BY co.year ASC, co.semester ASC
    '''

    cursor.execute(query, (course_id,))
    json_data = format_query_results(cursor)

    return build_response(json_data)


# ------------------------------------------------------------
# GET /courses/<course_id>/reviewsummary
# Returns a summarized review snapshot for a single course.
# Useful for professor/advisor dashboard-style views.
# ------------------------------------------------------------
@courses.route('/courses/<int:course_id>/reviewsummary', methods=['GET'])
def get_course_review_summary(course_id):
    current_app.logger.info(f'course_routes.py: GET /courses/{course_id}/reviewsummary')

    cursor = get_db().cursor()

    query = '''
        SELECT
            c.course_id,
            c.course_code,
            c.course_name,
            COUNT(r.review_id) AS review_count,
            ROUND(AVG(r.difficulty_score), 2) AS avg_difficulty,
            ROUND(AVG(r.workload_score), 2) AS avg_workload,
            ROUND(AVG(r.clarity_score), 2) AS avg_clarity,
            ROUND(AVG(r.satisfaction_score), 2) AS avg_satisfaction,
            ROUND(AVG(r.fairness_score), 2) AS avg_fairness,
            ROUND(AVG(r.weekly_hours), 2) AS avg_weekly_hours
        FROM Course c
        LEFT JOIN CourseOffering co
            ON c.course_id = co.course_id
        LEFT JOIN Review r
            ON co.offering_id = r.offering_id
            AND r.status != 'rejected'
        WHERE c.course_id = %s
        GROUP BY
            c.course_id,
            c.course_code,
            c.course_name
    '''

    cursor.execute(query, (course_id,))
    json_data = format_query_results(cursor)

    if not json_data:
        return build_response({'error': f'Course {course_id} not found'}, 404)

    return build_response(json_data)