import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TASKS = [
    ("discount-001", "examples/discount-bug"),
    ("username-001", "examples/username-bug"),
]

env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT / "src")

results = []

for task_id, fixture in TASKS:
    fixture_path = ROOT / fixture
    task_file = fixture_path / "task.json"
    patch_file = fixture_path / "solution.patch"

    print(f"\n{'=' * 60}")
    print(f"Running task: {task_id}")
    print(f"{'=' * 60}")

    command = [
        sys.executable,
        "-m",
        "mini_swe_bench.cli",
        "--task", str(task_file),
        "--repo", str(fixture_path),
        "--patch", str(patch_file),
    ]

    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    report_files = sorted(
        (ROOT / "reports").glob(f"{task_id}_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if result.returncode != 0 or not report_files:
        results.append({
            "task_id": task_id,
            "status": "FAILED",
            "reward": 0.0,
        })
        continue

    try:
        report = json.loads(report_files[0].read_text(encoding="utf-8"))
        status = report.get("overall_status", "unknown")
        reward_data = report.get("reward", {})
        reward = float(reward_data.get("reward", 0))
        passed = status == "passed" and reward > 0
    except (OSError, ValueError, TypeError):
        status = "invalid_report"
        reward = 0.0
        passed = False

    results.append({
        "task_id": task_id,
        "status": "PASSED" if passed else "FAILED",
        "reward": reward,
    })

print("\n" + "=" * 60)
print("BATCH EVALUATION SUMMARY")
print("=" * 60)

for result in results:
    print(
        f"{result['task_id']}: {result['status']} "
        f"| Reward: {result['reward']:.1f}/100"
    )

completed = sum(result["status"] == "PASSED" for result in results)
average = sum(result["reward"] for result in results) / len(results)

print(f"\nTasks solved: {completed}/{len(results)}")
print(f"Average reward: {average:.1f}/100")
print(f"Success rate: {completed / len(results) * 100:.1f}%")

summary_command = [
    sys.executable,
    str(ROOT / "scripts" / "generate_summary.py"),
]

summary_result = subprocess.run(
    summary_command,
    cwd=ROOT,
    env=env,
)

if summary_result.returncode != 0:
    sys.exit(summary_result.returncode)

if completed != len(results):
    sys.exit(1)
