import logging
from flask import Blueprint, current_app, jsonify, render_template, request

from . import db
from .workflow import CATEGORIES, PRIORITIES, STATUSES, ValidationError, run_workflow

bp = Blueprint("main", __name__)
log = logging.getLogger(__name__)


def _db():
    return current_app.config["DATABASE"]


@bp.route("/")
def index():
    return render_template("index.html", categories=CATEGORIES, priorities=PRIORITIES)


@bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", statuses=STATUSES)


@bp.route("/api/complaints", methods=["POST"])
def create_complaint():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be valid JSON."}), 400
    try:
        data = run_workflow(payload)
        complaint_id = db.insert_complaint(_db(), data)
    except ValidationError as exc:
        return jsonify({"error": "Validation failed.", "fields": exc.errors}), 422
    except db.DatabaseError:
        log.exception("Database failure while creating complaint")
        return jsonify({"error": "Server could not save the complaint. Please try again."}), 500

    log.info("Created %s (%s, %s)", complaint_id, data["category"], data["priority"])
    return jsonify({
        "complaint_id": complaint_id,
        "priority": data["priority"],
        "assigned_to": data["assigned_to"],
        "status": data["status"],
    }), 201


@bp.route("/api/complaints", methods=["GET"])
def get_complaints():
    status = request.args.get("status")
    if status and status not in STATUSES:
        return jsonify({"error": "Invalid status filter."}), 400
    try:
        return jsonify({
            "complaints": db.list_complaints(_db(), status),
            "counts": db.status_counts(_db()),
        })
    except db.DatabaseError:
        log.exception("Database failure while listing complaints")
        return jsonify({"error": "Could not load complaints."}), 500


@bp.route("/api/complaints/<complaint_id>", methods=["GET"])
def track_complaint(complaint_id):
    try:
        row = db.get_complaint(_db(), complaint_id.upper())
    except db.DatabaseError:
        log.exception("Database failure while tracking complaint")
        return jsonify({"error": "Could not look up complaint."}), 500
    if not row:
        return jsonify({"error": "Complaint not found."}), 404
    return jsonify(row)


@bp.route("/api/complaints/<complaint_id>/status", methods=["PATCH"])
def change_status(complaint_id):
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    if status not in STATUSES:
        return jsonify({"error": "Invalid status."}), 400
    try:
        updated = db.update_status(_db(), complaint_id.upper(), status)
    except db.DatabaseError:
        log.exception("Database failure while updating status")
        return jsonify({"error": "Could not update status."}), 500
    if not updated:
        return jsonify({"error": "Complaint not found."}), 404
    log.info("Status of %s changed to %s", complaint_id, status)
    return jsonify({"complaint_id": complaint_id.upper(), "status": status})
