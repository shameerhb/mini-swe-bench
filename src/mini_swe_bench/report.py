import json
from pathlib import Path
from datetime import datetime, timezone


def calculate_reward(results: dict) -> dict:
    fail_tests = results.get("fail_to_pass", [])
    pass_tests = results.get("pass_to_pass", [])

    fix_rate = (
        sum(item.get("status") == "passed" for item in fail_tests)
        / len(fail_tests)
        if fail_tests else 0.0
    )

    regression_rate = (
        sum(item.get("status") == "passed" for item in pass_tests)
        / len(pass_tests)
        if pass_tests else 1.0
    )

    reward = 100 * (
        0.70 * fix_rate + 0.30 * regression_rate
    )

    return {
        "reward": round(reward, 2),
        "fix_rate": round(fix_rate, 4),
        "regression_rate": round(regression_rate, 4),
        "max_reward": 100,
    }


def generate_report(
    results: dict,
    output_dir: str | Path = "reports",
) -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    task_id = results.get("task_id", "unknown")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    json_path = output_dir / f"{task_id}_{timestamp}.json"
    markdown_path = output_dir / f"{task_id}_{timestamp}.md"

    reward = calculate_reward(results)

    report = {
        **results,
        "reward": reward,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    json_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    lines = [
        f"# Evaluation Report: {task_id}",
        "",
        f"**Overall status:** {results.get('overall_status', 'unknown')}",
        f"**Reward:** {reward['reward']}/100",
        f"**Fix rate:** {reward['fix_rate'] * 100:.1f}%",
        f"**Regression rate:** {reward['regression_rate'] * 100:.1f}%",
        "",
    ]

    for section in ("fail_to_pass", "pass_to_pass"):
        lines.extend([
            f"## {section.replace('_', ' ').title()}",
            "",
        ])

        for item in results.get(section, []):
            lines.extend([
                f"- **Status:** {item.get('status', 'unknown')}",
                f"  - Command: `{item.get('command', '')}`",
                f"  - Return code: {item.get('returncode')}",
            ])

        if not results.get(section):
            lines.append("No tests configured.")

        lines.append("")

    markdown_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, markdown_path
