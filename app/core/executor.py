from datetime import datetime, timezone

from app.agents.research_agent import ResearchAgent
from app.agents.tech_agent import TechAgent
from app.agents.qa_agent import QAAgent
from app.core.memory import save_plan


AGENT_REGISTRY = {
    "Research Agent": ResearchAgent(),
    "Tech Agent": TechAgent(),
    "QA Agent": QAAgent()
}


def now():
    return datetime.now(timezone.utc).isoformat()


def execute_plan(plan: dict) -> dict:
    if not plan:
        raise ValueError("Project tidak ditemukan")

    if plan.get("status") != "approved":
        raise ValueError("Project harus disetujui sebelum dieksekusi")

    if plan.get("requires_approval", True):
        raise ValueError("Approval belum diselesaikan")

    tasks = plan.get("tasks", [])

    if not tasks:
        raise ValueError("Tidak ada tugas untuk dieksekusi")

    if plan.get("execution", {}).get("status") in (
        "running", "completed"
    ):
        raise ValueError("Project sudah atau sedang dieksekusi")

    plan["status"] = "executing"
    plan["execution"] = {
        "status": "running",
        "started_at": now(),
        "completed_at": None,
        "error": None
    }

    save_plan(plan, "execution_started")

    context = {}

    try:
        for task in tasks:
            agent_name = task.get("agent")
            agent = AGENT_REGISTRY.get(agent_name)

            if agent is None:
                raise ValueError(
                    f"Agent tidak terdaftar: {agent_name}"
                )

            task["status"] = "running"
            task["started_at"] = now()

            save_plan(
                plan,
                "agent_started",
                {"agent": agent_name}
            )

            result = agent.run(plan, task, context)

            task["result"] = result
            task["completed_at"] = now()
            task["status"] = result["status"]

            context[agent_name] = result

            save_plan(
                plan,
                "agent_completed",
                {
                    "agent": agent_name,
                    "status": result["status"]
                }
            )

            if result["status"] != "completed":
                raise ValueError(
                    f"{agent_name} membutuhkan pemeriksaan"
                )

            if agent_name == "QA Agent":
                if not result.get("passed"):
                    raise ValueError("QA gagal")

        plan["status"] = "completed"
        plan["execution"]["status"] = "completed"
        plan["execution"]["completed_at"] = now()

        save_plan(plan, "execution_completed")
        return plan

    except Exception as error:
        plan["status"] = "failed"
        plan["execution"]["status"] = "failed"
        plan["execution"]["completed_at"] = now()
        plan["execution"]["error"] = str(error)

        for task in tasks:
            if task.get("status") == "running":
                task["status"] = "failed"

        save_plan(
            plan,
            "execution_failed",
            {"error": str(error)}
        )

        raise ValueError(
            f"Eksekusi gagal: {error}"
        ) from error
