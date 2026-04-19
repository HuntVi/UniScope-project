DROP DATABASE IF EXISTS uniscope;

CREATE DATABASE IF NOT EXISTS uniscope;

USE uniscope;

-- =====================
-- CREATE TABLES
-- =====================

CREATE TABLE Department (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL
);

CREATE TABLE Student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    student_email VARCHAR(100) NOT NULL UNIQUE,
    department_id INT,
    total_hours INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE Professor (
    professor_id INT AUTO_INCREMENT PRIMARY KEY,
    professor_name VARCHAR(100) NOT NULL,
    professor_email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE AcademicAdvisor (
    advisor_id INT AUTO_INCREMENT PRIMARY KEY,
    advisor_name VARCHAR(100) NOT NULL,
    advisor_email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_name VARCHAR(100) NOT NULL,
    admin_email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Course (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    course_code VARCHAR(20) NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    credits INT NOT NULL,
    description TEXT,
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE CourseOffering (
    offering_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    semester VARCHAR(20) NOT NULL,
    year INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    offering_id INT NOT NULL,
    comment_text TEXT,
    review_date DATE NOT NULL,
    difficulty_score INT NOT NULL,
    workload_score INT NOT NULL,
    clarity_score INT NOT NULL,
    satisfaction_score INT NOT NULL,
    fairness_score INT NOT NULL,
    attendance_required BOOLEAN NOT NULL,
    weekly_hours DECIMAL(4,1) NOT NULL,
    status VARCHAR(20) DEFAULT 'approved',
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (offering_id) REFERENCES CourseOffering(offering_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE SemesterPlan (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    advisor_id INT,
    plan_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (advisor_id) REFERENCES AcademicAdvisor(advisor_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE Flag (
    flag_id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    reporter_id INT,
    resolved_by_admin_id INT,
    reason TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES Review(review_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (reporter_id) REFERENCES Student(student_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (resolved_by_admin_id) REFERENCES Admin(admin_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE SystemLog (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT,
    message TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    severity VARCHAR(20) NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE PlanCourse (
    plan_id INT NOT NULL,
    course_id INT NOT NULL,
    PRIMARY KEY (plan_id, course_id),
    FOREIGN KEY (plan_id) REFERENCES SemesterPlan(plan_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE ProfessorOffering (
    professor_id INT NOT NULL,
    offering_id INT NOT NULL,
    PRIMARY KEY (professor_id, offering_id),
    FOREIGN KEY (professor_id) REFERENCES Professor(professor_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (offering_id) REFERENCES CourseOffering(offering_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);
