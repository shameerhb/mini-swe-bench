import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

tasks = [
    ("discount-001", "Discount validation"),
    ("username-001", "Username validation"),
]

results = []

for task_id, name in tasks:
    files = sorted(
        REPORTS.glob(f"{task_id}_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not files:
        results.append({
            "task_id": task_id,
            "name": name,
            "status": "missing",
            "reward": 0.0,
        })
        continue

    report = json.loads(files[0].read_text(encoding="utf-8"))
    reward_data = report.get("reward", {})

    results.append({
        "task_id": task_id,
        "name": name,
        "status": report.get("overall_status", "unknown"),
        "reward": float(reward_data.get("reward", 0)),
    })

total = len(results)
solved = sum(r["status"] == "passed" for r in results)
average = sum(r["reward"] for r in results) / total if total else 0

summary = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "total_tasks": total,
    "tasks_solved": solved,
    "success_rate": round(solved / total * 100, 2) if total else 0,
    "average_reward": round(average, 2),
    "tasks": results,
}

REPORTS.mkdir(exist_ok=True)

(REPORTS / "benchmark_summary.json").write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8",
)

lines = [
    "# Mini SWE-bench — Benchmark Summary",
    "",
    f"Generated: {summary['generated_at']}",
    "",
    "## Overall Results",
    "",
    f"- Tasks evaluated: {total}",
    f"- Tasks solved: {solved}",
    f"- Success rate: {summary['success_rate']}%",
    f"- Average reward: {average:.1f}/100",
    "",
    "## Task Results",
    "",
    "| Task | Status | Reward |",
    "|---|---|---:|",
]

for result in results:
    lines.append(
        f"| {result['name']} | {result['status']} | "
        f"{result['reward']:.1f}/100 |"
    )

(REPORTS / "benchmark_summary.md").write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)

print("Aggregate benchmark reports generated.")
print(f"Tasks solved: {solved}/{total}")
print(f"Average reward: {average:.1f}/100")
print("Created: reports/benchmark_summary.json")
print("Created: reports/benchmark_summary.md")
