import subprocess
from pathlib import Path
from typing import Any


class EvaluationRunner:
    def __init__(self, timeout: int = 120):
        self.timeout = timeout

    def run_command(self, command: str, repo_path: str | Path) -> dict[str, Any]:
        try:
            result = subprocess.run(
                command,
                cwd=repo_path,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            return {
                "command": command,
                "status": "passed" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired as exc:
            return {
                "command": command,
                "status": "timeout",
                "returncode": None,
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
            }

        except OSError as exc:
            return {
                "command": command,
                "status": "error",
                "returncode": None,
                "stdout": "",
                "stderr": str(exc),
            }

    def evaluate(
        self,
        task,
        repo_path: str | Path,
        patch_path: str | Path | None = None,
    ) -> dict[str, Any]:
        repo_path = Path(repo_path).resolve()

        if not repo_path.is_dir():
            raise NotADirectoryError(f"Repository directory not found: {repo_path}")

        patch_result = None

        if patch_path is not None:
            patch_path = Path(patch_path).resolve()

            if not patch_path.is_file():
                raise FileNotFoundError(f"Patch file not found: {patch_path}")

            check = subprocess.run(
                ["git", "apply", "--check", str(patch_path)],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )

            if check.returncode != 0:
                return {
                    "task_id": task.task_id,
                    "overall_status": "patch_rejected",
                    "patch_error": check.stderr,
                    "fail_to_pass": [],
                    "pass_to_pass": [],
                }

            applied = subprocess.run(
                ["git", "apply", str(patch_path)],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )

            if applied.returncode != 0:
                return {
                    "task_id": task.task_id,
                    "overall_status": "patch_error",
                    "patch_error": applied.stderr,
                    "fail_to_pass": [],
                    "pass_to_pass": [],
                }

            patch_result = "applied"

        fail_to_pass = [
            self.run_command(command, repo_path)
            for command in task.fail_to_pass
        ]

        pass_to_pass = [
            self.run_command(command, repo_path)
            for command in task.pass_to_pass
        ]

        all_results = fail_to_pass + pass_to_pass
        success = bool(all_results) and all(
            result["status"] == "passed" for result in all_results
        )

        return {
            "task_id": task.task_id,
            "overall_status": "passed" if success else "failed",
            "patch_status": patch_result,
            "fail_to_pass": fail_to_pass,
            "pass_to_pass": pass_to_pass,
        }
