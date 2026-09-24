from pathlib import Path
import hashlib
import json
root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
source = (root / "src/fld_adspot.c").read_bytes()
newline = b"\r\n" if b"\r\n" in source else b"\n"
old = newline.join([
    b"typedef struct HTTPResponse {",
    b"    int iStatusCode;",
    b"    unsigned int iNumHeaders;",
    b"    HTTPHeader *pHeaders;",
    b"    unsigned char *pPayload;",
    b"    unsigned int iPayloadSize;",
    b"} HTTPResponse;",
])
assert source.count(old) == 1
replacement = b'#include "recovered/HTTPResponse.h"' + newline * 6
variant = source.replace(old, replacement, 1)
assert variant.count(newline) == source.count(newline)
comment_replacement = b'#include "recovered/HTTPResponse.h"' + newline + newline.join(
    [b"/* position control */"] * 6
)
comment_variant = source.replace(old, comment_replacement, 1)
assert comment_variant.count(newline) == source.count(newline)
variants = (
    ("baseline.c", source),
    ("position-preserved.c", variant),
    ("position-comments.c", comment_variant),
)
for name, body in variants:
    (out / name).write_bytes(body)
(out / "identities.json").write_text(json.dumps({
    name: {"sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}
    for name, body in variants
}, indent=2) + "\n")
