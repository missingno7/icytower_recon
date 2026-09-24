# Replay REPLAY_HEADER read-only .rdata diagnostic

Date: 2026-09-24. This note records a read-only inspection of the retained uppercase-owner / explicit-six-character-initializer probe. No maintained source, generated state, recovery status, or protected function body was edited.

## Source-backed owner evidence

The current storage card docs/current/storage/game-replay/224757.json proves that the original owner is global REPLAY_HEADER, type const char[6], size 6, section .rdata, bytes ITR140, at VA 0x4d7dd0. It is DWARF DIE 224757, declared at original replay.c:20; the original COFF symbol is _REPLAY_HEADER in final section 3 at value 15824.

The charlist probe object has _REPLAY_HEADER at .rdata+715; its comparison maps that contribution's section base to 0x4d7b05, so the owner resolves to 0x4d7dd0 exactly. The candidate owner identity, bytes, section, and final address therefore agree with the historical storage record. That does not prove the full .rdata contribution or object identity.

## Exact relocation findings

The retained probe is create-replay-header-charlist-noproto (TDM-2, GCC 4.4.1, -O2), based on docs/attempts/research-20260924-create-replay-context/header-owner-charlist.c. In its object .rdata, the first Harold is at offset 153 and the owned REPLAY_HEADER is at 715. In the original PE .rdata, Harold is at .rdata offset 14974 (VA 0x4d7a7e) and ITR140 is at .rdata offset 15824 (VA 0x4d7dd0). Anchoring by the exact owner address makes the candidate Harold target 0x4d7b9e, 288 bytes after the original. The string bytes themselves are present in both images.

Strict comparison records:

- create_replay: its two relocations to REPLAY_HEADER resolve exactly at 0x4d7dd0 and 0x4d7dd4; the Harold relocation at function offset 127 resolves to candidate 0x4d7b9e instead of original 0x4d7a7e (delta +288).
- get_replay_property: 11 .rdata relocation targets differ. Deltas vary (+288, +117, +129, +105, and -552 in this receipt), showing the target set cannot be repaired by applying one section-base adjustment.
- load_replay: the ITR140 literal at function offsets 16 and 150 resolves to 0x4d7ba5 versus 0x4d7a85 (delta +288); the literal relocation at offset 113 resolves to 0x4d7ba8 versus original 0x4d7dd0 (delta -552). Its other reported relocations include a non-.rdata anomaly, so this note treats only explicit .rdata target evidence as relevant.
- update_file_list: the .rdata reference at function offset 79 resolves to 0x4d7b05 versus 0x4d7960 (delta +421).

The current maintained 7/15 exact set is get_sort_method, set_sort_method, hash, destroy_replay, update_file_list, load_replay, and get_replay_property (src/recovery.json). The charlist receipt's strict exact count is 4/15, with get_replay_property, load_replay, and update_file_list among the regressed neighbors. These unchanged bodies are not licensed for edits. The 7/15 control remains the relevant preserved baseline; function equality does not prove section ownership.

## Outcome and missing evidence

Established: the immediate strict failures are resolved .rdata target-address mismatches. The uppercase object's owner is anchored correctly, while literal targets elsewhere in the emitted .rdata contribution do not land at their historical addresses. The PE data confirms byte strings and final addresses, but cannot identify original object-relative relocation records or explain the compiler's full contribution ordering.

Not established: which source declaration/expression or GCC 4.4.1 emission decision accounts for the varying target deltas. The original replay object is unavailable, and the current evidence has no object-relative relocation table, section contribution map, or exact full historical replay.c source. The next high-value artifact is an original replay .o (or equivalent object-level section/relocation dump); absent that, no tested owner-context variant proves the layout-only hypothesis. Do not promote this as an ownership or layout match.



