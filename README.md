# TrackHub — Project & Task Management API

A clean, modular Django + DRF backend for organizations, projects, sprints, tasks, labels, attachments, comments, time-tracking, and basic reports.
Auth uses JWT (SimpleJWT). Filtering with `django-filter`.

Apps:

* `accounts` — custom user (`Member`)
* `orgs` — organizations & memberships
* `projects` — projects, memberships, sprints, invites
* `tasks` — tasks, labels, attachments, comments, time entries
* `reports` — burndown, cycle time, workload

---

* JWT auth (`/api/auth/jwt/create`, `/api/auth/jwt/refresh`)
* Organization & project membership model
* Kanban-style tasks (Todo/Doing/Done) with ordering
* Labels, attachments (multipart), comments
* Project sprints
* Lightweight reports (burndown, cycle time, workload)
* Pagination, search, ordering, filtering

---

## Tech Stack

* Python 3.10+ (recommended)
* Django 4.x
* Django REST Framework
* SimpleJWT
* django-filter
* PostgreSQL 13+ (recommended)

## Quickstart (for local use)

### 1) Clone & create a virtualenv

```bash
git clone https://github.com/Foad-KhAb/TrackHub.git trackhub
cd trackhub
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) PostgreSQL: create DB & user

```bash
# Start postgres service first

# Set password for postgres superuser (Linux/macOS)
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
# You can change password and set in setting.py
# Create database (prefer lowercase to avoid quoting)
createdb -U postgres -h localhost -p 5432 trackhub
```
### 4) Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```
### 5) Create a superuser

```bash
python manage.py createsuperuser
```
After this command you should enter username and password.



### 6) Run the server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` (default port) to check admin and confirm models are there.

---

## API Overview

### Auth (JWT)

* `POST /api/auth/jwt/create` → `{ "email": "you@example.com", "password": "pass" }`
* `POST /api/auth/jwt/refresh` → `{ "refresh": "<token>" }`

Use `Authorization: Bearer <access>` header for protected endpoints.


### Organizations

* `GET/POST /api/orgs/` — list/create orgs you belong to
* `GET/PATCH/DELETE /api/orgs/{id}/` — retrieve/update/delete
* `GET/POST /api/orgs/{id}/members` — list/add members (POST expects `user_id`, optionally `role`)

### Projects

* `GET/POST /api/projects/` — list/create projects you’re a member of
* `GET/PATCH/DELETE /api/projects/{id}/`
* `POST /api/projects/{id}/invite` — body: `{ "email": "person@example.com" }`

### Tasks

* `GET/POST /api/projects/{project_id}/tasks/` — project-scoped list/create
  Filters: `?status=Doing&label=bug&search=timeout`
* `GET/PATCH/DELETE /api/tasks/{id}/`
* Actions:

  * `POST /api/tasks/{id}/move` — `{ "status": "Doing", "order": 12 }`
  * `POST /api/tasks/{id}/assign` — `{ "user_ids": [1,2] }`
  * `POST /api/tasks/{id}/labels` — `{ "label_ids": [1,2] }`
  * `POST /api/tasks/{id}/attachments` — multipart: `file=@path/to/file`
  * `GET/POST /api/tasks/{id}/comments`
  * `GET/POST /api/tasks/{id}/time-entries`

### Reports

* `GET /api/reports/burndown?sprint={sprint_id}`
* `GET /api/reports/cycle-time?project={project_id}`
* `GET /api/reports/workload?user={user_id}`

