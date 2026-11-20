from types import SimpleNamespace

import pytest

from mini_swe_bench.agent import build_agent_payload


def test_build_agent_payload(tmp_path):
    task = SimpleNamespace(
        task_id="agent-001",
        issue="Fix the response parsing bug.",
        fail_to_pass=["pytest tests/test_bug.py"],
        pass_to_pass=["pytest tests/test_existing.py"],
    )

    payload = build_agent_payload(task, tmp_path)

    assert payload["task_id"] == "agent-001"
    assert payload["issue"] == "Fix the response parsing bug."
    assert payload["workspace"] == str(tmp_path.resolve())
    assert "hidden" not in payload


def test_agent_payload_rejects_missing_workspace(tmp_path):
    task = SimpleNamespace(
        task_id="agent-002",
        issue="Fix a bug.",
    )

    with pytest.raises(NotADirectoryError):
        build_agent_payload(task, tmp_path / "missing")
