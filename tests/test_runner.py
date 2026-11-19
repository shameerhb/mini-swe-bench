import sys
from types import SimpleNamespace

import pytest

from mini_swe_bench.runner import EvaluationRunner


def test_command_passes(tmp_path):
    runner = EvaluationRunner()
    command = f'"{sys.executable}" -c "print(1 + 1)"'

    result = runner.run_command(command, tmp_path)

    assert result["status"] == "passed"
    assert "2" in result["stdout"]


def test_command_fails(tmp_path):
    runner = EvaluationRunner()
    command = f'"{sys.executable}" -c "raise SystemExit(1)"'

    result = runner.run_command(command, tmp_path)

    assert result["status"] == "failed"
    assert result["returncode"] == 1


def test_command_times_out(tmp_path):
    runner = EvaluationRunner(timeout=1)
    command = f'"{sys.executable}" -c "import time; time.sleep(3)"'

    result = runner.run_command(command, tmp_path)

    assert result["status"] == "timeout"


def test_evaluate_task(tmp_path):
    task = SimpleNamespace(
        task_id="test-001",
        fail_to_pass=[f'"{sys.executable}" -c "print(1)"'],
        pass_to_pass=[f'"{sys.executable}" -c "print(2)"'],
    )

    result = EvaluationRunner().evaluate(task, tmp_path)

    assert result["overall_status"] == "passed"
    assert result["fail_to_pass"][0]["status"] == "passed"
    assert result["pass_to_pass"][0]["status"] == "passed"


def test_invalid_repository_path():
    task = SimpleNamespace(
        task_id="test-002",
        fail_to_pass=[],
        pass_to_pass=[],
    )

    with pytest.raises(NotADirectoryError):
        EvaluationRunner().evaluate(task, "missing-repository")
