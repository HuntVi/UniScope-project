# UniScope

A data-driven course review and planning platform for Northeastern University students.

## Team: Raiders of the Lost Class

| Name | Email |
|---|---|
| Hunter Wissmann | wissmann.h@northeastern.edu |
| Jiaen Ma | ma.jiae@northeastern.edu |
| Haozhe Zhu | zhu.haozh@northeastern.edu |
| Yuqiu Wang | wang.yuqiu@northeastern.edu |
| Michael Atsuya | atsuya.m@northeastern.edu |

---

## Project Overview

UniScope allows students to rate and review courses with structured data — difficulty, workload, clarity, satisfaction, fairness, weekly hours, and attendance requirements — so that future students can make informed decisions when planning their schedules.

**Four user personas:**
- **Jason** (Student) — browse reviews, submit ratings, manage semester plans
- **Josh** (Professor) — view aggregated course ratings, trends, and student feedback
- **Muhammad** (Academic Advisor) — compare courses, evaluate semester plans, view student profiles
- **Barry** (System Admin) — moderate reviews, resolve flags, monitor system logs

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Git

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repo-url>
cd UniScope-project
```

### 2. Create your `.env` file

The `.env` file is **not committed to Git** for security reasons. You must create it manually:

```bash
# In the api/ folder, copy the example file
cp api/.env.example api/.env
```

Then open `api/.env` and set your own password:

```
SECRET_KEY=any-random-string-you-choose
DB_USER=root
DB_HOST=db
DB_PORT=3306
DB_NAME=uniscope
MYSQL_ROOT_PASSWORD=your-own-password-here
```

> Each teammate sets their **own** password — it only applies to their local container.

### 3. Start the Docker containers

```bash
docker compose up -d
```

This starts three containers:
- `mysql_db` — MySQL database on port **3200**
- `web-api` — Flask REST API on port **4000**
- `web-app` — Streamlit UI on port **8501**

On first creation, MySQL automatically executes all `.sql` files in `database-files/` in alphabetical order:
1. `uniscope.sql` — creates the database schema (tables + FK rules)
2. `uniscope_data.sql` — inserts all mock data (35 departments, 35 courses, 35 students, etc.)

### 4. Verify the database loaded correctly

Connect DataGrip to `localhost:3200` (user: `root`, password: whatever you set) and run:

```sql
USE uniscope;

SELECT 'Department'       AS tbl, COUNT(*) AS rows FROM Department
UNION ALL SELECT 'Course',            COUNT(*) FROM Course
UNION ALL SELECT 'Student',           COUNT(*) FROM Student
UNION ALL SELECT 'Professor',         COUNT(*) FROM Professor
UNION ALL SELECT 'AcademicAdvisor',   COUNT(*) FROM AcademicAdvisor
UNION ALL SELECT 'Admin',             COUNT(*) FROM Admin
UNION ALL SELECT 'CourseOffering',    COUNT(*) FROM CourseOffering
UNION ALL SELECT 'Review',            COUNT(*) FROM Review
UNION ALL SELECT 'SemesterPlan',      COUNT(*) FROM SemesterPlan
UNION ALL SELECT 'Flag',              COUNT(*) FROM Flag
UNION ALL SELECT 'SystemLog',         COUNT(*) FROM SystemLog
UNION ALL SELECT 'ProfessorOffering', COUNT(*) FROM ProfessorOffering
UNION ALL SELECT 'PlanCourse',        COUNT(*) FROM PlanCourse;
```

Expected counts: 35 / 35 / 35 / 35 / 30 / 30 / 65 / 70 / 55 / 50 / 55 / 130+ / 140+

### 5. Open the app

Navigate to [http://localhost:8501](http://localhost:8501)

---

## Useful Docker Commands

| Command | Purpose |
|---|---|
| `docker compose up -d` | Start all containers in background |
| `docker compose down` | Stop and remove containers |
| `docker compose down db -v` | **Fully reset** database (deletes volume) |
| `docker compose up db -d` | Recreate only the database container |
| `docker compose restart` | Restart all containers (keeps data) |

> **When to reset the database:** If you change `uniscope.sql` (schema changes), you must fully reset: `docker compose down db -v` then `docker compose up db -d`. Simply restarting won't re-run the SQL files.

---

## Project Structure

```
UniScope-project/
├── api/                        Flask REST API
│   ├── backend/
│   │   ├── students/           Jason persona routes
│   │   ├── professors/         Josh persona routes
│   │   ├── advisors/           Muhammad persona routes
│   │   ├── admin/              Barry persona routes
│   │   └── db_connection/      MySQL connection manager
│   ├── .env.example            Template for .env (copy this)
│   └── backend_app.py          API entry point
├── app/src/                    Streamlit UI
│   ├── Home.py                 Landing page (persona select)
│   ├── pages/
│   │   ├── 00_Student_Home.py
│   │   ├── 01_Course_Reviews.py
│   │   ├── 02_Submit_Review.py
│   │   ├── 03_Semester_Plan.py
│   │   ├── 10_Professor_Home.py
│   │   ├── 11_Course_Ratings.py
│   │   ├── 12_Course_Trends.py
│   │   ├── 13_Student_Feedback.py
│   │   ├── 20_Advisor_Home.py
│   │   ├── 21_Course_Comparison.py
│   │   ├── 22_Student_Profile.py
│   │   ├── 23_Plan_Evaluator.py
│   │   ├── 30_Admin_Home.py
│   │   ├── 31_Review_Moderation.py
│   │   ├── 32_Flag_Management.py
│   │   └── 33_System_Logs.py
│   └── modules/nav.py          Sidebar navigation by role
├── database-files/
│   ├── uniscope.sql            DDL — table definitions
│   └── uniscope_data.sql       Mock data — INSERT statements
└── scripts/
    └── generate_data.py        Mock data generator (Faker)
```

---

## Demo Video

*Link to be added before submission.*
