# Automated Complaint Management System

Python (Flask) + SQLite + HTML/CSS/JavaScript project that automates receiving,
validating, prioritising, assigning and tracking customer complaints.

## Workflow
1. User submits a complaint (name, category, priority, description).
2. **JavaScript** validates the form in the browser.
3. **Python** re-validates (server side), escalates priority if urgent keywords
   are found, assigns the responsible team, sets status `Pending`.
4. **SQLite** stores the record and generates an ID like `CMP-2026-0001`.
5. **Dashboard** shows Pending / In Progress / Resolved counts, filter, and status updates.

## Project structure
```
app/
  __init__.py   app factory, logging
  db.py         all SQL + DatabaseError handling
  workflow.py   validation + automation rules (priority, assignment)
  routes.py     REST API + pages, error responses (400/404/422/500)
  templates/    index.html, dashboard.html, base.html
  static/       style.css, form.js, dashboard.js
tests/          pytest tests (valid/invalid input, workflow, DB failure)
run.py          entry point
```

## Setup (VS Code / PyCharm / any IDE)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run.py
```
Open http://127.0.0.1:5000

## Run tests
```bash
pytest -v
```

## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/complaints | Create complaint |
| GET | /api/complaints?status=Pending | List + counts |
| GET | /api/complaints/<id> | Track one complaint |
| PATCH | /api/complaints/<id>/status | Update status |

## Ideas to extend (good interview talking points)
- Add login for admin vs customer
- Email notification when status changes
- Deploy on Render / PythonAnywhere
- Add SLA deadlines by priority
