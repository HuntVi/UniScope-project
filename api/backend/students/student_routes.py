from flask import Blueprint, jsonify, current_app
from backend.db_connection import get_db

students = Blueprint("students", __name__)


# ------------------------------------------------------------
# /students/<student_id>
# Returns academic profile information for one student
@students.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    current_app.logger.info(f"GET /students/{student_id}")

    cursor = get_db().cursor()

    query = '''
        SELECT
            s.student_id,
            s.student_name,
            s.academic_year,
            s.student_email,
            s.total_hours,
            s.department_id,
            d.department_name
        FROM Student s
        LEFT JOIN Department d
            ON s.department_id = d.department_id
        WHERE s.student_id = %s
    '''

    cursor.execute(query, (student_id,))

    row_headers = [x[0] for x in cursor.description]
    json_data = []

    the_data = cursor.fetchall()
    for row in the_data:
        json_data.append(dict(zip(row_headers, row)))

    if not json_data:
        current_app.logger.warning(f"Student {student_id} not found")
        return jsonify({"error": f"Student {student_id} not found"}), 404

    return jsonify(json_data), 200