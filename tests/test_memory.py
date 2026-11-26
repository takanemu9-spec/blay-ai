import sqlite3

import pytest

from app.core import memory


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_memory.db"
    monkeypatch.setattr(memory, "DB_PATH", db_path)
    return db_path


def make_plan(project_id="project-001"):
    return {
        "project_id": project_id,
        "status": "created",
        "instruction": "Test memory engine",
        "tasks": [{"agent": "Research Agent"}],
    }


def test_save_and_get_plan(isolated_db):
    plan = make_plan()

    memory.save_plan(plan)

    result = memory.get_plan("project-001")

    assert result == plan


def test_update_existing_plan(isolated_db):
    plan = make_plan()
    memory.save_plan(plan)

    updated = make_plan()
    updated["status"] = "approved"

    memory.save_plan(updated)

    result = memory.get_plan("project-001")

    assert result["status"] == "approved"

    with memory.get_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM projects"
        ).fetchone()[0]

    assert count == 1


def test_save_and_get_memory_events(isolated_db):
    plan = make_plan()

    memory.save_plan(
        plan,
        "project_created",
        {"source": "test"}
    )

    events = memory.get_project_events("project-001")

    assert len(events) == 1
    assert events[0]["event_type"] == "project_created"
    assert events[0]["details"] == {"source": "test"}


def test_multiple_events_keep_order(isolated_db):
    plan = make_plan()

    memory.save_plan(plan, "created")
    memory.save_plan(plan, "updated")
    memory.save_plan(plan, "approved")

    events = memory.get_project_events("project-001")

    assert [
        event["event_type"] for event in events
    ] == ["created", "updated", "approved"]


def test_project_memory_isolation(isolated_db):
    memory.save_plan(make_plan("project-A"), "created")
    memory.save_plan(make_plan("project-B"), "updated")

    events_a = memory.get_project_events("project-A")
    events_b = memory.get_project_events("project-B")

    assert len(events_a) == 1
    assert len(events_b) == 1

    assert events_a[0]["event_type"] == "created"
    assert events_b[0]["event_type"] == "updated"


def test_missing_project_returns_none(isolated_db):
    assert memory.get_plan("missing-project") is None


def test_missing_project_events_returns_empty(isolated_db):
    assert memory.get_project_events("missing-project") == []


def test_delete_project_cascades_events(isolated_db):
    memory.save_plan(make_plan(), "created")

    with memory.get_connection() as conn:
        conn.execute(
            "DELETE FROM projects WHERE project_id = ?",
            ("project-001",)
        )

    assert memory.get_project_events("project-001") == []
    assert memory.get_plan("project-001") is None
