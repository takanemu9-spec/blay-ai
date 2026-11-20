from uuid import uuid4
from datetime import datetime, timezone

from app.core.memory import save_plan, get_plan as memory_get_plan


def create_plan(prompt: str):
    if not prompt or not prompt.strip():
        raise ValueError("Instruksi tidak boleh kosong")

    project_id = str(uuid4())

    plan = {
        "project_id": project_id,
        "director": "BLAY Director",
        "instruction": prompt.strip(),
        "status": "awaiting_approval",
        "requires_approval": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "approval": {
            "status": "pending",
            "decided_at": None
        },
        "tasks": [
            {
                "agent": "Research Agent",
                "task": "Menganalisis kebutuhan dan mengumpulkan informasi proyek",
                "status": "pending",
                "result": None
            },
            {
                "agent": "Tech Agent",
                "task": "Menyusun solusi dan rancangan teknis berdasarkan hasil riset",
                "status": "pending",
                "result": None
            },
            {
                "agent": "QA Agent",
                "task": "Memeriksa kualitas dan kelengkapan hasil pekerjaan",
                "status": "pending",
                "result": None
            }
        ]
    }

    save_plan(plan, "project_created")
    return plan


def get_plan(project_id: str):
    return memory_get_plan(project_id)


def approve_plan(project_id: str):
    plan = get_plan(project_id)

    if plan is None:
        raise ValueError("Project tidak ditemukan")

    if plan["status"] != "awaiting_approval":
        raise ValueError("Project tidak sedang menunggu persetujuan")

    now = datetime.now(timezone.utc).isoformat()

    plan["status"] = "approved"
    plan["requires_approval"] = False
    plan["approval"] = {
        "status": "approved",
        "decided_at": now
    }

    save_plan(plan, "project_approved")
    return plan


def reject_plan(project_id: str):
    plan = get_plan(project_id)

    if plan is None:
        raise ValueError("Project tidak ditemukan")

    if plan["status"] != "awaiting_approval":
        raise ValueError("Project tidak sedang menunggu persetujuan")

    now = datetime.now(timezone.utc).isoformat()

    plan["status"] = "rejected"
    plan["requires_approval"] = False
    plan["approval"] = {
        "status": "rejected",
        "decided_at": now
    }

    save_plan(plan, "project_rejected")
    return plan
