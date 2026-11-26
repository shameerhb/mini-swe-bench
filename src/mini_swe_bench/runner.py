import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class EvaluationRunner:
    def __init__(
        self,
        timeout: int = 120,
        use_docker: bool = False,
        docker_image: str = "mini-swe-bench-runner:latest",
    ):
        self.timeout = timeout
        self.use_docker = use_docker
        self.docker_image = docker_image

    def run_command(self, command: str, repo_path: str | Path) -> dict[str, Any]:
        if self.use_docker:
            return self._run_docker_command(command, repo_path)

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

    def _run_docker_command(
        self, command: str, repo_path: str | Path
    ) -> dict[str, Any]:
        workspace = str(Path(repo_path).resolve())

        docker_command = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "512m",
            "--cpus", "1",
            "--pids-limit", "128",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--read-only",
            "--tmpfs", "/tmp:rw,nosuid,nodev,size=64m",
            "--mount", f"type=bind,source={workspace},target=/workspace",
            "--workdir", "/workspace",
            self.docker_image,
            "sh", "-lc", command,
        ]

        try:
            result = subprocess.run(
                docker_command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            return {
                "command": command,
                "execution": "docker",
                "status": "passed" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "command": command,
                "execution": "docker",
                "status": "timeout",
                "returncode": None,
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
            }
        except OSError as exc:
            return {
                "command": command,
                "execution": "docker",
                "status": "error",
                "returncode": None,
                "stdout": "",
                "stderr": str(exc),
            }

    def evaluate(self, task, repo_path, patch_path=None) -> dict[str, Any]:
        repo_path = Path(repo_path).resolve()

        if not repo_path.is_dir():
            raise NotADirectoryError(
                f"Repository directory not found: {repo_path}"
            )

        patch_file = None
        if patch_path is not None:
            patch_file = Path(patch_path).resolve()
            if not patch_file.is_file():
                raise FileNotFoundError(
                    f"Patch file not found: {patch_file}"
                )

        with tempfile.TemporaryDirectory(prefix="mini-swe-bench-") as temp:
            workspace = Path(temp) / "repository"
            shutil.copytree(repo_path, workspace)

            base_commit = getattr(task, "base_commit", None)

            if base_commit and (workspace / ".git").exists():
                checkout = subprocess.run(
                    ["git", "checkout", "--detach", base_commit],
                    cwd=workspace,
                    capture_output=True,
                    text=True,
                )
                if checkout.returncode != 0:
                    raise RuntimeError(
                        f"Could not checkout base commit: {checkout.stderr}"
                    )

            patch_status = None

            if patch_file is not None:
                check = subprocess.run(
                    ["git", "apply", "--check", str(patch_file)],
                    cwd=workspace,
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
                    ["git", "apply", str(patch_file)],
                    cwd=workspace,
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

                patch_status = "applied"

            fail_to_pass = [
                self.run_command(command, workspace)
                for command in task.fail_to_pass
            ]
            pass_to_pass = [
                self.run_command(command, workspace)
                for command in task.pass_to_pass
            ]

            all_results = fail_to_pass + pass_to_pass
            success = bool(all_results) and all(
                result["status"] == "passed" for result in all_results
            )

            return {
                "task_id": task.task_id,
                "overall_status": "passed" if success else "failed",
                "patch_status": patch_status,
                "execution_mode": "docker" if self.use_docker else "host",
                "fail_to_pass": fail_to_pass,
                "pass_to_pass": pass_to_pass,
            }
