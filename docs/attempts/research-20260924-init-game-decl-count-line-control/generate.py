"""Build a line- and byte-position-preserving prototype-count control."""

from hashlib import sha256
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
source = (ROOT / "src/main.c").read_bytes()
lines = source.splitlines(keepends=True)
marker = b"/* Forward declarations; definitions follow in their original source order. */"
starts = [i for i, line in enumerate(lines) if line.rstrip(b"\r\n") == marker]
if len(starts) != 16:
    raise SystemExit(f"expected 16 prototype blocks, found {len(starts)}")

variant = list(lines)
blanked = 0
for block in range(1, 15):
    for i in range(starts[block] + 1, starts[block + 1]):
        line = lines[i]
        body = line.rstrip(b"\r\n")
        if not body.strip().endswith(b";"):
            continue
        variant[i] = b" " * len(body) + line[len(body):]
        blanked += 1
if blanked != 14 * 81:
    raise SystemExit(f"expected 1134 blanked prototypes, found {blanked}")

changed = b"".join(variant)
assert len(source) == len(changed)
assert len(source.splitlines()) == len(changed.splitlines())
(HERE / "control.c").write_bytes(source)
(HERE / "blanked.c").write_bytes(changed)
(HERE / "inputs.json").write_text(
    json.dumps({
        "source_sha256": sha256(source).hexdigest(),
        "control_sha256": sha256(source).hexdigest(),
        "blanked_sha256": sha256(changed).hexdigest(),
        "source_bytes": len(source),
        "source_lines": len(lines),
        "blocks": len(starts),
        "blanked_legacy_blocks": 14,
        "blanked_prototypes": blanked,
        "retained_blocks": ["first legacy", "final historical"],
        "invariant": "All retained tokens keep their byte offsets, lines, and columns.",
    }, indent=2) + "\n",
    encoding="utf-8",
)
