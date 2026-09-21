"""Pool-aligned literal diagnosis: chain confirmation, boundary and similarity guards."""
import unittest
from types import SimpleNamespace
from pool_literals import diagnose, source_repairs


class FakeExe:
    def __init__(self, rdata, base=0x1000):
        self.rdata = rdata; self.base = base; self.image_base = 0
        self.sections = [{'name': '.rdata', 'rva': base}]
    def section_bytes(self, s): return self.rdata
    def at_va(self, va, size):
        off = va - self.base
        if off < 0: return b''
        return self.rdata[off:off + size]


def pool_of(*items):
    data = b''; offsets = []
    for item in items:
        offsets.append(len(data)); data += item
    return data, offsets


def report_for(offsets, names=None):
    return {'functions': [{'name': names[i] if names else 'f%d' % i, 'relocations': [{'symbol': '.rdata', 'addend': a}]} for i, a in enumerate(offsets)]}


class PoolLiteralTests(unittest.TestCase):
    def test_chain_of_spacing_differences_confirmed_by_following_anchor(self):
        hist, _ = pool_of(b'UNIQUE-HEAD-A\0', b'Profile name:          %s\n\0', b'Rank:                  %s\n\0', b'       \0', b'UNIQUE-TAIL-B\0')
        cand, offs = pool_of(b'UNIQUE-HEAD-A\0', b'Profile name:           %s\n\0', b'Rank:                   %s\n\0', b'        \0', b'UNIQUE-TAIL-B\0')
        anchors, proposals = diagnose(report_for(offs), cand, FakeExe(hist))
        self.assertEqual(sorted(anchors), [offs[0], offs[4]])
        self.assertEqual([(p['candidate'], p['historical']) for p in proposals],
                         [('Profile name:           %s\n', 'Profile name:          %s\n'), ('Rank:                   %s\n', 'Rank:                  %s\n'), ('        ', '       ')])
        self.assertEqual(sum(p['length_delta'] for p in proposals), -3)

    def test_unconfirmed_chain_and_extra_literal_are_not_proposed(self):
        # The tail anchor disagrees with the accumulated delta: nothing is proposed.
        hist, _ = pool_of(b'UNIQUE-HEAD-A\0', b'Profile name:          %s\n\0', b'zzzz\0', b'UNIQUE-TAIL-B\0')
        cand, offs = pool_of(b'UNIQUE-HEAD-A\0', b'Profile name:           %s\n\0', b'zz\0', b'UNIQUE-TAIL-B\0')
        self.assertEqual(diagnose(report_for(offs), cand, FakeExe(hist))[1], [])
        # An extra candidate literal misaligns the following text mid-string: boundary guard rejects.
        hist, _ = pool_of(b'UNIQUE-HEAD-A\0', b'%d second%s\0', b'%d minute%s\0', b'UNIQUE-TAIL-B\0')
        cand, offs = pool_of(b'UNIQUE-HEAD-A\0', b'\0', b'%d second%s\0', b'%d minute%s\0', b'UNIQUE-TAIL-B\0')
        self.assertEqual(diagnose(report_for(offs), cand, FakeExe(hist))[1], [])

    def test_dissimilar_text_at_a_boundary_is_not_a_repair(self):
        hist, _ = pool_of(b'UNIQUE-HEAD-A\0', b'%s:combo=%d\0', b'UNIQUE-TAIL-B\0')
        cand, offs = pool_of(b'UNIQUE-HEAD-A\0', b'.\0', b'UNIQUE-TAIL-B\0')
        self.assertEqual(diagnose(report_for(offs), cand, FakeExe(hist))[1], [])

    def test_source_repairs_require_a_unique_token(self):
        proposals = [{'candidate': ' no sound', 'historical': 'no sound', 'functions': ['init_game'], 'addend': 0, 'historical_va': 0, 'length_delta': -1}]
        edits, skipped = source_repairs('log(" no sound"); x(" no sound");', proposals)
        self.assertEqual(edits, []); self.assertEqual(skipped[0]['token_count'], 2)
        edits, skipped = source_repairs('log(" no sound");', proposals)
        self.assertEqual(edits[0]['after'], '"no sound"'); self.assertEqual(skipped, [])


if __name__ == '__main__': unittest.main()
