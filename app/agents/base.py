class BaseAgent:
    """Common interface for BLAY agents."""

    name = "Base Agent"

    def run(self, plan: dict, task: dict, context: dict) -> dict:
        raise NotImplementedError("Agent harus mengimplementasikan run()")
