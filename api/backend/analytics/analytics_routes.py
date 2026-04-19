from flask import Blueprint, jsonify, current_app
from backend.db_connection import get_db

analytics = Blueprint("analytics", __name__)


# ------------------------------------------------------------
# /analytics/workload returns workload analytics across courses
@analytics.route("/analytics/workload", methods=["GET"])
def get_workload_analytics():
    current_app.logger.info("GET /analytics/workload")

    cursor = get_db().cursor()

    query = '''
        SELECT
            c.course_id,
            c.course_code,
            c.course_name,
            ROUND(AVG(r.difficulty_score), 2) AS avg_difficulty,
            ROUND(AVG(r.workload_score), 2) AS avg_workload,
            ROUND(AVG(r.weekly_hours), 2) AS avg_weekly_hours,
            COUNT(r.review_id) AS review_count
        FROM Course c
        LEFT JOIN CourseOffering co
            ON c.course_id = co.course_id
        LEFT JOIN Review r
            ON co.offering_id = r.offering_id
            AND r.status != 'rejected'
        GROUP BY
            c.course_id,
            c.course_code,
            c.course_name
        HAVING 
            COUNT(r.review_id) > 0
            AND AVG(r.workload_score) IS NOT NULL
            AND AVG(r.weekly_hours) IS NOT NULL
        ORDER BY avg_workload DESC, avg_weekly_hours DESC
    '''

    cursor.execute(query)

    row_headers = [x[0] for x in cursor.description]
    json_data = []

    the_data = cursor.fetchall()
    for row in the_data:
        json_data.append(dict(zip(row_headers, row)))

    return jsonify(json_data), 200