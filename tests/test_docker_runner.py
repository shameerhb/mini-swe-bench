from unittest.mock import patch, MagicMock

from mini_swe_bench.runner import EvaluationRunner


def test_docker_command_uses_security_restrictions(tmp_path):
    runner = EvaluationRunner(use_docker=True)
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "3 passed"
    mock_result.stderr = ""

    with patch("mini_swe_bench.runner.subprocess.run", return_value=mock_result) as mocked:
        result = runner.run_command("python -m pytest -q", tmp_path)

    command = mocked.call_args.args[0]

    assert command[0:2] == ["docker", "run"]
    assert "--network" in command
    assert "none" in command
    assert "--memory" in command
    assert "512m" in command
    assert "--cpus" in command
    assert "--cap-drop" in command
    assert "--read-only" in command
    assert result["status"] == "passed"
    assert result["execution"] == "docker"


def test_docker_command_reports_failure(tmp_path):
    runner = EvaluationRunner(use_docker=True)
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "1 failed"

    with patch("mini_swe_bench.runner.subprocess.run", return_value=mock_result):
        result = runner.run_command("python -m pytest -q", tmp_path)

    assert result["status"] == "failed"
    assert result["returncode"] == 1
    assert result["stderr"] == "1 failed"


def test_docker_command_reports_timeout(tmp_path):
    import subprocess

    runner = EvaluationRunner(use_docker=True)

    with patch(
        "mini_swe_bench.runner.subprocess.run",
        side_effect=subprocess.TimeoutExpired("docker run", 120),
    ):
        result = runner.run_command("python -m pytest -q", tmp_path)

    assert result["status"] == "timeout"
    assert result["returncode"] is None


def test_docker_command_reports_missing_docker(tmp_path):
    runner = EvaluationRunner(use_docker=True)

    with patch(
        "mini_swe_bench.runner.subprocess.run",
        side_effect=FileNotFoundError("docker not found"),
    ):
        result = runner.run_command("python -m pytest -q", tmp_path)

    assert result["status"] == "error"
    assert "docker not found" in result["stderr"]
