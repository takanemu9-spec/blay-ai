import pytest
from app.core import director


def sample_plan():
    return {
        "project_id": "test-001",
        "status": "awaiting_approval",
        "requires_approval": True,
        "approval": {
            "status": "pending",
            "decided_at": None,
        },
        "tasks": [],
    }


def test_create_plan_success(monkeypatch):
    monkeypatch.setattr(
        director, "save_plan", lambda *args: None
    )

    plan = director.create_plan("Buat proyek BLAY")

    assert plan["status"] == "awaiting_approval"
    assert plan["requires_approval"] is True
    assert plan["approval"]["status"] == "pending"
    assert len(plan["project_id"]) > 0


def test_create_plan_rejects_empty_prompt():
    with pytest.raises(ValueError):
        director.create_plan("")


def test_approve_plan_success(monkeypatch):
    plan = sample_plan()

    monkeypatch.setattr(
        director, "get_plan", lambda project_id: plan
    )
    monkeypatch.setattr(
        director, "save_plan", lambda *args: None
    )

    result = director.approve_plan("test-001")

    assert result["status"] == "approved"
    assert result["requires_approval"] is False
    assert result["approval"]["status"] == "approved"


def test_reject_plan_success(monkeypatch):
    plan = sample_plan()

    monkeypatch.setattr(
        director, "get_plan", lambda project_id: plan
    )
    monkeypatch.setattr(
        director, "save_plan", lambda *args: None
    )

    result = director.reject_plan("test-001")

    assert result["status"] == "rejected"
    assert result["requires_approval"] is False
    assert result["approval"]["status"] == "rejected"


def test_approve_rejects_wrong_status(monkeypatch):
    plan = sample_plan()
    plan["status"] = "approved"

    monkeypatch.setattr(
        director, "get_plan", lambda project_id: plan
    )

    with pytest.raises(ValueError):
        director.approve_plan("test-001")


def test_reject_missing_project(monkeypatch):
    monkeypatch.setattr(
        director, "get_plan", lambda project_id: None
    )

    with pytest.raises(ValueError):
        director.reject_plan("missing-project")
