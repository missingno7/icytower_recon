"""Track assignment and SSA PHI order for the exact-neighbor regression."""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[3]
base = root / "build/tu-context/game-fld-adspot"
folders = {
    "baseline": base / "research-20260924-http-response-baseline-all-tree-passes",
    "comments": base / "research-20260924-http-response-comments-all-tree-passes",
}
pattern = re.compile(r"fld_adspot\.c\.(\d+)t\.(.+)$")
names = sorted(
    set(p.name for p in folders["baseline"].iterdir() if pattern.fullmatch(p.name))
    & set(p.name for p in folders["comments"].iterdir() if pattern.fullmatch(p.name)),
    key=lambda n: int(pattern.fullmatch(n).group(1)),
)

def order(body, first, second):
    a = re.search(first, body, re.M)
    b = re.search(second, body, re.M)
    if not (a and b):
        return None
    return "i_before_f" if a.start() < b.start() else "f_before_i"

rows = []
for name in names:
    row = {"pass": name}
    for tag, directory in folders.items():
        text = (directory / name).read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^fldads_get_random_ad \(\)\s*\{", text, re.M)
        if not m:
            row[tag] = {"function_present": False}
            continue
        end = re.search(r"^\}", text[m.end():], re.M)
        body = text[m.start():m.end() + end.end()] if end else text[m.start():]
        row[tag] = {
            "function_present": True,
            "assignment_order": order(
                body,
                r"^\s*i(?:_\d+)?\s*=\s*0;",
                r"^\s*fCumulativeProbability(?:_\d+)?\s*=\s*0\.0;",
            ),
            "phi_order": order(
                body,
                r"^\s*#\s*i_\d+\s*=\s*PHI",
                r"^\s*#\s*fCumulativeProbability_\d+\s*=\s*PHI",
            ),
        }
    rows.append(row)

out = Path(__file__).resolve().parent / "tree-init-order.json"
out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
for dimension in ("assignment_order", "phi_order"):
    first = next(
        (row for row in rows
         if row["baseline"].get(dimension) is not None
         and row["comments"].get(dimension) is not None
         and row["baseline"][dimension] != row["comments"][dimension]),
        None,
    )
    print(dimension, "first tracked difference:", first)
print("common pass dumps:", len(rows))
