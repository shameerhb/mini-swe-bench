import json

from mini_swe_bench.report import generate_report


def test_generate_json_and_markdown_reports(tmp_path):
    results = {
        "task_id": "example-001",
        "overall_status": "passed",
        "fail_to_pass": [
            {"command": "pytest tests/test_fix.py", "status": "passed", "returncode": 0}
        ],
        "pass_to_pass": [],
    }

    json_path, markdown_path = generate_report(results, tmp_path)

    assert json_path.exists()
    assert markdown_path.exists()
    assert json.loads(json_path.read_text(encoding="utf-8"))["overall_status"] == "passed"
    assert "Evaluation Report: example-001" in markdown_path.read_text(encoding="utf-8")
