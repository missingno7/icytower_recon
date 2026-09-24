"""Generate the two new fixed-position declaration-group corners."""

from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE_HASH = "2a12d635e2fbf74bd0388869fd303a6622b9ee31305e110bc7cfaa41d4c05044"
source = (ROOT / "src/main.c").read_bytes()
if sha256(source).hexdigest() != SOURCE_HASH:
    raise SystemExit("current main.c is not the pinned baseline")
lines = source.splitlines(keepends=True)
marker = b"/* Forward declarations; definitions follow in their original source order. */"
starts = [i for i, line in enumerate(lines) if line.rstrip(b"\r\n") == marker]
if len(starts) != 16:
    raise SystemExit(f"expected 16 declaration blocks, got {len(starts)}")

manifest = {"source_sha256": SOURCE_HASH, "source_bytes": len(source), "source_lines": len(lines)}
for name, blocks in {"early": range(1, 8), "late": range(8, 15)}.items():
    changed = list(lines)
    count = 0
    for block in blocks:
        for i in range(starts[block] + 1, starts[block + 1]):
            line = lines[i]
            body = line.rstrip(b"\r\n")
            if body.strip().endswith(b";"):
                changed[i] = b" " * len(body) + line[len(body):]
                count += 1
    if count != 7 * 81:
        raise SystemExit(f"{name}: expected 567 declarations, got {count}")
    output = b"".join(changed)
    if len(output) != len(source) or len(output.splitlines()) != len(lines):
        raise SystemExit(f"{name}: source positions moved")
    (HERE / f"{name}.c").write_bytes(output)
    manifest[name] = {
        "legacy_blocks_blanked_one_based": [i + 1 for i in blocks],
        "prototypes_blanked": count,
        "sha256": sha256(output).hexdigest(),
    }
(HERE / "inputs.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
