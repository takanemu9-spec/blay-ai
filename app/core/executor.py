from datetime import datetime, timezone


def execute_plan(plan: dict) -> dict:
    if not plan:
        raise ValueError("Project tidak ditemukan")

    if plan.get("status") != "approved":
        raise ValueError(
            "Project harus disetujui sebelum dieksekusi"
        )

    if plan.get("requires_approval", True):
        raise ValueError("Approval belum diselesaikan")

    tasks = plan.get("tasks", [])

    if not tasks:
        raise ValueError("Tidak ada tugas untuk dieksekusi")

    if plan.get("execution", {}).get("status") == "queued":
        raise ValueError("Project sudah masuk antrean")

    now = datetime.now(timezone.utc).isoformat()

    plan["status"] = "executing"

    plan["execution"] = {
        "status": "running",
        "started_at": now,
        "completed_at": None
    }

    for task in tasks:
        if task.get("status") == "pending":
            task["status"] = "queued"

    return plan
