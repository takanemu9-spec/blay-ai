from app.agents.base import BaseAgent


class ResearchAgent(BaseAgent):
    name = "Research Agent"

    def run(self, plan, task, context):
        instruction = plan.get("instruction", "").strip()

        return {
            "agent": self.name,
            "status": "completed",
            "objective": instruction,
            "task": task.get("task"),
            "findings": [
                "Instruksi berhasil dibaca.",
                "Ruang lingkup awal berhasil disusun.",
                "Riset eksternal belum diaktifkan."
            ]
        }
