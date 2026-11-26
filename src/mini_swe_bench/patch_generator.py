from pathlib import Path
import json
import shutil
import subprocess
import tempfile
import urllib.request
import urllib.error
import difflib


class PatchGenerator:
    def __init__(
        self,
        model="qwen2.5-coder:7b",
        ollama_url="http://localhost:11434/api/generate",
    ):
        self.model = model
        self.ollama_url = ollama_url

    def collect_source(self, repo_path):
        repo_path = Path(repo_path).resolve()
        source_root = repo_path / "src"

        if not source_root.is_dir():
            source_root = repo_path

        excluded = {
            ".git", ".venv", "venv", "__pycache__", "node_modules",
            ".pytest_cache", ".mypy_cache", "dist", "build",
        }

        sources = {}

        for path in source_root.rglob("*.py"):
            if any(part in excluded for part in path.parts):
                continue
            if "tests" in path.parts or path.name.startswith("test_"):
                continue

            try:
                relative = path.relative_to(repo_path).as_posix()
                sources[relative] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

        if not sources:
            raise ValueError("No eligible Python source files found.")

        return sources

    def _request_model(self, prompt):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        }

        request = urllib.request.Request(
            self.ollama_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(
                "Could not connect to Ollama. Make sure Ollama is running."
            ) from exc

        return result.get("response", "").strip()

    def _clean_output(self, output):
        output = output.strip()

        if output.startswith("```"):
            lines = output.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            output = "\n".join(lines).strip()

        return output

    def _build_patch(self, relative, original, updated):
        original_lines = original.splitlines()
        updated_lines = updated.splitlines()

        if original_lines == updated_lines:
            raise ValueError("AI returned unchanged source; no fix was generated.")

        diff = list(difflib.unified_diff(
            original_lines,
            updated_lines,
            fromfile=f"a/{relative}",
            tofile=f"b/{relative}",
            lineterm="",
        ))

        if not diff:
            raise ValueError("Could not construct a patch.")

        return "\n".join(diff) + "\n"

    def _validate_patch(self, repo_path, patch):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_repo = Path(temp_dir) / "repo"
            shutil.copytree(repo_path, test_repo)

            result = subprocess.run(
                ["git", "apply", "--check", "-"],
                cwd=test_repo,
                input=patch,
                capture_output=True,
                text=True,
            )

            return result.returncode == 0, result.stderr.strip()

    def generate(self, task, repo_path, output_path):
        repo_path = Path(repo_path).resolve()
        sources = self.collect_source(repo_path)

        # This fixture currently has a single application source file.
        if len(sources) != 1:
            raise ValueError(
                "Current AI generator expects exactly one eligible source file."
            )

        relative, original = next(iter(sources.items()))

        prompt = f"""
You are an expert Python engineer fixing a software issue.

ISSUE:
{task.issue}

FILE PATH:
{relative}

EXACT ORIGINAL FILE CONTENT:
{original}

Instructions:
- Fix the issue with the smallest necessary change.
- Preserve existing functionality.
- Do not change unrelated code.
- Do not modify tests.
- Return the COMPLETE corrected Python file.
- Do not return a diff.
- Do not include explanations or markdown fences.
"""

        print("Requesting corrected source from local AI model...")
        updated = self._clean_output(self._request_model(prompt))

        if not updated:
            raise ValueError("AI returned an empty source file.")

        # Generate a structurally correct diff ourselves.
        patch = self._build_patch(relative, original, updated)

        valid, error = self._validate_patch(repo_path, patch)

        if not valid:
            raise ValueError(f"Generated patch failed validation:\n{error}")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(patch.encode('utf-8'))

        print("Patch generated and validated successfully.")
        return output_path
