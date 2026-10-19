"""Automation rules: validation, priority escalation, and auto-assignment."""

CATEGORIES = ["Billing", "Technical", "Service", "Product", "Other"]
PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Pending", "In Progress", "Resolved"]

# Which team handles which category
ASSIGNMENT_RULES = {
    "Billing": "Finance Team",
    "Technical": "Tech Support Team",
    "Service": "Customer Care Team",
    "Product": "Product Team",
    "Other": "General Desk",
}

# If the description contains these words, priority is escalated to High
URGENT_KEYWORDS = ["urgent", "emergency", "immediately", "danger", "outage", "fraud", "not working"]


class ValidationError(Exception):
    def __init__(self, errors):
        super().__init__("Validation failed")
        self.errors = errors


def validate_complaint(data):
    """Server-side validation (never trust only the browser)."""
    errors = {}
    name = str(data.get("name") or "").strip()
    category = str(data.get("category") or "").strip()
    description = str(data.get("description") or "").strip()
    priority = str(data.get("priority") or "").strip()

    if len(name) < 2:
        errors["name"] = "Name must be at least 2 characters."
    elif len(name) > 100:
        errors["name"] = "Name is too long (max 100)."
    if category not in CATEGORIES:
        errors["category"] = "Please select a valid category."
    if len(description) < 10:
        errors["description"] = "Description must be at least 10 characters."
    elif len(description) > 1000:
        errors["description"] = "Description is too long (max 1000)."
    if priority not in PRIORITIES:
        errors["priority"] = "Please select a valid priority."

    if errors:
        raise ValidationError(errors)
    return {"name": name, "category": category, "description": description, "priority": priority}


def escalate_priority(priority, description):
    """Rule: urgent keywords force High priority."""
    text = description.lower()
    if any(word in text for word in URGENT_KEYWORDS):
        return "High"
    return priority


def assign_team(category):
    return ASSIGNMENT_RULES.get(category, "General Desk")


def run_workflow(data):
    """Validate -> escalate priority -> assign team -> set initial status."""
    clean = validate_complaint(data)
    clean["priority"] = escalate_priority(clean["priority"], clean["description"])
    clean["assigned_to"] = assign_team(clean["category"])
    clean["status"] = "Pending"
    return clean
