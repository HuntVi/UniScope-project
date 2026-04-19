from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import get_db
from datetime import date, datetime

systemlogs = Blueprint('systemlogs', __name__)

VALID_SEVERITIES = {'INFO', 'WARNING', 'ERROR'}


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


# GET /systemlogs
# Default (no params): returns logs from the last 7 days — Barry's live health dashboard.
# If ANY search param is provided, the 7-day window is lifted and the full
# log history is searched using the given criteria.
#
# Search params (all optional, all combinable):
#   ?severity=INFO|WARNING|ERROR  — filter by severity level
#   ?admin_name={str}             — partial match on the admin who created the log
#   ?message={str}                — partial match on log message content
#   ?since=YYYY-MM-DD             — logs on or after this date
#   ?until=YYYY-MM-DD             — logs on or before this date
#   ?system_only=true             — only system-generated logs (admin_id IS NULL)
@systemlogs.route('/systemlogs', methods=['GET'])
def get_systemlogs():
    current_app.logger.info('GET /systemlogs')

    severity    = request.args.get('severity')
    admin_name  = request.args.get('admin_name')
    message     = request.args.get('message')
    since       = request.args.get('since')
    until       = request.args.get('until')
    system_only = request.args.get('system_only', 'false').lower() == 'true'

    # Any search param lifts the default 7-day window
    is_search = any([severity, admin_name, message, since, until, system_only])

    cursor = get_db().cursor()

    base_query = '''
        SELECT  sl.log_id,
                sl.admin_id,
                sl.message,
                sl.timestamp,
                sl.severity,
                a.admin_name
        FROM SystemLog sl
        LEFT JOIN Admin a ON sl.admin_id = a.admin_id
    '''

    conditions = []
    params     = []

    if not is_search:
        conditions.append("DATE(sl.timestamp) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)")

    if severity:
        conditions.append('sl.severity = %s')
        params.append(severity)
    if admin_name:
        conditions.append('a.admin_name LIKE %s')
        params.append(f'%{admin_name}%')
    if message:
        conditions.append('sl.message LIKE %s')
        params.append(f'%{message}%')
    if since:
        conditions.append('DATE(sl.timestamp) >= %s')
        params.append(since)
    if until:
        conditions.append('DATE(sl.timestamp) <= %s')
        params.append(until)
    if system_only:
        conditions.append('sl.admin_id IS NULL')

    if conditions:
        base_query += ' WHERE ' + ' AND '.join(conditions)
    base_query += ' ORDER BY sl.timestamp DESC'

    cursor.execute(base_query, params)
    return make_response(jsonify(_rows(cursor)), 200)


# POST /systemlogs
# Creates a new log entry. admin_id is optional (system events have no admin).
# Body: { "message": str, "severity": "INFO"|"WARNING"|"ERROR", "admin_id": int (optional) }
@systemlogs.route('/systemlogs', methods=['POST'])
def create_systemlog():
    body = request.get_json()
    current_app.logger.info(f'POST /systemlogs body={body}')

    if 'message' not in body or 'severity' not in body:
        return make_response(jsonify({'error': 'message and severity are required'}), 400)
    if body['severity'] not in VALID_SEVERITIES:
        return make_response(jsonify({'error': f'severity must be one of {VALID_SEVERITIES}'}), 400)

    cursor = get_db().cursor()
    cursor.execute(
        'INSERT INTO SystemLog (admin_id, message, timestamp, severity) VALUES (%s, %s, NOW(), %s)',
        (body.get('admin_id'), body['message'], body['severity'])
    )
    get_db().commit()
    return make_response(jsonify({'log_id': cursor.lastrowid, 'message': 'Log entry created'}), 201)
