from mini_swe_bench.task import EvaluationTask
from mini_swe_bench.patch_generator import PatchGenerator

task = EvaluationTask.load("examples/username-bug/task.json")

generator = PatchGenerator()
patch_path = generator.generate(
    task=task,
    repo_path="examples/username-bug",
    output_path="generated_patches/username-ai.patch",
)

print(f"\nAI patch saved to: {patch_path}")
print("\n--- GENERATED PATCH ---")
print(patch_path.read_text(encoding="utf-8"))
