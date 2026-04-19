from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import get_db
from datetime import date, datetime

flags = Blueprint('flags', __name__)


def _serialize(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _rows(cursor):
    headers = [x[0] for x in cursor.description]
    return [
        {h: _serialize(v) for h, v in zip(headers, row)}
        for row in cursor.fetchall()
    ]


# GET /flags
# Default (no params): returns only unresolved flags (resolved_at IS NULL).
# If ANY search param is provided, the resolved_at filter is lifted and ALL
# flags (resolved + unresolved) are searched using the given criteria.
#
# Search params (all optional, all combinable):
#   ?course_id={int}          — flags on a specific course
#   ?reporter_name={str}      — partial match on reporter's student name
#   ?reason={str}             — partial match on flag reason text
#   ?review_status={str}      — filter by review status (approved/pending/rejected)
#   ?since=YYYY-MM-DD          — flags created on or after this date
#   ?resolved_since=YYYY-MM-DD — flags resolved on or after this date
#   ?system_only=true          — only system-generated flags (reporter_id IS NULL)
#
# Used by: Barry-3, Barry-5
@flags.route('/flags', methods=['GET'])
def get_flags():
    current_app.logger.info('GET /flags')

    course_id       = request.args.get('course_id',       type=int)
    reporter_name   = request.args.get('reporter_name')
    reason          = request.args.get('reason')
    review_status   = request.args.get('review_status')
    since           = request.args.get('since')
    resolved_since  = request.args.get('resolved_since')
    system_only     = request.args.get('system_only', 'false').lower() == 'true'

    # If any search param is present, open up to all flags (resolved + unresolved)
    is_search = any([course_id, reporter_name, reason, review_status, since, resolved_since, system_only])

    cursor = get_db().cursor()

    base_query = '''
        SELECT  f.flag_id,
                f.review_id,
                f.reporter_id,
                f.resolved_by_admin_id,
                f.reason,
                f.created_at,
                f.resolved_at,
                s.student_name  AS reporter_name,
                a.admin_name    AS resolver_name,
                r.comment_text  AS review_comment,
                r.status        AS review_status,
                c.course_id,
                c.course_code,
                c.course_name
        FROM Flag f
        JOIN  Review         r  ON f.review_id            = r.review_id
        JOIN  CourseOffering co ON r.offering_id          = co.offering_id
        JOIN  Course         c  ON co.course_id           = c.course_id
        LEFT JOIN Student    s  ON f.reporter_id          = s.student_id
        LEFT JOIN Admin      a  ON f.resolved_by_admin_id = a.admin_id
    '''

    conditions = []
    params     = []

    if not is_search:
        conditions.append('f.resolved_at IS NULL')

    if course_id:
        conditions.append('c.course_id = %s')
        params.append(course_id)
    if reporter_name:
        conditions.append('s.student_name LIKE %s')
        params.append(f'%{reporter_name}%')
    if reason:
        conditions.append('f.reason LIKE %s')
        params.append(f'%{reason}%')
    if review_status:
        conditions.append('r.status = %s')
        params.append(review_status)
    if since:
        conditions.append('DATE(f.created_at) >= %s')
        params.append(since)
    if resolved_since:
        conditions.append('DATE(f.resolved_at) >= %s')
        params.append(resolved_since)
    if system_only:
        conditions.append('f.reporter_id IS NULL')

    if conditions:
        base_query += ' WHERE ' + ' AND '.join(conditions)
    base_query += ' ORDER BY f.created_at DESC'

    cursor.execute(base_query, params)
    return make_response(jsonify(_rows(cursor)), 200)


# POST /flags
# Creates a new flag on a review AND atomically sets the review status
# to 'pending' so it is pulled from public view for admin moderation.
# Both writes happen in one transaction — if either fails, neither commits.
# reporter_id is nullable (system-generated flags have no reporter).
# Used by: Jason-2, Barry-4
@flags.route('/flags', methods=['POST'])
def create_flag():
    body = request.get_json()
    current_app.logger.info(f'POST /flags body={body}')

    if 'review_id' not in body or 'reason' not in body:
        return make_response(jsonify({'error': 'review_id and reason are required'}), 400)

    db     = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            'INSERT INTO Flag (review_id, reporter_id, reason, created_at) VALUES (%s, %s, %s, NOW())',
            (body['review_id'], body.get('reporter_id'), body['reason'])
        )
        flag_id = cursor.lastrowid

        cursor.execute(
            "UPDATE Review SET status = 'pending' WHERE review_id = %s",
            (body['review_id'],)
        )

        db.commit()
    except Exception as e:
        db.rollback()
        current_app.logger.error(f'POST /flags transaction failed: {e}')
        return make_response(jsonify({'error': 'Failed to create flag'}), 500)

    return make_response(jsonify({'flag_id': flag_id, 'message': 'Flag created and review marked as pending'}), 201)


# PUT /flags/{flagID}
# Marks a flag as resolved. Records the resolving admin and timestamp.
# Body: { "resolved_by_admin_id": <int> }
# Used by: Barry-5
@flags.route('/flags/<int:flag_id>', methods=['PUT'])
def resolve_flag(flag_id):
    body = request.get_json()
    current_app.logger.info(f'PUT /flags/{flag_id} body={body}')

    if 'resolved_by_admin_id' not in body:
        return make_response(jsonify({'error': 'resolved_by_admin_id is required'}), 400)

    cursor = get_db().cursor()
    query = '''
        UPDATE Flag
        SET resolved_by_admin_id = %s,
            resolved_at          = NOW()
        WHERE flag_id = %s
    '''
    cursor.execute(query, (body['resolved_by_admin_id'], flag_id))
    get_db().commit()
    if cursor.rowcount == 0:
        return make_response(jsonify({'error': 'Flag not found'}), 404)
    return make_response(jsonify({'message': 'Flag resolved'}), 200)
