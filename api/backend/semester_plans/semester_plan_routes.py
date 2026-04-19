from flask import Blueprint, jsonify, current_app, request
from backend.db_connection import get_db

# This blueprint handles semester plan routes
semester_plans = Blueprint("semester_plans", __name__)


# ------------------------------------------------------------
# /semesterplans/<plan_id> returns one semester plan
# along with all courses in the plan and summary metrics
@semester_plans.route("/semesterplans/<int:plan_id>", methods=["GET"])
def get_semester_plan(plan_id):
    current_app.logger.info(f"GET /semesterplans/{plan_id}")

    try:
        cursor = get_db().cursor()

        # ------------------------------------------------------------
        # Query 1:
        # Retrieve the semester plan record itself
        # This gives the basic plan metadata
        plan_query = '''
            SELECT
                plan_id,
                student_id,
                advisor_id,
                plan_name
            FROM SemesterPlan
            WHERE plan_id = %s
        '''
        cursor.execute(plan_query, (plan_id,))

        plan_headers = [x[0] for x in cursor.description]
        plan_data = []

        the_data = cursor.fetchall()
        for row in the_data:
            plan_data.append(dict(zip(plan_headers, row)))

        # If no semester plan is found with the given ID,
        # return a 404 error response
        if not plan_data:
            return jsonify({"error": f"Semester plan {plan_id} not found"}), 404

        plan = plan_data[0]

        # ------------------------------------------------------------
        # Query 2:
        # Retrieve all courses connected to this plan
        # along with aggregated review metrics for each course
        #
        # LEFT JOIN is used for reviews so that courses still appear
        # even if they have no review data yet
        courses_query = '''
            SELECT
                c.course_id,
                c.course_code,
                c.course_name,
                c.credits,
                ROUND(AVG(r.difficulty_score), 2) AS avg_difficulty,
                ROUND(AVG(r.workload_score), 2) AS avg_workload,
                ROUND(AVG(r.satisfaction_score), 2) AS avg_satisfaction,
                ROUND(AVG(r.weekly_hours), 2) AS avg_weekly_hours,
                COUNT(r.review_id) AS review_count
            FROM PlanCourse pc
            JOIN Course c
                ON pc.course_id = c.course_id
            LEFT JOIN CourseOffering co
                ON c.course_id = co.course_id
            LEFT JOIN Review r
                ON co.offering_id = r.offering_id
                AND r.status != 'rejected'
            WHERE pc.plan_id = %s
            GROUP BY
                c.course_id,
                c.course_code,
                c.course_name,
                c.credits
            ORDER BY c.course_code
        '''
        cursor.execute(courses_query, (plan_id,))

        course_headers = [x[0] for x in cursor.description]
        courses = []

        the_data = cursor.fetchall()
        for row in the_data:
            courses.append(dict(zip(course_headers, row)))

        # ------------------------------------------------------------
        # Compute semester plan summary metrics in Python
        #
        # We calculate:
        # - total number of courses
        # - total credits
        # - average difficulty/workload/satisfaction
        # - total average weekly hours across the plan
        total_courses = len(courses)
        total_credits = sum(course["credits"] for course in courses)

        valid_difficulty = [
            float(course["avg_difficulty"])
            for course in courses
            if course["avg_difficulty"] is not None
        ]
        valid_workload = [
            float(course["avg_workload"])
            for course in courses
            if course["avg_workload"] is not None
        ]
        valid_satisfaction = [
            float(course["avg_satisfaction"])
            for course in courses
            if course["avg_satisfaction"] is not None
        ]
        valid_weekly_hours = [
            float(course["avg_weekly_hours"])
            for course in courses
            if course["avg_weekly_hours"] is not None
        ]

        avg_difficulty = round(sum(valid_difficulty) / len(valid_difficulty), 2) if valid_difficulty else None
        avg_workload = round(sum(valid_workload) / len(valid_workload), 2) if valid_workload else None
        avg_satisfaction = round(sum(valid_satisfaction) / len(valid_satisfaction), 2) if valid_satisfaction else None
        total_avg_weekly_hours = round(sum(valid_weekly_hours), 2) if valid_weekly_hours else 0

        # ------------------------------------------------------------
        # A simple workload check:
        # if total average weekly hours is above 20,
        # mark the plan as potentially hard to manage
        is_manageable = total_avg_weekly_hours <= 20
        warning = None

        if not is_manageable:
            warning = "This semester plan may have a high workload."

        # ------------------------------------------------------------
        # Build the final JSON response
        response = {
            "plan_id": plan["plan_id"],
            "student_id": plan["student_id"],
            "advisor_id": plan["advisor_id"],
            "plan_name": plan["plan_name"],
            "total_courses": total_courses,
            "total_credits": total_credits,
            "avg_difficulty": avg_difficulty,
            "avg_workload": avg_workload,
            "avg_satisfaction": avg_satisfaction,
            "total_avg_weekly_hours": total_avg_weekly_hours,
            "is_manageable": is_manageable,
            "warning": warning,
            "courses": courses
        }

        return jsonify(response), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching semester plan {plan_id}: {e}")
        return jsonify({"error": "Failed to retrieve semester plan"}), 500


# ------------------------------------------------------------
# /semesterplans creates a new semester plan
# The client sends plan information in JSON format
@semester_plans.route("/semesterplans", methods=["POST"])
def create_semester_plan():
    current_app.logger.info("POST /semesterplans")

    try:
        # ------------------------------------------------------------
        # Read the JSON body sent by the client
        # Example:
        # {
        #   "student_id": 1,
        #   "advisor_id": 2,
        #   "plan_name": "Fall Plan"
        # }
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        student_id = data.get("student_id")
        advisor_id = data.get("advisor_id")
        plan_name = data.get("plan_name")

        # ------------------------------------------------------------
        # plan_name is required because the table defines it as NOT NULL
        if not plan_name:
            return jsonify({"error": "plan_name is required"}), 400

        cursor = get_db().cursor()

        # ------------------------------------------------------------
        # Insert the new semester plan into the SemesterPlan table
        insert_query = '''
            INSERT INTO SemesterPlan (student_id, advisor_id, plan_name)
            VALUES (%s, %s, %s)
        '''
        cursor.execute(insert_query, (student_id, advisor_id, plan_name))
        get_db().commit()

        # ------------------------------------------------------------
        # cursor.lastrowid gives the primary key of the row just inserted
        new_plan_id = cursor.lastrowid

        # ------------------------------------------------------------
        # Build a response showing the newly created semester plan
        response = {
            "plan_id": new_plan_id,
            "student_id": student_id,
            "advisor_id": advisor_id,
            "plan_name": plan_name
        }

        return jsonify(response), 201

    except Exception as e:
        current_app.logger.error(f"Error creating semester plan: {e}")
        return jsonify({"error": "Failed to create semester plan"}), 500


# ------------------------------------------------------------
# /semesterplans/<plan_id> deletes an existing semester plan
# All associated courses will also be removed due to cascade
@semester_plans.route("/semesterplans/<int:plan_id>", methods=["DELETE"])
def delete_semester_plan(plan_id):
    current_app.logger.info(f"DELETE /semesterplans/{plan_id}")

    try:
        cursor = get_db().cursor()

        # ------------------------------------------------------------
        # First, check whether the semester plan exists
        check_query = '''
            SELECT plan_id
            FROM SemesterPlan
            WHERE plan_id = %s
        '''
        cursor.execute(check_query, (plan_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": f"Semester plan {plan_id} not found"}), 404

        # ------------------------------------------------------------
        # Delete the semester plan
        # Related PlanCourse rows will be deleted automatically
        delete_query = '''
            DELETE FROM SemesterPlan
            WHERE plan_id = %s
        '''
        cursor.execute(delete_query, (plan_id,))
        get_db().commit()

        # ------------------------------------------------------------
        # Build success response
        response = {
            "message": f"Semester plan {plan_id} deleted successfully",
            "plan_id": plan_id
        }

        return jsonify(response), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting semester plan {plan_id}: {e}")
        return jsonify({"error": "Failed to delete semester plan"}), 500


# ------------------------------------------------------------
# /semesterplans/<plan_id>/courses/<course_id> adds a course
# to an existing semester plan
@semester_plans.route("/semesterplans/<int:plan_id>/courses/<int:course_id>", methods=["POST"])
def add_course_to_plan(plan_id, course_id):
    current_app.logger.info(f"POST /semesterplans/{plan_id}/courses/{course_id}")

    try:
        cursor = get_db().cursor()

        # ------------------------------------------------------------
        # First, check whether the semester plan exists
        plan_check_query = '''
            SELECT plan_id
            FROM SemesterPlan
            WHERE plan_id = %s
        '''
        cursor.execute(plan_check_query, (plan_id,))
        plan_result = cursor.fetchone()

        if not plan_result:
            return jsonify({"error": f"Semester plan {plan_id} not found"}), 404

        # ------------------------------------------------------------
        # Next, check whether the course exists
        course_check_query = '''
            SELECT course_id
            FROM Course
            WHERE course_id = %s
        '''
        cursor.execute(course_check_query, (course_id,))
        course_result = cursor.fetchone()

        if not course_result:
            return jsonify({"error": f"Course {course_id} not found"}), 404

        # ------------------------------------------------------------
        # Check whether this course is already in the semester plan
        duplicate_check_query = '''
            SELECT plan_id, course_id
            FROM PlanCourse
            WHERE plan_id = %s AND course_id = %s
        '''
        cursor.execute(duplicate_check_query, (plan_id, course_id))
        duplicate_result = cursor.fetchone()

        if duplicate_result:
            return jsonify({
                "error": f"Course {course_id} is already in semester plan {plan_id}"
            }), 409

        # ------------------------------------------------------------
        # Insert the new plan-course relationship into the bridge table
        insert_query = '''
            INSERT INTO PlanCourse (plan_id, course_id)
            VALUES (%s, %s)
        '''
        cursor.execute(insert_query, (plan_id, course_id))
        get_db().commit()

        # ------------------------------------------------------------
        # Build success response
        response = {
            "plan_id": plan_id,
            "course_id": course_id,
            "message": f"Course {course_id} added to semester plan {plan_id}"
        }

        return jsonify(response), 201

    except Exception as e:
        current_app.logger.error(f"Error adding course {course_id} to semester plan {plan_id}: {e}")
        return jsonify({"error": "Failed to add course to semester plan"}), 500
    

# ------------------------------------------------------------
# /semesterplans/<plan_id>/courses/<course_id> removes a course
# from an existing semester plan
@semester_plans.route("/semesterplans/<int:plan_id>/courses/<int:course_id>", methods=["DELETE"])
def remove_course_from_plan(plan_id, course_id):
    current_app.logger.info(f"DELETE /semesterplans/{plan_id}/courses/{course_id}")

    try:
        cursor = get_db().cursor()

        # ------------------------------------------------------------
        # First, check whether the semester plan exists
        plan_check_query = '''
            SELECT plan_id
            FROM SemesterPlan
            WHERE plan_id = %s
        '''
        cursor.execute(plan_check_query, (plan_id,))
        plan_result = cursor.fetchone()

        if not plan_result:
            return jsonify({"error": f"Semester plan {plan_id} not found"}), 404

        # ------------------------------------------------------------
        # Next, check whether the course exists
        course_check_query = '''
            SELECT course_id
            FROM Course
            WHERE course_id = %s
        '''
        cursor.execute(course_check_query, (course_id,))
        course_result = cursor.fetchone()

        if not course_result:
            return jsonify({"error": f"Course {course_id} not found"}), 404

        # ------------------------------------------------------------
        # Check whether this course is currently in the semester plan
        relationship_check_query = '''
            SELECT plan_id, course_id
            FROM PlanCourse
            WHERE plan_id = %s AND course_id = %s
        '''
        cursor.execute(relationship_check_query, (plan_id, course_id))
        relationship_result = cursor.fetchone()

        if not relationship_result:
            return jsonify({
                "error": f"Course {course_id} is not in semester plan {plan_id}"
            }), 404

        # ------------------------------------------------------------
        # Delete the plan-course relationship from the bridge table
        delete_query = '''
            DELETE FROM PlanCourse
            WHERE plan_id = %s AND course_id = %s
        '''
        cursor.execute(delete_query, (plan_id, course_id))
        get_db().commit()

        # ------------------------------------------------------------
        # Build success response
        response = {
            "message": f"Course {course_id} removed from semester plan {plan_id}",
            "plan_id": plan_id,
            "course_id": course_id
        }

        return jsonify(response), 200

    except Exception as e:
        current_app.logger.error(f"Error removing course {course_id} from semester plan {plan_id}: {e}")
        return jsonify({"error": "Failed to remove course from semester plan"}), 500