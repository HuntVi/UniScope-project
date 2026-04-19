import random
import os
from datetime import date, timedelta
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__), '..', 'database-files', 'uniscope_data.sql'
)

lines = []

def emit(s=''):
    lines.append(s)

def escape(s):
    if s is None:
        return 'NULL'
    return "'" + str(s).replace("'", "''").replace('\\', '\\\\') + "'"

def nu_email(first, last):
    """lastname.firstname@northeastern.edu, lowercase, no spaces/special chars"""
    def clean(s):
        return ''.join(c for c in s.lower() if c.isalpha() or c == '-')
    return f'{clean(last)}.{clean(first)}@northeastern.edu'


# Real Northeastern departments and courses
DEPARTMENTS = [
    (1,  'Computer Science'),
    (2,  'Mathematics'),
    (3,  'Economics'),
    (4,  'Data Science'),
    (5,  'Electrical and Computer Engineering'),
    (6,  'Physics'),
    (7,  'Business Administration'),
    (8,  'English'),
    (9,  'Biology'),
    (10, 'Chemistry and Chemical Biology'),
    (11, 'Mechanical Engineering'),
    (12, 'Civil and Environmental Engineering'),
    (13, 'Chemical Engineering'),
    (14, 'Bioengineering'),
    (15, 'Psychology'),
    (16, 'Political Science'),
    (17, 'Sociology'),
    (18, 'Philosophy'),
    (19, 'History'),
    (20, 'Communication Studies'),
    (21, 'Journalism'),
    (22, 'Linguistics'),
    (23, 'Architecture'),
    (24, 'Music'),
    (25, 'Theatre'),
    (26, 'Finance and Insurance'),
    (27, 'Marketing'),
    (28, 'Management'),
    (29, 'International Business'),
    (30, 'Cybersecurity'),
    (31, 'Network Science'),
    (32, 'Industrial Engineering'),
    (33, 'Materials Engineering'),
    (34, 'Biochemistry'),
    (35, 'Game Science and Design'),
]

# (course_id, dept_id, code, name, credits, description)
COURSES = [
    # Computer Science
    (1,  1, 'CS 1800', 'Discrete Structures', 4,
     'Introduces mathematical structures and methods that form the foundation of computer science, including sets, functions, logic, and counting techniques.'),
    (2,  1, 'CS 2100', 'Program Design and Implementation 1', 4,
     'Examines fundamentals of program design and implementation including data structures, object-oriented design patterns, and software engineering practices.'),
    (3,  1, 'CS 2500', 'Fundamentals of Computer Science 1', 4,
     'Introduces the design and analysis of algorithms, the management of information, and the principles of computation using a functional programming language.'),
    (4,  1, 'CS 2510', 'Fundamentals of Computer Science 2', 4,
     'Continues study of program design and data structures, emphasizing object-oriented design, mutation, and large-scale program construction.'),
    (5,  1, 'CS 2800', 'Logic and Computation', 4,
     'Introduces formal logic and its connections to computer science, covering propositional and first-order logic, logical inference, and mathematical induction.'),
    (6,  1, 'CS 3000', 'Algorithms and Data', 4,
     'Introduces principles and techniques for the design, analysis, and implementation of efficient algorithms and data representations.'),
    (7,  1, 'CS 3100', 'Program Design and Implementation 2', 4,
     'Builds on CS 2100 to examine program design at increasing scales of complexity, covering software design patterns and large-scale software projects.'),
    (8,  1, 'CS 3200', 'Introduction to Databases', 4,
     'Studies the design of a database for use in a relational database management system. Covers ER modeling, relational algebra, SQL, and advanced topics.'),
    (9,  1, 'CS 3500', 'Object-Oriented Design', 4,
     'Covers the principles and practices of designing large-scale object-oriented software systems using design patterns and SOLID principles.'),
    (10, 1, 'CS 3650', 'Computer Systems', 4,
     'Introduces basic design of computing systems, operating systems, and assembly language. Covers caches, virtual memory, system calls, and OS structures.'),
    (11, 1, 'CS 3700', 'Networks and Distributed Systems', 4,
     'Introduces fundamentals of computer networks, including architectures, protocols, and distributed program construction with emphasis on high-level protocols.'),
    (12, 1, 'CS 3800', 'Theory of Computation', 4,
     'Introduces the theory behind computers, covering automata theory, computability, and complexity including finite automata and Turing machines.'),
    (13, 1, 'CS 4100', 'Artificial Intelligence', 4,
     'Introduces fundamental problems, theories, and algorithms of AI, including heuristic search, knowledge representation, planning, and machine learning.'),
    (14, 1, 'CS 4120', 'Natural Language Processing', 4,
     'Introduces computational modeling of human language, covering computational grammar models, statistical language models, and NLP applications.'),
    (15, 1, 'CS 4300', 'Computer Graphics', 4,
     'Charts a path through major aspects of computer graphics: modeling, viewing, rendering, transformations, and interaction with hardware context.'),
    (16, 1, 'CS 4400', 'Programming Languages', 4,
     'Introduces a systematic approach to understanding programming language behavior, covering interpreters, scope, binding, type rules, and concurrency.'),
    (17, 1, 'CS 4500', 'Software Development', 4,
     'Covers large-scale software development practices, agile methods, code review, and collaborative development with substantial project work.'),
    (18, 1, 'CS 4550', 'Web Development', 4,
     'Covers design and implementation of web applications, including client-server architecture, REST APIs, databases, and modern front-end frameworks.'),
    # Mathematics
    (19, 2, 'MATH 1341', 'Calculus 1 for Science and Engineering', 4,
     'Covers limits, derivatives, and integrals of functions of one variable. Emphasizes conceptual understanding and problem-solving for STEM students.'),
    (20, 2, 'MATH 1342', 'Calculus 2 for Science and Engineering', 4,
     'Covers techniques of integration, series, polar coordinates, and introductory differential equations for science and engineering students.'),
    (21, 2, 'MATH 2321', 'Calculus 3 for Science and Engineering', 4,
     'Covers multivariable calculus including partial derivatives, multiple integrals, vector calculus, and the theorems of Green, Stokes, and Gauss.'),
    (22, 2, 'MATH 2331', 'Linear Algebra', 4,
     'Covers systems of linear equations, matrix algebra, determinants, vector spaces, eigenvalues, and linear transformations with applications.'),
    (23, 2, 'MATH 3081', 'Probability and Statistics', 4,
     'Introduces probability theory and statistical inference, covering discrete and continuous distributions, estimation, and hypothesis testing.'),
    (24, 2, 'MATH 4545', 'Fourier Series and Partial Differential Equations', 4,
     'Covers Fourier series, boundary value problems, partial differential equations, and their applications to heat, wave, and Laplace equations.'),
    # Economics
    (25, 3, 'ECON 1115', 'Principles of Microeconomics', 4,
     'Introduces microeconomic theory including supply and demand, consumer behavior, firm theory, market structures, and market failure.'),
    (26, 3, 'ECON 1116', 'Principles of Macroeconomics', 4,
     'Introduces macroeconomic theory including GDP, unemployment, inflation, monetary and fiscal policy, and the open economy.'),
    (27, 3, 'ECON 2350', 'Probability and Statistics for Economists', 4,
     'Covers statistical methods for economic analysis including probability, sampling distributions, regression analysis, and hypothesis testing.'),
    # Data Science
    (28, 4, 'DS 2500', 'Intermediate Programming with Data', 4,
     'Covers intermediate programming using Python for data analysis, including data manipulation, visualization, and introductory machine learning.'),
    (29, 4, 'DS 3000', 'Foundations of Data Science', 4,
     'Introduces foundational concepts in data science including data cleaning, exploratory analysis, statistical modeling, and evaluation.'),
    (30, 4, 'DS 3500', 'Advanced Programming with Data', 4,
     'Covers advanced programming techniques for data-intensive applications, including parallel processing, APIs, and scalable data pipelines.'),
    # Electrical and Computer Engineering
    (31, 5, 'EECE 2160', 'Embedded Design Enabling Robotics', 4,
     'Introduces embedded computing systems design, covering microcontrollers, C programming, digital I/O, and hardware-software integration.'),
    (32, 5, 'EECE 2560', 'Fundamentals of Engineering Algorithms', 4,
     'Covers algorithm design and analysis for engineering applications, including sorting, searching, and graph algorithms in C++.'),
    # Physics
    (33, 6, 'PHYS 1151', 'Physics for Engineering 1', 4,
     'Covers classical mechanics including kinematics, dynamics, energy, momentum, rotation, and oscillations for engineering students.'),
    (34, 6, 'PHYS 1152', 'Physics for Engineering 2', 4,
     'Covers electricity, magnetism, waves, optics, and introductory modern physics for engineering students.'),
    # English Writing
    (35, 8, 'ENGW 1111', 'First-Year Writing', 4,
     'Develops academic writing skills through reading, analysis, and composition. Emphasizes research, argumentation, and revision.'),
]

SEMESTERS = ['Fall', 'Spring']
YEARS     = [2022, 2023, 2024, 2025, 2026]
ACADEMIC_YEARS = ['Freshman', 'Sophomore', 'Junior', 'Senior']
SEVERITIES = ['INFO', 'WARNING', 'ERROR']
FLAG_REASONS = [
    'This review contains inappropriate language.',
    'This comment is not related to the course.',
    'Possibly inaccurate or misleading information.',
    'Review appears to be a duplicate.',
    'Review contains personal attacks on the professor.',
    'Spam or promotional content.',
    'Review violates community guidelines.',
]


# GENERATION HELPERS
def gen_students(n=35):
    """Generate n students with unique NU emails."""
    students = []
    used_emails = set()
    dept_ids = [d[0] for d in DEPARTMENTS]
    for i in range(1, n + 1):
        first = fake.first_name()
        last  = fake.last_name()
        email = nu_email(first, last)
        base, domain = email.split('@')
        counter = 1
        while email in used_emails:
            email = f'{base}{counter}@{domain}'
            counter += 1
        used_emails.add(email)
        dept = random.choice(dept_ids + [None])
        year = random.choice(ACADEMIC_YEARS)
        total_hours = {'Freshman': random.randint(0, 32),
                       'Sophomore': random.randint(32, 64),
                       'Junior': random.randint(64, 96),
                       'Senior': random.randint(96, 132)}[year]
        students.append({
            'student_id': i,
            'student_name': f'{first} {last}',
            'academic_year': year,
            'student_email': email,
            'department_id': dept,
            'total_hours': total_hours,
        })
    return students

def gen_professors(n=35):
    professors = []
    used_emails = set()
    for i in range(1, n + 1):
        first = fake.first_name()
        last  = fake.last_name()
        email = nu_email(first, last)
        base, domain = email.split('@')
        counter = 1
        while email in used_emails:
            email = f'{base}{counter}@{domain}'
            counter += 1
        used_emails.add(email)
        professors.append({
            'professor_id': i,
            'professor_name': f'{first} {last}',
            'professor_email': email,
        })
    return professors

def gen_advisors(n=30):
    advisors = []
    used_emails = set()
    for i in range(1, n + 1):
        first = fake.first_name()
        last  = fake.last_name()
        email = nu_email(first, last)
        base, domain = email.split('@')
        counter = 1
        while email in used_emails:
            email = f'{base}{counter}@{domain}'
            counter += 1
        used_emails.add(email)
        advisors.append({
            'advisor_id': i,
            'advisor_name': f'{first} {last}',
            'advisor_email': email,
        })
    return advisors

def gen_admins(n=30):
    admins = []
    used_emails = set()
    for i in range(1, n + 1):
        first = fake.first_name()
        last  = fake.last_name()
        email = nu_email(first, last)
        base, domain = email.split('@')
        counter = 1
        while email in used_emails:
            email = f'{base}{counter}@{domain}'
            counter += 1
        used_emails.add(email)
        admins.append({
            'admin_id': i,
            'admin_name': f'{first} {last}',
            'admin_email': email,
        })
    return admins

def gen_offerings(n=65):
    offerings = []
    course_ids = [c[0] for c in COURSES]
    used = set()
    oid = 1
    for cid in course_ids:
        semester = random.choice(SEMESTERS)
        year     = random.choice(YEARS)
        offerings.append({
            'offering_id': oid,
            'course_id': cid,
            'semester': semester,
            'year': year,
        })
        used.add((cid, semester, year))
        oid += 1

    # Fill up to n with additional offerings (different semester/year)
    attempts = 0
    while len(offerings) < n and attempts < 1000:
        cid      = random.choice(course_ids)
        semester = random.choice(SEMESTERS)
        year     = random.choice(YEARS)
        if (cid, semester, year) not in used:
            used.add((cid, semester, year))
            offerings.append({
                'offering_id': oid,
                'course_id': cid,
                'semester': semester,
                'year': year,
            })
            oid += 1
        attempts += 1
    return offerings

def gen_professor_offerings(offerings, professors, target=130):
    """Bridge table: assign at least one professor to every offering."""
    prof_ids     = [p['professor_id'] for p in professors]
    offering_ids = [o['offering_id']  for o in offerings]
    assigned     = set()
    result       = []

    # Every offering gets at least one professor
    for oid in offering_ids:
        pid = random.choice(prof_ids)
        assigned.add((pid, oid))
        result.append({'professor_id': pid, 'offering_id': oid})

    attempts = 0
    while len(result) < target and attempts < 5000:
        pid = random.choice(prof_ids)
        oid = random.choice(offering_ids)
        if (pid, oid) not in assigned:
            assigned.add((pid, oid))
            result.append({'professor_id': pid, 'offering_id': oid})
        attempts += 1
    return result

def gen_reviews(students, offerings, n=70):
    student_ids  = [s['student_id']  for s in students]
    offering_ids = [o['offering_id'] for o in offerings]
    used         = set()
    reviews      = []

    for i in range(1, n + 1):
        attempts = 0
        while attempts < 1000:
            sid = random.choice(student_ids)
            oid = random.choice(offering_ids)
            if (sid, oid) not in used:
                used.add((sid, oid))
                break
            attempts += 1
        else:
            break

        diff = random.randint(1, 5)
        wkld = random.randint(1, 5)
        clar = random.randint(1, 5)
        sat  = random.randint(1, 5)
        fair = random.randint(1, 5)
        att  = random.choice([True, False])
        hrs  = round(random.uniform(2.0, 20.0), 1)
        start = date(2022, 1, 1)
        rdate = start + timedelta(days=random.randint(0, 1550))
        status = random.choices(['approved', 'rejected'], weights=[90, 10])[0]
        comment = fake.paragraph(nb_sentences=random.randint(2, 5))

        reviews.append({
            'review_id': i,
            'student_id': sid,
            'offering_id': oid,
            'comment_text': comment,
            'review_date': rdate.isoformat(),
            'difficulty_score': diff,
            'workload_score': wkld,
            'clarity_score': clar,
            'satisfaction_score': sat,
            'fairness_score': fair,
            'attendance_required': att,
            'weekly_hours': hrs,
            'status': status,
        })
    return reviews

def gen_plans(students, advisors, n=55):
    student_ids = [s['student_id'] for s in students]
    advisor_ids = [a['advisor_id'] for a in advisors]
    plans = []
    for i in range(1, n + 1):
        sid = random.choice(student_ids)
        aid = random.choice(advisor_ids)
        sem = random.choice(SEMESTERS)
        yr  = random.choice(YEARS)
        plans.append({
            'plan_id': i,
            'student_id': sid,
            'advisor_id': aid,
            'plan_name': f'{sem} {yr} Plan',
        })
    return plans

def gen_plan_courses(plans, target=140):
    course_ids = [c[0] for c in COURSES]
    plan_ids   = [p['plan_id'] for p in plans]
    used       = set()
    result     = []

    for pid in plan_ids:
        chosen = random.sample(course_ids, min(2, len(course_ids)))
        for cid in chosen:
            if (pid, cid) not in used:
                used.add((pid, cid))
                result.append({'plan_id': pid, 'course_id': cid})

    attempts = 0
    while len(result) < target and attempts < 5000:
        pid = random.choice(plan_ids)
        cid = random.choice(course_ids)
        if (pid, cid) not in used:
            used.add((pid, cid))
            result.append({'plan_id': pid, 'course_id': cid})
        attempts += 1
    return result

def gen_flags(reviews, students, admins, n=50):
    review_ids  = [r['review_id']  for r in reviews]
    student_ids = [s['student_id'] for s in students]
    admin_ids   = [a['admin_id']   for a in admins]
    flags = []
    used_reviews = set()

    for i in range(1, n + 1):
        rid = random.choice(review_ids)
        reporter = random.choice(student_ids) if random.random() < 0.8 else None
        if random.random() < 0.6:
            resolver   = random.choice(admin_ids)
            resolved_at = fake.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
        else:
            resolver   = None
            resolved_at = None

        created_at = fake.date_time_between(start_date='-2y', end_date='-1d').strftime('%Y-%m-%d %H:%M:%S')
        reason = random.choice(FLAG_REASONS)

        flags.append({
            'flag_id': i,
            'review_id': rid,
            'reporter_id': reporter,
            'resolved_by_admin_id': resolver,
            'reason': reason,
            'created_at': created_at,
            'resolved_at': resolved_at,
        })
    return flags

def gen_system_logs(admins, n=55):
    admin_ids = [a['admin_id'] for a in admins]
    messages = [
        'Routine system health check completed successfully.',
        'Duplicate review entry detected and flagged.',
        'Slow query detected on Review table.',
        'Database backup completed.',
        'Failed login attempt detected.',
        'New user registration spike detected.',
        'Inconsistent data found in Review table.',
        'Flag resolution rate dropped below threshold.',
        'System performance within normal parameters.',
        'Cache cleared after schema migration.',
        'Unresolved flags count exceeded warning threshold.',
        'API response time exceeded 500ms.',
        'Scheduled maintenance window starting.',
        'Scheduled maintenance window completed.',
        'Review submission rate anomaly detected.',
    ]
    logs = []
    for i in range(1, n + 1):
        aid       = random.choice(admin_ids)
        msg       = random.choice(messages)
        severity  = random.choices(SEVERITIES, weights=[60, 30, 10])[0]
        timestamp = fake.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
        logs.append({
            'log_id': i,
            'admin_id': aid,
            'message': msg,
            'timestamp': timestamp,
            'severity': severity,
        })
    return logs


# SQL WRITERS
def write_departments():
    emit('-- Department')
    for dept_id, name in DEPARTMENTS:
        emit(f"INSERT INTO Department (department_id, department_name) VALUES ({dept_id}, {escape(name)});")
    emit()

def write_courses():
    emit('-- Course')
    for cid, did, code, name, credits, desc in COURSES:
        emit(f"INSERT INTO Course (course_id, department_id, course_code, course_name, credits, description) "
             f"VALUES ({cid}, {did}, {escape(code)}, {escape(name)}, {credits}, {escape(desc)});")
    emit()

def write_students(students):
    emit('-- Student')
    for s in students:
        did = s['department_id'] if s['department_id'] is not None else 'NULL'
        emit(f"INSERT INTO Student (student_id, student_name, academic_year, student_email, department_id, total_hours) "
             f"VALUES ({s['student_id']}, {escape(s['student_name'])}, {escape(s['academic_year'])}, "
             f"{escape(s['student_email'])}, {did}, {s['total_hours']});")
    emit()

def write_professors(professors):
    emit('-- Professor')
    for p in professors:
        emit(f"INSERT INTO Professor (professor_id, professor_name, professor_email) "
             f"VALUES ({p['professor_id']}, {escape(p['professor_name'])}, {escape(p['professor_email'])});")
    emit()

def write_advisors(advisors):
    emit('-- AcademicAdvisor')
    for a in advisors:
        emit(f"INSERT INTO AcademicAdvisor (advisor_id, advisor_name, advisor_email) "
             f"VALUES ({a['advisor_id']}, {escape(a['advisor_name'])}, {escape(a['advisor_email'])});")
    emit()

def write_admins(admins):
    emit('-- Admin')
    for a in admins:
        emit(f"INSERT INTO Admin (admin_id, admin_name, admin_email) "
             f"VALUES ({a['admin_id']}, {escape(a['admin_name'])}, {escape(a['admin_email'])});")
    emit()

def write_offerings(offerings):
    emit('-- CourseOffering')
    for o in offerings:
        emit(f"INSERT INTO CourseOffering (offering_id, course_id, semester, year) "
             f"VALUES ({o['offering_id']}, {o['course_id']}, {escape(o['semester'])}, {o['year']});")
    emit()

def write_professor_offerings(po_list):
    emit('-- ProfessorOffering')
    for po in po_list:
        emit(f"INSERT INTO ProfessorOffering (professor_id, offering_id) "
             f"VALUES ({po['professor_id']}, {po['offering_id']});")
    emit()

def write_reviews(reviews):
    emit('-- Review')
    for r in reviews:
        att = 'TRUE' if r['attendance_required'] else 'FALSE'
        emit(f"INSERT INTO Review (review_id, student_id, offering_id, comment_text, review_date, "
             f"difficulty_score, workload_score, clarity_score, satisfaction_score, fairness_score, "
             f"attendance_required, weekly_hours, status) VALUES ("
             f"{r['review_id']}, {r['student_id']}, {r['offering_id']}, {escape(r['comment_text'])}, "
             f"{escape(r['review_date'])}, {r['difficulty_score']}, {r['workload_score']}, "
             f"{r['clarity_score']}, {r['satisfaction_score']}, {r['fairness_score']}, "
             f"{att}, {r['weekly_hours']}, {escape(r['status'])});")
    emit()

def write_plans(plans):
    emit('-- SemesterPlan')
    for p in plans:
        emit(f"INSERT INTO SemesterPlan (plan_id, student_id, advisor_id, plan_name) "
             f"VALUES ({p['plan_id']}, {p['student_id']}, {p['advisor_id']}, {escape(p['plan_name'])});")
    emit()

def write_plan_courses(pc_list):
    emit('-- PlanCourse')
    for pc in pc_list:
        emit(f"INSERT INTO PlanCourse (plan_id, course_id) "
             f"VALUES ({pc['plan_id']}, {pc['course_id']});")
    emit()

def write_flags(flags):
    emit('-- Flag')
    for f in flags:
        reporter  = f['reporter_id'] if f['reporter_id'] is not None else 'NULL'
        resolver  = f['resolved_by_admin_id'] if f['resolved_by_admin_id'] is not None else 'NULL'
        resolved_at = escape(f['resolved_at']) if f['resolved_at'] is not None else 'NULL'
        emit(f"INSERT INTO Flag (flag_id, review_id, reporter_id, resolved_by_admin_id, reason, created_at, resolved_at) "
             f"VALUES ({f['flag_id']}, {f['review_id']}, {reporter}, {resolver}, "
             f"{escape(f['reason'])}, {escape(f['created_at'])}, {resolved_at});")
    emit()

def write_system_logs(logs):
    emit('-- SystemLog')
    for l in logs:
        emit(f"INSERT INTO SystemLog (log_id, admin_id, message, timestamp, severity) "
             f"VALUES ({l['log_id']}, {l['admin_id']}, {escape(l['message'])}, "
             f"{escape(l['timestamp'])}, {escape(l['severity'])});")
    emit()


# MAIN
def main():
    # Generate all data
    students   = gen_students(35)
    professors = gen_professors(35)
    advisors   = gen_advisors(30)
    admins     = gen_admins(30)
    offerings  = gen_offerings(65)
    prof_offs  = gen_professor_offerings(offerings, professors, target=130)
    reviews    = gen_reviews(students, offerings, n=70)
    plans      = gen_plans(students, advisors, n=55)
    plan_crs   = gen_plan_courses(plans, target=140)
    flags      = gen_flags(reviews, students, admins, n=50)
    logs       = gen_system_logs(admins, n=55)

    # Print summary (For Debug)
    print('Generated:')
    print(f'  Department:         {len(DEPARTMENTS)}')
    print(f'  Course:             {len(COURSES)}')
    print(f'  Student:            {len(students)}')
    print(f'  Professor:          {len(professors)}')
    print(f'  AcademicAdvisor:    {len(advisors)}')
    print(f'  Admin:              {len(admins)}')
    print(f'  CourseOffering:     {len(offerings)}')
    print(f'  Review:             {len(reviews)}')
    print(f'  SemesterPlan:       {len(plans)}')
    print(f'  Flag:               {len(flags)}')
    print(f'  SystemLog:          {len(logs)}')
    print(f'  ProfessorOffering:  {len(prof_offs)}  (bridge)')
    print(f'  PlanCourse:         {len(plan_crs)}  (bridge)')

    # Build SQL file
    emit('USE uniscope;')
    emit()
    emit('-- Disable FK checks so TRUNCATE order does not matter')
    emit('SET FOREIGN_KEY_CHECKS = 0;')
    emit()
    emit('-- Clear existing data (safe to re-run)')
    for tbl in ['SystemLog', 'Flag', 'PlanCourse', 'SemesterPlan',
                'Review', 'ProfessorOffering', 'CourseOffering',
                'Course', 'Student', 'Professor', 'AcademicAdvisor',
                'Admin', 'Department']:
        emit(f'TRUNCATE TABLE {tbl};')
    emit()
    emit('SET FOREIGN_KEY_CHECKS = 1;')
    emit()
    emit('-- ============================================================')
    emit('-- INSERT DATA')
    emit('-- ============================================================')
    emit()

    write_departments()
    write_courses()
    write_students(students)
    write_professors(professors)
    write_advisors(advisors)
    write_admins(admins)
    write_offerings(offerings)
    write_professor_offerings(prof_offs)
    write_reviews(reviews)
    write_plans(plans)
    write_plan_courses(plan_crs)
    write_flags(flags)
    write_system_logs(logs)

    # Write to file
    out_path = os.path.abspath(OUTPUT_FILE)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'\nOutput written to: {out_path}')


if __name__ == '__main__':
    main()
