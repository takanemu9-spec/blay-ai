from app.agents.base import BaseAgent


class TechAgent(BaseAgent):
    name = "Tech Agent"

    def run(self, plan, task, context):
        research = context.get("Research Agent", {})

        return {
            "agent": self.name,
            "status": "completed",
            "task": task.get("task"),
            "based_on": research.get("findings", []),
            "implementation_steps": [
                "Analisis kebutuhan proyek.",
                "Susun solusi teknis.",
                "Tentukan urutan implementasi.",
                "Siapkan kriteria pemeriksaan."
            ]
        }
