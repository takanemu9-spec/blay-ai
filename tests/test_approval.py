import pytest
from app.core import director


def sample_plan(status="awaiting_approval"):
    return {
        "project_id": "approval-001",
        "status": status,
        "requires_approval": status == "awaiting_approval",
        "approval": {
            "status": "pending" if status == "awaiting_approval" else status,
            "decided_at": None,
        },
        "tasks": [],
    }


def setup_plan(monkeypatch, plan):
    monkeypatch.setattr(
        director, "get_plan",
        lambda project_id: plan
    )
    monkeypatch.setattr(
        director, "save_plan",
        lambda *args: None
    )


def test_approval_success(monkeypatch):
    plan = sample_plan()
    setup_plan(monkeypatch, plan)

    result = director.approve_plan("approval-001")

    assert result["status"] == "approved"
    assert result["requires_approval"] is False
    assert result["approval"]["status"] == "approved"
    assert result["approval"]["decided_at"] is not None


def test_rejection_success(monkeypatch):
    plan = sample_plan()
    setup_plan(monkeypatch, plan)

    result = director.reject_plan("approval-001")

    assert result["status"] == "rejected"
    assert result["requires_approval"] is False
    assert result["approval"]["status"] == "rejected"


def test_approval_repeated_rejected(monkeypatch):
    plan = sample_plan("approved")
    setup_plan(monkeypatch, plan)

    with pytest.raises(ValueError):
        director.approve_plan("approval-001")


def test_rejection_repeated_rejected(monkeypatch):
    plan = sample_plan("rejected")
    setup_plan(monkeypatch, plan)

    with pytest.raises(ValueError):
        director.reject_plan("approval-001")


def test_approval_after_rejection_rejected(monkeypatch):
    plan = sample_plan("rejected")
    setup_plan(monkeypatch, plan)

    with pytest.raises(ValueError):
        director.approve_plan("approval-001")


def test_rejection_after_approval_rejected(monkeypatch):
    plan = sample_plan("approved")
    setup_plan(monkeypatch, plan)

    with pytest.raises(ValueError):
        director.reject_plan("approval-001")


def test_approval_missing_project(monkeypatch):
    setup_plan(monkeypatch, None)

    with pytest.raises(ValueError):
        director.approve_plan("missing-project")


def test_rejection_missing_project(monkeypatch):
    setup_plan(monkeypatch, None)

    with pytest.raises(ValueError):
        director.reject_plan("missing-project")
