from pathlib import Path


def build_agent_payload(task, workspace_path: str | Path) -> dict:
    workspace = Path(workspace_path).resolve()

    if not workspace.is_dir():
        raise NotADirectoryError(
            f"Agent workspace not found: {workspace}"
        )

    return {
        "task_id": task.task_id,
        "issue": task.issue,
        "workspace": str(workspace),
        "instructions": (
            "Inspect the repository, investigate the reported issue, "
            "implement a suitable fix, and verify your changes with tests. "
            "Do not modify files outside the assigned workspace."
        ),
    }
