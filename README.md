Mini SWE-bench

A lightweight repository-level patch evaluation harness inspired by SWE-bench.

## Features
- Load evaluation tasks from JSON files.
- Apply candidate patches using Git.
- Run fail-to-pass and pass-to-pass tests.
- Enforce execution timeouts.
- Generate JSON and Markdown reports.
- Provide a command-line interface.

## Setup

Run: pip install -e .

## Tests

Run: pytest -q

## Limitations

This MVP has no LLM integration or Docker sandbox. It does not automatically check out the task base commit. Commands execute locally.
