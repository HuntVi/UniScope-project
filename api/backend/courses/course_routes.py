from flask import Blueprint, request, jsonify, make_response, current_app

courses = Blueprint('courses', __name__)

ROW_HEADERS = ['id', 'dept_id', 'code', 'name', 'credits', 'description']

COURSES = [
    (1, 1, 'CS 1800', 'Discrete Structures', 4,
     'Introduces mathematical structures and methods that form the foundation of computer science, including sets, functions, logic, and counting techniques.'),
    (2, 1, 'CS 2100', 'Program Design and Implementation 1', 4,
     'Examines fundamentals of program design and implementation including data structures, object-oriented design patterns, and software engineering practices.'),
    (3, 1, 'CS 2500', 'Fundamentals of Computer Science 1', 4,
     'Introduces the design and analysis of algorithms, the management of information, and the principles of computation using a functional programming language.'),
    (4, 1, 'CS 2510', 'Fundamentals of Computer Science 2', 4,
     'Continues study of program design and data structures, emphasizing object-oriented design, mutation, and large-scale program construction.'),
    (5, 1, 'CS 2800', 'Logic and Computation', 4,
     'Introduces formal logic and its connections to computer science, covering propositional and first-order logic, logical inference, and mathematical induction.'),
    (6, 1, 'CS 3000', 'Algorithms and Data', 4,
     'Introduces principles and techniques for the design, analysis, and implementation of efficient algorithms and data representations.'),
    (7, 1, 'CS 3100', 'Program Design and Implementation 2', 4,
     'Builds on CS 2100 to examine program design at increasing scales of complexity, covering software design patterns and large-scale software projects.'),
    (8, 1, 'CS 3200', 'Introduction to Databases', 4,
     'Studies the design of a database for use in a relational database management system. Covers ER modeling, relational algebra, SQL, and advanced topics.'),
    (9, 1, 'CS 3500', 'Object-Oriented Design', 4,
     'Covers the principles and practices of designing large-scale object-oriented software systems using design patterns and SOLID principles.'),
    (10, 1, 'CS 3650', 'Computer Systems', 4,
     'Introduces basic design of computing systems, operating systems, and assembly language. Covers caches, virtual memory, system calls, and OS structures.'),
    (11, 1, 'CS 3700', 'Networks and Distributed Systems', 4,
     'Introduces fundamentals of computer networks, including architectures, protocols, and distributed program construction with emphasis on high-level protocols.'),
    (12, 1, 'CS 3800', 'Theory of Computation', 4,
     'Introduces the theory behind computers, covering automata theory, computability, and complexity including finite automata and Turing machines.')
]

# Get all courses
@courses.route('/courses', methods=['GET'])
def get_courses():
    current_app.logger.info('course_routes.py: GET /courses')

    json_data = []
    for row in COURSES:
        json_data.append(dict(zip(ROW_HEADERS, row)))

    the_response = make_response(jsonify(json_data))
    the_response.status_code = 200
    the_response.mimetype = 'application/json'
    return the_response


# Get one course by courseID
@courses.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    current_app.logger.info(f'course_routes.py: GET /courses/{course_id}')

    for row in COURSES:
        if row[0] == course_id:
            course = dict(zip(ROW_HEADERS, row))

            the_response = make_response(jsonify(course))
            the_response.status_code = 200
            the_response.mimetype = 'application/json'
            return the_response

    the_response = make_response(jsonify({"error": "Course not found"}))
    the_response.status_code = 404
    the_response.mimetype = 'application/json'
    return the_response


# Get reviews for one course
@courses.route('/courses/<int:course_id>/reviews', methods=['GET'])
def get_course_reviews(course_id):
    current_app.logger.info(f'course_routes.py: GET /courses/{course_id}/reviews')

    the_response = make_response(jsonify({
        "course_id": course_id,
        "reviews": []
    }))
    the_response.status_code = 200
    the_response.mimetype = 'application/json'
    return the_response