from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class EvaluationTask:
    task_id: str
    repo: str
    base_commit: str
    issue: str
    fail_to_pass: list[str] = field(default_factory=list)
    pass_to_pass: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "EvaluationTask":
        required_fields = ["task_id", "repo", "base_commit", "issue"]

        for name in required_fields:
            value = data.get(name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Missing or invalid required field: {name}")

        for name in ["fail_to_pass", "pass_to_pass"]:
            value = data.get(name, [])

            if not isinstance(value, list):
                raise ValueError(f"{name} must be a list")

            if not all(isinstance(item, str) and item.strip() for item in value):
                raise ValueError(f"Every item in {name} must be a non-empty string")

        return cls(
            task_id=data["task_id"],
            repo=data["repo"],
            base_commit=data["base_commit"],
            issue=data["issue"],
            fail_to_pass=data.get("fail_to_pass", []),
            pass_to_pass=data.get("pass_to_pass", []),
        )

    @classmethod
    def load(cls, path: str | Path) -> "EvaluationTask":
        task_path = Path(path)

        with task_path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Task file must contain a JSON object")

        return cls.from_dict(data)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "repo": self.repo,
            "base_commit": self.base_commit,
            "issue": self.issue,
            "fail_to_pass": self.fail_to_pass,
            "pass_to_pass": self.pass_to_pass,
        }

