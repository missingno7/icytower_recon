# Batch TU probe helper

`tools/batch_tu_probe.py MANIFEST.json` runs a chosen batch of complete-function body overlays through the existing diagnostic `tools/tu_context_probe.py`. The manifest names one target CU, source file, function, and at least two probe objects with `name`, unique `label`, and retained `body` path. Choose the batch size from independent hypotheses; avoid factorial source combinations. Optional `order` defaults to `current`; `no_prototypes` defaults to true. A unique label creates evidence under `docs/attempts/tu-context/<target>/` and output under `build/tu-context/<target>/`.

The wrapper reuses a receipt only when its target, source, label, body path, source/body byte hashes, and reconstructed overlay hash still match. This also catches changed definition order or prototype settings. `--reuse-only` validates and summarizes saved receipts without invoking the compiler. Its summary includes the strict function status, candidate/history sizes, first mismatch, whole-TU exact match count plus gain/loss lists, and effective emission groups. This is diagnostic evidence only; it does not update the oracle, recovery ledger, or production sources.

Example:

```powershell
python tools/batch_tu_probe.py docs/attempts/research-20260923-collision-original/batch-manifest.json --reuse-only
```
