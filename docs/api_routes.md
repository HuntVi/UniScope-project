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
