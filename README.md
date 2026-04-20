# UniScope

A data-driven course review and planning platform for Northeastern University students.

---

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

UniScope allows students to rate and review courses using structured metrics — difficulty, workload, clarity, satisfaction, fairness, weekly hours, and attendance requirements — so that future students can make informed decisions when planning their schedules.

### User Personas

- **Jason (Student)** — browse reviews, submit ratings, manage semester plans  
- **Josh (Professor)** — view aggregated course ratings, trends, and student feedback  
- **Muhammad (Academic Advisor)** — compare courses, evaluate semester plans, view student profiles  
- **Barry (System Admin)** — moderate reviews, resolve flags, monitor system logs  

---

## 🔄 How the System Works

UniScope follows a full-stack architecture connecting the user interface, backend API, and database.

### Flow of Data

1. User interacts with the Streamlit UI (selects course, submits review, etc.)
2. The UI sends an HTTP request to the Flask REST API
3. The Flask API processes the request and queries the MySQL database
4. The database returns the requested data
5. The API formats the response as JSON
6. The Streamlit UI renders the data (tables, charts, metrics)

**Flow:**  
UI → API → Database → API → UI

---

## Prerequisites

- Docker Desktop  
- Git  

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/HuntVi/UniScope-project
cd UniScope-project
```

---

### 2. Create your `.env` file

```bash
cp api/.env.example api/.env
```

Then edit `api/.env`:

```env
SECRET_KEY=any-random-string-you-choose
DB_USER=root
DB_HOST=db
DB_PORT=3306
DB_NAME=uniscope
MYSQL_ROOT_PASSWORD=your-own-password-here
```

---

### 3. Start the Docker containers

```bash
docker compose up -d
```

This starts:

- mysql_db (MySQL database on port 3200)  
- web-api (Flask API on port 4000)  
- web-app (Streamlit UI on port 8501)  

---

### 4. Verify the database

```sql
USE uniscope;

SELECT 'Department' AS tbl, COUNT(*) AS rows FROM Department
UNION ALL SELECT 'Course', COUNT(*) FROM Course
UNION ALL SELECT 'Student', COUNT(*) FROM Student
UNION ALL SELECT 'Professor', COUNT(*) FROM Professor
UNION ALL SELECT 'AcademicAdvisor', COUNT(*) FROM AcademicAdvisor
UNION ALL SELECT 'Admin', COUNT(*) FROM Admin
UNION ALL SELECT 'CourseOffering', COUNT(*) FROM CourseOffering
UNION ALL SELECT 'Review', COUNT(*) FROM Review
UNION ALL SELECT 'SemesterPlan', COUNT(*) FROM SemesterPlan
UNION ALL SELECT 'Flag', COUNT(*) FROM Flag
UNION ALL SELECT 'SystemLog', COUNT(*) FROM SystemLog
UNION ALL SELECT 'ProfessorOffering', COUNT(*) FROM ProfessorOffering
UNION ALL SELECT 'PlanCourse', COUNT(*) FROM PlanCourse;
```

Expected counts:  
35 / 35 / 35 / 35 / 30 / 30 / 65 / 70 / 55 / 50 / 55 / 130+ / 140+

---

### 5. Open the app

http://localhost:8501

---

## 🔌 API Overview

The backend is built using a Flask REST API with multiple blueprints.

### Main API Groups

- `/courses` — course catalog and analytics  
- `/reviews` — create/update/delete reviews  
- `/flags` — moderation system  
- `/systemlogs` — system logs  
- `/students` — student profiles  
- `/analytics` — workload insights  
- `/semesterplans` — course planning  

### Example Endpoints

- GET /courses  
- GET /courses/{id}/trends  
- POST /reviews  
- PUT /reviews/{id}  
- DELETE /reviews/{id}  
- POST /semesterplans  

All endpoints return JSON and follow REST principles.

---

## Useful Docker Commands

| Command | Purpose |
|---|---|
| docker compose up -d | Start containers |
| docker compose down | Stop containers |
| docker compose down db -v | Reset database |
| docker compose up db -d | Recreate database |
| docker compose restart | Restart containers |

---

## Project Structure

```
UniScope-project/
├── api/
├── app/src/
├── database-files/
└── scripts/
```

---

## 🎥 Demo Video

A 6–8 minute demo video showcasing:

- API functionality  
- Frontend features  
- Database interactions  

Link: (to be added before submission)
