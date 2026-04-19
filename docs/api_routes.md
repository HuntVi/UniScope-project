# UniScope API Routes — Haozhe's Blueprints

Blueprints: `departments`, `reviews`, `flags`, `systemlogs`  
Base URL: `http://localhost:4000`  
All responses are JSON. Dates/timestamps are ISO 8601 strings.

---

## Departments

### `GET /departments`
Returns all departments, sorted alphabetically. Used to populate department dropdowns on any persona page.

**Query params:** none

**Returns:** `200`
```json
[
  { "department_id": 3, "department_name": "Computer Science" },
  { "department_id": 7, "department_name": "Mathematics" }
]
```

---

### `GET /departments/{departmentID}/courses`
Returns all courses in a department with aggregated review metrics. Only `approved` reviews count toward averages; courses with no reviews return `null` for metric fields.

**URL param:** `departmentID` — integer

**Query params:** none

**Returns:** `200`
```json
[
  {
    "course_id": 12,
    "course_code": "CS 3200",
    "course_name": "Database Design",
    "credits": 4,
    "description": "...",
    "avg_difficulty": 3.75,
    "avg_workload": 4.10,
    "avg_clarity": 3.50,
    "avg_satisfaction": 4.00,
    "review_count": 8
  }
]
```
**Returns:** `404` if department does not exist or has no courses.

---

## Reviews

### `GET /reviews`
Returns reviews with student and course context. Both filters are optional and combinable.

**Query params:**

| Param | Type | Description |
|---|---|---|
| `status` | string | Filter by `approved`, `pending`, or `rejected` |
| `student_id` | int | Filter to one student's reviews only |

**Usage:**
- `GET /reviews` — all reviews (Barry's moderation list)
- `GET /reviews?status=pending` — reviews needing moderation
- `GET /reviews?student_id=4` — Jason's own reviews
- `GET /reviews?student_id=4&status=approved` — combinable

**Returns:** `200` — list of review objects:
```json
[
  {
    "review_id": 5,
    "student_id": 4,
    "offering_id": 12,
    "comment_text": "Great course!",
    "review_date": "2024-11-15",
    "difficulty_score": 4,
    "workload_score": 3,
    "clarity_score": 5,
    "satisfaction_score": 4,
    "fairness_score": 4,
    "attendance_required": true,
    "weekly_hours": 8.0,
    "status": "approved",
    "student_name": "Jason Lee",
    "course_code": "CS 3200",
    "course_name": "Database Design",
    "semester": "Fall",
    "year": 2024
  }
]
```

---

### `POST /reviews`
Creates a new review. Status is set to `approved` immediately — becomes `pending` only if later flagged.

**Body (JSON):**

| Field | Type | Required | Notes |
|---|---|---|---|
| `student_id` | int | ✓ | |
| `offering_id` | int | ✓ | Use `GET /courses/{id}/offerings` to get valid IDs |
| `difficulty_score` | int | ✓ | 1–5 |
| `workload_score` | int | ✓ | 1–5 |
| `clarity_score` | int | ✓ | 1–5 |
| `satisfaction_score` | int | ✓ | 1–5 |
| `fairness_score` | int | ✓ | 1–5 |
| `attendance_required` | bool | ✓ | |
| `weekly_hours` | float | ✓ | |
| `comment_text` | string | — | Optional free-text comment |

**Returns:** `201`
```json
{ "review_id": 71, "message": "Review created" }
```
**Returns:** `400` if any required field is missing.

---

### `GET /reviews/{reviewID}`
Returns full detail for one review.

**URL param:** `reviewID` — integer

**Returns:** `200` — single review object (same shape as `GET /reviews` items)  
**Returns:** `404` if review not found.

---

### `PUT /reviews/{reviewID}`
Updates one or more fields on an existing review. Send only the fields you want to change.

**URL param:** `reviewID` — integer

**Body (JSON) — any subset of:**

| Field | Who uses it |
|---|---|
| `comment_text` | Student (edit own comment) |
| `difficulty_score` | Student |
| `workload_score` | Student |
| `clarity_score` | Student |
| `satisfaction_score` | Student |
| `fairness_score` | Student |
| `attendance_required` | Student |
| `weekly_hours` | Student |
| `status` | Admin (set `approved` / `rejected`) |

**Returns:** `200 { "message": "Review updated" }`  
**Returns:** `400` if no valid fields provided.  
**Returns:** `404` if review not found.

---

### `DELETE /reviews/{reviewID}`
Permanently deletes a review. Cascades to any flags on that review.

**URL param:** `reviewID` — integer

**Returns:** `200 { "message": "Review deleted" }`  
**Returns:** `404` if review not found.

---

## Flags

### `GET /flags`
**Default (no params):** returns only unresolved flags (`resolved_at IS NULL`) — Barry's active queue.  
**With any search param:** the unresolved filter is lifted and ALL flags (resolved + unresolved) matching the criteria are returned.

**Query params:**

| Param | Type | Description |
|---|---|---|
| `course_id` | int | Flags on reviews for a specific course |
| `reporter_name` | string | Partial match on reporter's name (LIKE) |
| `reason` | string | Partial match on flag reason text (LIKE) |
| `review_status` | string | Filter by linked review's status (`approved`/`pending`/`rejected`) |
| `since` | YYYY-MM-DD | Flags created on or after this date |
| `resolved_since` | YYYY-MM-DD | Flags resolved on or after this date |
| `system_only` | `true` | Only system-generated flags (no reporter) |

**Usage:**
- `GET /flags` — unresolved queue
- `GET /flags?course_id=5` — all flags (any status) for course 5
- `GET /flags?since=2026-04-01` — all flags since April 1
- `GET /flags?system_only=true` — auto-generated flags only
- `GET /flags?reporter_name=john&since=2026-04-01` — combinable

**Returns:** `200`
```json
[
  {
    "flag_id": 3,
    "review_id": 5,
    "reporter_id": 4,
    "resolved_by_admin_id": null,
    "reason": "Offensive language",
    "created_at": "2026-04-10T14:32:00",
    "resolved_at": null,
    "reporter_name": "Jason Lee",
    "resolver_name": null,
    "review_comment": "This course is terrible...",
    "review_status": "pending",
    "course_id": 12,
    "course_code": "CS 3200",
    "course_name": "Database Design"
  }
]
```

---

### `POST /flags`
Creates a flag on a review AND atomically sets the review's status to `pending`. Both happen in one transaction — if either fails, neither is saved.

**Body (JSON):**

| Field | Type | Required | Notes |
|---|---|---|---|
| `review_id` | int | ✓ | The review being flagged |
| `reason` | string | ✓ | Explanation of the flag |
| `reporter_id` | int | — | Omit for system-generated flags |

**Returns:** `201`
```json
{ "flag_id": 4, "message": "Flag created and review marked as pending" }
```
**Returns:** `400` if `review_id` or `reason` is missing.  
**Returns:** `500` if the transaction fails (both writes rolled back).

---

### `PUT /flags/{flagID}`
Marks a flag as resolved. Records who resolved it and when.  
Note: this only closes the flag — use `PUT /reviews/{id}` separately to set the review's final status.

**URL param:** `flagID` — integer

**Body (JSON):**

| Field | Type | Required |
|---|---|---|
| `resolved_by_admin_id` | int | ✓ |

**Returns:** `200 { "message": "Flag resolved" }`  
**Returns:** `400` if `resolved_by_admin_id` is missing.  
**Returns:** `404` if flag not found.

---

## System Logs

### `GET /systemlogs`
**Default (no params):** returns logs from the **last 7 days** — Barry's live health dashboard.  
**With any search param:** the 7-day window is lifted and the full log history is searched.

**Query params:**

| Param | Type | Description |
|---|---|---|
| `severity` | string | Exact match: `INFO`, `WARNING`, or `ERROR` |
| `admin_name` | string | Partial match on admin name (LIKE) |
| `message` | string | Partial match on log message content (LIKE) |
| `since` | YYYY-MM-DD | Logs on or after this date |
| `until` | YYYY-MM-DD | Logs on or before this date |
| `system_only` | `true` | Only system-generated logs (no admin) |

**Usage:**
- `GET /systemlogs` — last 7 days
- `GET /systemlogs?severity=ERROR` — all errors ever
- `GET /systemlogs?since=2026-04-01&until=2026-04-10` — date range
- `GET /systemlogs?message=timeout` — logs mentioning "timeout"
- `GET /systemlogs?system_only=true` — automated system events only

**Returns:** `200`
```json
[
  {
    "log_id": 22,
    "admin_id": 2,
    "message": "Duplicate review detected for offering 14",
    "timestamp": "2026-04-15T09:12:44",
    "severity": "WARNING",
    "admin_name": "Barry Admin"
  }
]
```

---

### `POST /systemlogs`
Creates a new log entry. `admin_id` is optional — omit it for automated system events.

**Body (JSON):**

| Field | Type | Required | Notes |
|---|---|---|---|
| `message` | string | ✓ | Log message text |
| `severity` | string | ✓ | Must be `INFO`, `WARNING`, or `ERROR` |
| `admin_id` | int | — | Omit for system-generated events |

**Returns:** `201`
```json
{ "log_id": 56, "message": "Log entry created" }
```
**Returns:** `400` if `message` or `severity` is missing, or severity is invalid.

---

## Review Status Lifecycle (Reference)

```
POST /reviews          → status = 'approved'   (live immediately)
POST /flags            → status = 'pending'    (pulled from view, atomically)
PUT  /reviews/{id}     → status = 'approved'   (Barry clears the review)
PUT  /reviews/{id}     → status = 'rejected'   (Barry removes the review)
PUT  /flags/{id}       → flag closed           (review status unchanged — decide separately)
```


# UniScope API Routes — Michael's Blueprints

Blueprints: `courses`, `students`, `analytics`, `semester_plans`  
Base URL: `http://localhost:4000`  
All responses are JSON. Dates/timestamps are ISO 8601 strings.

---

## Courses

### `GET /courses`
Returns all courses with aggregated metrics such as average difficulty, workload, clarity, satisfaction, review count, and credits. Rejected reviews are excluded from the aggregates.

**Query params:** none

**Usage:**
- `GET /courses` — full course catalog for browsing
- Used on course exploration pages, comparison pages, and advisor planning pages
- Frontend can optionally sort or filter the returned list client-side

**Returns:** `200`
```json
[
  {
    "course_id": 12,
    "department_id": 3,
    "course_code": "CS 3200",
    "course_name": "Database Design",
    "credits": 4,
    "description": "Introduction to relational database design and SQL.",
    "avg_difficulty": 3.75,
    "avg_workload": 4.10,
    "avg_clarity": 3.50,
    "avg_satisfaction": 4.00,
    "review_count": 8
  }
]
```

---

### `GET /courses/{course_id}`
Returns one course with summary-level aggregated review metrics. Rejected reviews are excluded from the aggregates.

**URL param:** `course_id` — integer

**Query params:** none

**Usage:**
- `GET /courses/12` — course detail page
- Used when a user selects a course from the course catalog
- Useful for showing summary metrics before opening reviews/trends/offering history

**Returns:** `200`
```json
[
  {
    "course_id": 12,
    "department_id": 3,
    "course_code": "CS 3200",
    "course_name": "Database Design",
    "credits": 4,
    "description": "Introduction to relational database design and SQL.",
    "avg_difficulty": 3.75,
    "avg_workload": 4.10,
    "avg_clarity": 3.50,
    "avg_satisfaction": 4.00,
    "review_count": 8
  }
]
```

**Returns:** `404` if course not found

---

### `GET /courses/{course_id}/reviews`
Returns all non-rejected reviews for a specific course. Includes semester and year from the linked course offering.

**URL param:** `course_id` — integer

**Query params:** none

**Usage:**
- `GET /courses/12/reviews` — display all visible reviews for course 12
- Used on course detail pages when the user wants full review text and ratings
- Helpful for students comparing courses and advisors answering course experience questions

**Returns:** `200`
```json
[
  {
    "review_id": 5,
    "student_id": 4,
    "offering_id": 12,
    "comment_text": "Great course!",
    "review_date": "2024-11-15",
    "difficulty_score": 4,
    "workload_score": 3,
    "clarity_score": 5,
    "satisfaction_score": 4,
    "fairness_score": 4,
    "attendance_required": true,
    "weekly_hours": 8.0,
    "status": "approved",
    "semester": "Fall",
    "year": 2024
  }
]
```

---

### `GET /courses/{course_id}/trends`
Returns trend data for a course across semesters and years. Aggregates exclude rejected reviews.

**URL param:** `course_id` — integer

**Query params:** none

**Usage:**
- `GET /courses/12/trends` — show trend chart for course 12
- Used for visualizing how satisfaction, workload, or difficulty changes over time
- Helpful for advisor dashboards and course analytics views

**Returns:** `200`
```json
[
  {
    "year": 2023,
    "semester": "Fall",
    "avg_difficulty": 3.40,
    "avg_workload": 3.90,
    "avg_satisfaction": 4.20,
    "review_count": 5
  },
  {
    "year": 2024,
    "semester": "Spring",
    "avg_difficulty": 3.60,
    "avg_workload": 4.00,
    "avg_satisfaction": 4.10,
    "review_count": 7
  }
]
```

---

### `GET /courses/{course_id}/reviewsummary`
Returns a summarized review snapshot for one course. Useful when the UI needs high-level review insights without showing every raw review.

**URL param:** `course_id` — integer

**Query params:** none

**Usage:**
- `GET /courses/12/reviewsummary` — quick insight panel for course 12
- Used by professor/advisor-style dashboard views
- Good for summary cards, ranking panels, or highlights sections

**Returns:** `200`
```json
[
  {
    "course_id": 12,
    "course_code": "CS 3200",
    "course_name": "Database Design",
    "review_count": 8,
    "avg_difficulty": 3.75,
    "avg_workload": 4.10,
    "avg_clarity": 3.50,
    "avg_satisfaction": 4.00,
    "avg_fairness": 4.12,
    "avg_weekly_hours": 7.80
  }
]
```

**Returns:** `404` if course not found

---

### `GET /courses/{course_id}/offerings`
Returns all offerings for a course, including semester, year, and professors who taught that offering. Offerings are sorted with newer years first.

**URL param:** `course_id` — integer

**Query params:** none

**Usage:**
- `GET /courses/12/offerings` — show offering history for course 12
- Used when creating a review so a student can choose the correct offering
- Helpful on course detail pages to show when the course was offered and who taught it

**Returns:** `200`
```json
[
  {
    "offering_id": 18,
    "semester": "Fall",
    "year": 2025,
    "professors": "Prof A, Prof B"
  },
  {
    "offering_id": 11,
    "semester": "Spring",
    "year": 2025,
    "professors": "Prof C"
  }
]
```

**Returns:** `404` if no offerings found for that course

---

## Students

### `GET /students/{studentID}`
Returns a student profile including academic year, department, and total completed hours.

**URL param:** `studentID` — integer

**Query params:** none

**Usage:**
- `GET /students/4` — advisor view of one student's academic profile
- Used for semester planning and advising pages
- Helpful when giving context before building a semester plan

**Returns:** `200`
```json
{
  "student_id": 4,
  "student_name": "Jason Lee",
  "academic_year": "Junior",
  "department": "Computer Science",
  "total_hours": 64
}
```

**Returns:** `404` if student not found

---

## Analytics

### `GET /analytics/workload`
Returns dashboard-style workload data across courses. Rows include aggregated workload, difficulty, and weekly hours, and courses with no valid review data are filtered out.

**Query params:** none

**Usage:**
- `GET /analytics/workload` — advisor workload dashboard
- Used to identify difficult or time-intensive courses
- Helpful when evaluating whether course combinations may be too stressful

**Returns:** `200`
```json
[
  {
    "course_id": 12,
    "course_code": "CS 3200",
    "course_name": "Database Design",
    "avg_difficulty": 3.75,
    "avg_workload": 4.10,
    "avg_weekly_hours": 7.80,
    "review_count": 8
  }
]
```

---

## Semester Plans

### `POST /semesterplans`
Creates a new semester plan.

**Body (JSON):**

| Field | Type | Required | Notes |
|---|---|---|---|
| `student_id` | int | — | Nullable in the schema |
| `advisor_id` | int | — | Nullable in the schema |
| `plan_name` | string | ✓ | Required plan name |

**Usage:**
- `POST /semesterplans` — create a new empty plan before adding courses
- Used by students or advisors starting a schedule draft
- Works even if `student_id` or `advisor_id` is omitted, as long as `plan_name` is present

**Returns:** `201`
```json
{
  "plan_id": 56,
  "student_id": 1,
  "advisor_id": 2,
  "plan_name": "Fall Plan"
}
```

**Returns:** `400` if request body is missing or `plan_name` is missing

---

### `GET /semesterplans/{planID}`
Returns one semester plan with summary metrics and the list of courses currently in that plan. Summary values are computed from the linked course metrics.

**URL param:** `planID` — integer

**Query params:** none

**Usage:**
- `GET /semesterplans/56` — open an existing semester plan
- Used for semester plan detail pages and advisor evaluation pages
- Helps determine whether a plan looks balanced and manageable

**Returns:** `200`
```json
{
  "plan_id": 56,
  "student_id": 1,
  "advisor_id": 2,
  "plan_name": "Fall Plan",
  "total_courses": 4,
  "total_credits": 16,
  "avg_difficulty": 3.50,
  "avg_workload": 4.00,
  "avg_satisfaction": 4.20,
  "total_avg_weekly_hours": 18.50,
  "is_manageable": true,
  "warning": null,
  "courses": [
    {
      "course_id": 12,
      "course_code": "CS 3200",
      "course_name": "Database Design",
      "credits": 4,
      "avg_difficulty": 3.75,
      "avg_workload": 4.10,
      "avg_satisfaction": 4.00,
      "avg_weekly_hours": 7.80,
      "review_count": 8
    }
  ]
}
```

**Returns:** `404` if semester plan not found

---

### `DELETE /semesterplans/{planID}`
Deletes one semester plan. Related `PlanCourse` rows are also removed automatically by cascade.

**URL param:** `planID` — integer

**Query params:** none

**Usage:**
- `DELETE /semesterplans/56` — remove a plan that is no longer needed
- Used when a student or advisor wants to discard a draft plan

**Returns:** `200`
```json
{
  "message": "Semester plan 56 deleted successfully",
  "plan_id": 56
}
```

**Returns:** `404` if semester plan not found

---

### `POST /semesterplans/{planID}/courses/{course_id}`
Adds a course to an existing semester plan.

**URL params:**
- `planID` — integer
- `course_id` — integer

**Query params:** none

**Usage:**
- `POST /semesterplans/56/courses/12` — add course 12 to plan 56
- Used in semester plan builders when a user selects a course to include
- Prevents duplicate entries for the same course-plan pair

**Returns:** `201`
```json
{
  "plan_id": 56,
  "course_id": 12,
  "message": "Course 12 added to semester plan 56"
}
```

**Returns:** `404` if plan or course not found  
**Returns:** `409` if course is already in the plan

---

### `DELETE /semesterplans/{planID}/courses/{course_id}`
Removes a course from an existing semester plan.

**URL params:**
- `planID` — integer
- `course_id` — integer

**Query params:** none

**Usage:**
- `DELETE /semesterplans/56/courses/12` — remove course 12 from plan 56
- Used when rebalancing or revising a semester plan
- Checks that the course-plan relationship currently exists before deleting

**Returns:** `200`
```json
{
  "message": "Course 12 removed from semester plan 56",
  "plan_id": 56,
  "course_id": 12
}
```

**Returns:** `404` if plan not found, course not found, or course is not in the plan

---

## Semester Plan Logic Notes (Reference)

```text
POST /semesterplans                         → creates a new empty plan
GET  /semesterplans/{id}                    → returns plan + computed summary metrics
POST /semesterplans/{id}/courses/{course}   → adds one course to the plan
DELETE /semesterplans/{id}/courses/{course} → removes one course from the plan
DELETE /semesterplans/{id}                  → deletes the whole plan
```

Additional notes:
- `is_manageable` is based on whether `total_avg_weekly_hours <= 20`
- `warning` is populated when the workload threshold is exceeded
- Plan summary metrics are computed in Python after fetching the courses
