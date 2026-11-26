from pathlib import Path
import difflib

source = Path("examples/discount-bug/src/pricing.py")
patch = Path("examples/discount-bug/solution.patch")

original = source.read_text(encoding="utf-8")
fixed = '''def apply_discount(price: float, discount: float) -> float:
    if price < 0:
        raise ValueError("Price cannot be negative")
    if not 0 <= discount <= 100:
        raise ValueError("Discount must be between 0 and 100")

    return price - (price * discount / 100)
'''

diff = difflib.unified_diff(
    original.splitlines(keepends=True),
    fixed.splitlines(keepends=True),
    fromfile="a/src/pricing.py",
    tofile="b/src/pricing.py",
)

patch.write_text("".join(diff), encoding="utf-8", newline="\n")
print("Discount patch regenerated successfully.")
