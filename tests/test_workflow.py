import pytest
from app.workflow import (ValidationError, assign_team, escalate_priority,
                          run_workflow, validate_complaint)

VALID = {"name": "Asha Patel", "category": "Billing",
         "description": "I was charged twice this month.", "priority": "Low"}


def test_valid_input_passes():
    assert validate_complaint(VALID)["name"] == "Asha Patel"


@pytest.mark.parametrize("field,value", [
    ("name", ""), ("name", "A"), ("category", "Nope"),
    ("description", "short"), ("priority", "Urgent!!"),
])
def test_invalid_inputs_rejected(field, value):
    bad = {**VALID, field: value}
    with pytest.raises(ValidationError) as exc:
        validate_complaint(bad)
    assert field in exc.value.errors


def test_missing_fields_rejected():
    with pytest.raises(ValidationError) as exc:
        validate_complaint({})
    assert len(exc.value.errors) == 4


def test_priority_escalated_on_keyword():
    assert escalate_priority("Low", "This is URGENT please help") == "High"


def test_priority_unchanged_without_keyword():
    assert escalate_priority("Medium", "Please update my address") == "Medium"


def test_assignment_rules():
    assert assign_team("Billing") == "Finance Team"
    assert assign_team("Unknown") == "General Desk"


def test_run_workflow_sets_status_and_team():
    result = run_workflow(VALID)
    assert result["status"] == "Pending"
    assert result["assigned_to"] == "Finance Team"
