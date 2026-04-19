from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import get_db
from datetime import date, datetime

reviews = Blueprint('reviews', __name__)


def _serialize(value):
    """Convert date/datetime to ISO string so jsonify can handle it."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _rows(cursor):
    headers = [x[0] for x in cursor.description]
    return [
        {h: _serialize(v) for h, v in zip(headers, row)}
        for row in cursor.fetchall()
    ]


# GET /reviews
# Returns reviews with student and course context.
# Optional query params (combinable):
#   ?status=pending|approved|rejected  — filter by moderation status (Barry)
#   ?student_id={id}                   — filter to one student's reviews (Jason)
@reviews.route('/reviews', methods=['GET'])
def get_reviews():
    current_app.logger.info('GET /reviews')
    status     = request.args.get('status')
    student_id = request.args.get('student_id', type=int)
    cursor     = get_db().cursor()

    base_query = '''
        SELECT  r.review_id,
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
                s.student_name,
                c.course_code,
                c.course_name,
                co.semester,
                co.year
        FROM Review r
        JOIN Student        s  ON r.student_id  = s.student_id
        JOIN CourseOffering co ON r.offering_id = co.offering_id
        JOIN Course         c  ON co.course_id  = c.course_id
    '''

    conditions = []
    params     = []

    if status:
        conditions.append('r.status = %s')
        params.append(status)
    if student_id:
        conditions.append('r.student_id = %s')
        params.append(student_id)

    if conditions:
        base_query += ' WHERE ' + ' AND '.join(conditions)
    base_query += ' ORDER BY r.review_date DESC'

    cursor.execute(base_query, params)
    return make_response(jsonify(_rows(cursor)), 200)


# POST /reviews
# Creates a new review. Status defaults to 'approved' — live immediately.
# Becomes 'pending' only if later flagged via POST /flags.
@reviews.route('/reviews', methods=['POST'])
def create_review():
    body = request.get_json()
    current_app.logger.info(f'POST /reviews body={body}')

    required = ['student_id', 'offering_id', 'difficulty_score', 'workload_score',
                'clarity_score', 'satisfaction_score', 'fairness_score',
                'attendance_required', 'weekly_hours']
    missing = [f for f in required if f not in body]
    if missing:
        return make_response(jsonify({'error': f'Missing fields: {missing}'}), 400)

    cursor = get_db().cursor()
    query = '''
        INSERT INTO Review
            (student_id, offering_id, comment_text, review_date,
             difficulty_score, workload_score, clarity_score,
             satisfaction_score, fairness_score,
             attendance_required, weekly_hours, status)
        VALUES (%s, %s, %s, CURDATE(), %s, %s, %s, %s, %s, %s, %s, 'approved')
    '''
    cursor.execute(query, (
        body['student_id'],
        body['offering_id'],
        body.get('comment_text', ''),
        body['difficulty_score'],
        body['workload_score'],
        body['clarity_score'],
        body['satisfaction_score'],
        body['fairness_score'],
        body['attendance_required'],
        body['weekly_hours'],
    ))
    get_db().commit()
    return make_response(jsonify({'review_id': cursor.lastrowid, 'message': 'Review created'}), 201)


# GET /reviews/{reviewID}
# Returns full detail for one review including course and student context.
@reviews.route('/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    current_app.logger.info(f'GET /reviews/{review_id}')
    cursor = get_db().cursor()
    query = '''
        SELECT  r.review_id,
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
                s.student_name,
                c.course_code,
                c.course_name,
                co.semester,
                co.year
        FROM Review r
        JOIN Student        s  ON r.student_id   = s.student_id
        JOIN CourseOffering co  ON r.offering_id  = co.offering_id
        JOIN Course         c  ON co.course_id    = c.course_id
        WHERE r.review_id = %s
    '''
    cursor.execute(query, (review_id,))
    rows = _rows(cursor)
    if not rows:
        return make_response(jsonify({'error': 'Review not found'}), 404)
    return make_response(jsonify(rows[0]), 200)


# PUT /reviews/{reviewID}
# Updates editable fields on a review.
# Students can update content fields; admins can update status.
@reviews.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    body = request.get_json()
    current_app.logger.info(f'PUT /reviews/{review_id} body={body}')

    allowed = {
        'comment_text', 'difficulty_score', 'workload_score', 'clarity_score',
        'satisfaction_score', 'fairness_score', 'attendance_required',
        'weekly_hours', 'status'
    }
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        return make_response(jsonify({'error': 'No valid fields provided'}), 400)

    set_clause = ', '.join(f'{k} = %s' for k in updates)
    values = list(updates.values()) + [review_id]

    cursor = get_db().cursor()
    cursor.execute(f'UPDATE Review SET {set_clause} WHERE review_id = %s', values)
    get_db().commit()
    if cursor.rowcount == 0:
        return make_response(jsonify({'error': 'Review not found'}), 404)
    return make_response(jsonify({'message': 'Review updated'}), 200)


# DELETE /reviews/{reviewID}
# Permanently removes a review.
@reviews.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    current_app.logger.info(f'DELETE /reviews/{review_id}')
    cursor = get_db().cursor()
    cursor.execute('DELETE FROM Review WHERE review_id = %s', (review_id,))
    get_db().commit()
    if cursor.rowcount == 0:
        return make_response(jsonify({'error': 'Review not found'}), 404)
    return make_response(jsonify({'message': 'Review deleted'}), 200)
