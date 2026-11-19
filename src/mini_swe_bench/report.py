import json
from pathlib import Path
from datetime import datetime, timezone


def generate_report(results: dict, output_dir: str | Path = "reports") -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    task_id = results.get("task_id", "unknown")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    json_path = output_dir / f"{task_id}_{timestamp}.json"
    markdown_path = output_dir / f"{task_id}_{timestamp}.md"

    report = {
        **results,
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
        "",
    ]

    for section in ("fail_to_pass", "pass_to_pass"):
        lines.extend([f"## {section.replace('_', ' ').title()}", ""])

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
