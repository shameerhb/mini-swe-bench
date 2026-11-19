import pytest

from mini_swe_bench.task import EvaluationTask


def test_valid_task():
    task = EvaluationTask.from_dict({
        "task_id": "example-001",
        "repo": "psf/requests",
        "base_commit": "abc123",
        "issue": "Fix response line iteration",
        "fail_to_pass": ["tests/test_requests.py"],
        "pass_to_pass": ["tests/test_models.py"],
    })

    assert task.task_id == "example-001"
    assert task.fail_to_pass == ["tests/test_requests.py"]


def test_missing_required_field():
    with pytest.raises(ValueError, match="task_id"):
        EvaluationTask.from_dict({
            "repo": "psf/requests",
            "base_commit": "abc123",
            "issue": "Example issue",
        })


def test_test_commands_must_be_lists():
    with pytest.raises(ValueError, match="fail_to_pass must be a list"):
        EvaluationTask.from_dict({
            "task_id": "example-001",
            "repo": "psf/requests",
            "base_commit": "abc123",
            "issue": "Example issue",
            "fail_to_pass": "not-a-list",
        })


def test_empty_test_command_is_rejected():
    with pytest.raises(ValueError, match="non-empty string"):
        EvaluationTask.from_dict({
            "task_id": "example-001",
            "repo": "psf/requests",
            "base_commit": "abc123",
            "issue": "Example issue",
            "fail_to_pass": [""],
        })


def test_to_dict():
    task = EvaluationTask(
        task_id="example-001",
        repo="psf/requests",
        base_commit="abc123",
        issue="Example issue",
    )

    assert task.to_dict()["task_id"] == "example-001"
    assert task.to_dict()["pass_to_pass"] == []
