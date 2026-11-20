from app.agents.base import BaseAgent


class QAAgent(BaseAgent):
    name = "QA Agent"

    def run(self, plan, task, context):
        research = context.get("Research Agent")
        technical = context.get("Tech Agent")

        checks = {
            "instruction_available": bool(plan.get("instruction")),
            "research_available": bool(research),
            "technical_available": bool(technical)
        }

        passed = all(checks.values())

        return {
            "agent": self.name,
            "status": "completed" if passed else "needs_review",
            "task": task.get("task"),
            "checks": checks,
            "passed": passed
        }
