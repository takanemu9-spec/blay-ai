import pytest
from app.core import executor


def sample_plan():
    return {
        "project_id": "executor-test-001",
        "status": "approved",
        "requires_approval": False,
        "tasks": [
            {
                "agent": "Research Agent",
                "task": "Test execution",
                "status": "pending",
                "result": None,
            }
        ],
        "execution": {
            "status": "idle",
            "started_at": None,
            "completed_at": None,
            "error": None,
        },
    }


def test_executor_rejects_unapproved_plan(monkeypatch):
    plan = sample_plan()
    plan["status"] = "awaiting_approval"

    with pytest.raises(ValueError):
        executor.execute_plan(plan)


def test_executor_rejects_pending_approval_flag():
    plan = sample_plan()
    plan["requires_approval"] = True

    with pytest.raises(ValueError):
        executor.execute_plan(plan)


def test_executor_rejects_empty_tasks():
    plan = sample_plan()
    plan["tasks"] = []

    with pytest.raises(ValueError):
        executor.execute_plan(plan)


def test_executor_rejects_unknown_agent(monkeypatch):
    plan = sample_plan()
    plan["tasks"][0]["agent"] = "Unknown Agent"

    monkeypatch.setattr(
        executor, "save_plan", lambda *args: None
    )

    with pytest.raises(ValueError, match="Agent tidak terdaftar"):
        executor.execute_plan(plan)

    assert plan["status"] == "failed"


def test_executor_rejects_completed_project():
    plan = sample_plan()
    plan["execution"]["status"] = "completed"

    with pytest.raises(ValueError):
        executor.execute_plan(plan)


def test_executor_success(monkeypatch):
    plan = sample_plan()

    class FakeAgent:
        def run(self, plan, task, context):
            return {"status": "completed"}

    monkeypatch.setattr(
        executor, "save_plan", lambda *args: None
    )
    monkeypatch.setitem(
        executor.AGENT_REGISTRY,
        "Research Agent",
        FakeAgent(),
    )

    result = executor.execute_plan(plan)

    assert result["status"] == "completed"
    assert result["execution"]["status"] == "completed"
    assert result["tasks"][0]["status"] == "completed"


def test_executor_handles_agent_failure(monkeypatch):
    plan = sample_plan()

    class FailingAgent:
        def run(self, plan, task, context):
            raise RuntimeError("Simulated failure")

    monkeypatch.setattr(
        executor, "save_plan", lambda *args: None
    )
    monkeypatch.setitem(
        executor.AGENT_REGISTRY,
        "Research Agent",
        FailingAgent(),
    )

    with pytest.raises(ValueError, match="Eksekusi gagal"):
        executor.execute_plan(plan)

    assert plan["status"] == "failed"
    assert plan["execution"]["status"] == "failed"
    assert plan["tasks"][0]["status"] == "failed"


def test_executor_rejects_running_project():
    plan = sample_plan()
    plan["execution"]["status"] = "running"

    with pytest.raises(
        ValueError,
        match="Project sudah atau sedang dieksekusi"
    ):
        executor.execute_plan(plan)


def test_executor_fails_when_qa_fails(monkeypatch):
    plan = sample_plan()
    plan["tasks"][0]["agent"] = "QA Agent"

    class FailingQAAgent:
        def run(self, plan, task, context):
            return {
                "agent": "QA Agent",
                "status": "completed",
                "passed": False,
                "checks": {},
            }

    monkeypatch.setattr(
        executor,
        "save_plan",
        lambda *args: None
    )
    monkeypatch.setitem(
        executor.AGENT_REGISTRY,
        "QA Agent",
        FailingQAAgent()
    )

    with pytest.raises(ValueError, match="QA gagal"):
        executor.execute_plan(plan)

    assert plan["status"] == "failed"
    assert plan["execution"]["status"] == "failed"


def test_executor_persists_success_to_sqlite(monkeypatch, tmp_path):
    from app.core import memory

    db_path = tmp_path / "executor_test.db"
    monkeypatch.setattr(memory, "DB_PATH", db_path)

    memory.init_db()

    class FakeAgent:
        def run(self, plan, task, context):
            return {"status": "completed", "result": "OK"}

    monkeypatch.setitem(
        executor.AGENT_REGISTRY,
        "Research Agent",
        FakeAgent()
    )

    plan = sample_plan()
    plan["instruction"] = "Test SQLite persistence"
    result = executor.execute_plan(plan)

    saved_plan = memory.get_plan("executor-test-001")
    events = memory.get_project_events("executor-test-001")

    assert result["status"] == "completed"
    assert saved_plan["status"] == "completed"
    assert saved_plan["execution"]["status"] == "completed"
    assert len(events) >= 1


def test_executor_persists_qa_failure_to_sqlite(monkeypatch, tmp_path):
    from app.core import memory

    db_path = tmp_path / "executor_failure_test.db"
    monkeypatch.setattr(memory, "DB_PATH", db_path)
    memory.init_db()

    class FailingQAAgent:
        def run(self, plan, task, context):
            return {
                "agent": "QA Agent",
                "status": "completed",
                "passed": False,
                "checks": {},
            }

    monkeypatch.setitem(
        executor.AGENT_REGISTRY,
        "QA Agent",
        FailingQAAgent()
    )

    plan = sample_plan()
    plan["instruction"] = "Test QA failure persistence"
    plan["tasks"][0]["agent"] = "QA Agent"

    with pytest.raises(ValueError, match="QA gagal"):
        executor.execute_plan(plan)

    saved_plan = memory.get_plan("executor-test-001")
    events = memory.get_project_events("executor-test-001")

    assert saved_plan["status"] == "failed"
    assert saved_plan["execution"]["status"] == "failed"
    assert saved_plan["execution"]["error"] == "QA gagal"
    assert len(events) >= 1
