"""Stage metadata from an external forged tree as evidence, never source input."""
import argparse
import hashlib
import re
from pathlib import Path

from common import ROOT, write_json

PROMOTION = re.compile(r'\|\s*\x60([A-Za-z_][A-Za-z0-9_]*)\x60\s*\|[^\n]*?\|\s*([A-Za-z0-9_-]+\.c)\s*\|')


def digest(path):
    data = path.read_bytes()
    return {'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True, help='External evidence root; never copied into src/.')
    ap.add_argument('--output', type=Path, default=ROOT / 'build/forged-evidence.json')
    a = ap.parse_args()
    root = a.root.resolve()
    if root == ROOT.resolve() or ROOT.resolve() in root.parents:
        raise ValueError('Forged evidence root must be outside this reconstruction')
    if not root.is_dir():
        raise ValueError('Missing forged evidence root: ' + str(root))
    files = []
    unreadable = []
    functions = []
    for path in sorted(root.rglob('*.c')):
        rel = path.relative_to(root).as_posix()
        try:
            files.append({'path': rel, **digest(path)})
        except OSError as error:
            unreadable.append({'path': rel, 'error': str(error)})
    for path in sorted(root.rglob('PROMOTIONS.md')) + sorted(root.rglob('INVIVO.md')):
        for symbol, cu in sorted(set(PROMOTION.findall(path.read_text(encoding='utf-8', errors='replace')))):
            source = 'src/main-partial.c' if cu == 'main.c' else 'src/' + cu
            functions.append({'source': source, 'function': symbol, 'confidence': 'strong',
                              'evidence_file': path.relative_to(root).as_posix()})
    promotion_docs = sorted(root.rglob('PROMOTIONS.md'))
    result = {'schema': 1, 'kind': 'external_candidate_metadata', 'root_identity': digest(promotion_docs[0]) if promotion_docs else None,
              'files': files, 'unreadable_files': unreadable, 'functions': functions,
              'restriction': 'Evidence only: no file was copied, included, compiled, or used as a runtime dependency.'}
    write_json(a.output, result)
    print(a.output)


if __name__ == '__main__':
    main()
