from pathlib import Path

path = Path("scripts/run_examples.py")
source = path.read_text(encoding="utf-8-sig")

old = '''if completed != len(results):
    sys.exit(1)
'''

new = '''summary_command = [
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
'''

if old not in source:
    raise SystemExit("Expected insertion point not found. No changes made.")

path.write_text(source.replace(old, new), encoding="utf-8")
print("Batch runner updated to generate aggregate reports.")
