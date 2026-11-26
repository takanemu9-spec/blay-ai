from app.agents.qa_agent import QAAgent


def test_qa_agent_rejects_incomplete_checks():
    agent = QAAgent()

    result = agent.run(
        plan={},
        task={"task": "Quality check"},
        context={}
    )

    assert result["status"] == "needs_review"
    assert result["passed"] is False
    assert result["checks"]["instruction_available"] is False
    assert result["checks"]["research_available"] is False
    assert result["checks"]["technical_available"] is False


def test_qa_agent_passes_complete_checks():
    agent = QAAgent()

    result = agent.run(
        plan={"instruction": "Analyze the project"},
        task={"task": "Quality check"},
        context={
            "Research Agent": {"findings": "Research complete"},
            "Tech Agent": {"analysis": "Technical review complete"},
        },
    )

    assert result["status"] == "completed"
    assert result["passed"] is True


def test_qa_agent_rejects_missing_research():
    agent = QAAgent()

    result = agent.run(
        plan={"instruction": "Analyze project"},
        task={"task": "Quality check"},
        context={
            "Research Agent": None,
            "Tech Agent": {"analysis": "Technical review complete"},
        },
    )

    assert result["status"] == "needs_review"
    assert result["passed"] is False
    assert result["checks"]["research_available"] is False


def test_qa_agent_rejects_missing_instruction():
    agent = QAAgent()

    result = agent.run(
        plan={},
        task={"task": "Quality check"},
        context={
            "Research Agent": {"findings": "Research complete"},
            "Tech Agent": {"analysis": "Technical review complete"},
        },
    )

    assert result["status"] == "needs_review"
    assert result["passed"] is False
    assert result["checks"]["instruction_available"] is False
