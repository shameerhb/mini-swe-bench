import argparse
import json

from mini_swe_bench.task import EvaluationTask
from mini_swe_bench.runner import EvaluationRunner
from mini_swe_bench.report import generate_report, calculate_reward


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate code patches against repository tests."
    )
    parser.add_argument("--task", required=True, help="Path to task JSON file")
    parser.add_argument("--repo", required=True, help="Path to local Git repository")
    parser.add_argument("--patch", help="Path to candidate .patch file")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--output", default="reports")
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Run test commands inside the restricted Docker container",
    )

    args = parser.parse_args()

    task = EvaluationTask.load(args.task)
    runner = EvaluationRunner(timeout=args.timeout, use_docker=args.docker)
    results = runner.evaluate(task, args.repo, args.patch)

    json_path, markdown_path = generate_report(results, args.output)

    reward = calculate_reward(results)
    print(json.dumps({**results, "reward": reward}, indent=2))
    print(f"\nJSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")


if __name__ == "__main__":
    main()
