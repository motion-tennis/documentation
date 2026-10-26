# S0 offline generated-codec checks

These tools validate the proposed shared [schema](../../spec/motion.proto) and
[profile](../../spec/reference-profile.json). They are contract fixtures, not
firmware, networking, a tracking adapter or a game service. See the
[S0 review baseline](../../docs/s0-baseline.md) for scope and remaining gates.

## Reproduce

From the documentation repository, create an isolated Python environment and
install the exact generator/runtime versions. The recorded run uses Python
3.14 on Linux x86-64 and GCC; it does not establish another platform's build.

```sh
python3 -m venv /tmp/motion-tennis-s0-venv
/tmp/motion-tennis-s0-venv/bin/python -m pip install -r scripts/contract/requirements.txt
/tmp/motion-tennis-s0-venv/bin/python scripts/contract/fetch_nanopb.py /tmp/motion-tennis-nanopb-0.4.9.1
/tmp/motion-tennis-s0-venv/bin/python scripts/contract/check_contract.py --nanopb-root /tmp/motion-tennis-nanopb-0.4.9.1 --report evidence/s0-contract-report.json
```

Only dependency installation and the explicit source fetch use the network.
`fetch_nanopb.py` verifies the archive SHA-256 and each C source/license hash
against [nanopb-source.lock.json](nanopb-source.lock.json). Its `--archive PATH`
option accepts a previously downloaded archive. Upstream sources remain in the
chosen temporary directory; no modified third-party implementation is vendored.
The checker verifies these same hashes, generates Python and nanopb C codecs in
a temporary directory, compiles the C harness, runs the checks and removes the
temporary build. `--cc` selects a GCC-compatible C compiler.

## Checks and evidence

- All envelope body alternatives receive a conservative maximum encoded-size
  fixture. Every bounded string/byte array and repeated field is full, all
  optional fields are present, and integer widths reach their profile bound.
  These are structural upper bounds, not valid tennis states. Each must fit its
  strictest allowed transport, including controller/pose UDP at 1,200 bytes.
- Python encoding, Python decoding and compiled nanopb C decoding/re-encoding
  must produce identical canonical bytes. Realistic controller/pose fixtures,
  the four-player setup, complete snapshots, eight-query/decision batches and
  periodic-only batches are included. A separately validated high-width batch
  demonstrates why a full match cannot always fit the old UDP ceiling.
- Every bounded collection has an overflow fixture. Additional failures cover
  byte/string limits, invalid UTF-8, embedded NUL, truncated/invalid wire data,
  unknown/duplicate fields, uint64 overflow, non-finite values, unknown enums,
  missing identities, legacy versions and wrong message transports. Some
  failures belong to the field validator; others to the C decoder or its
  canonical byte guard. The report identifies the checking layer.
- The independent [full-match suite](../../tests/match/test_match_contract.py)
  exercises setup/roster invariants, ordered correlation, atomic accept/reject,
  duplicate/retry behavior, stale versions and restart fencing. Its
  [oracle](../match_contract.py) receives prepared candidates; it computes no
  movement, scoring, hits or hardware outcomes.
- Generated C arrays are static and bounded; callbacks fail the check. Recorded
  `sizeof` values feed explicit pending/history/framing/deduplication storage
  formulas and are compared with the profile's contract-storage budgets.
  The C harness itself reserves two 65,536-byte raw test buffers, separately
  reported from the proposed runtime allocation model.

The report pins schema/profile/tool/fixture SHA-256 values, compiler and
generator versions, roundtrip hashes, size bounds, rejection cases, semantic
test count, C layout and storage formulas. It does not prove complete device RAM
fit, target ABI compatibility, real-time performance, WLAN behavior, clock
accuracy, tracking quality or full tennis rules. Those remain S1/S2 and later
evidence. Human S0 acceptance remains separate.

## Contract changes

Static [motion.options](motion.options) is generated from the profile and the
explicit field mappings in [wire_bounds.py](wire_bounds.py). After a reviewed
schema/profile change, use `--update-options` with the normal checker command,
review the option diff, and regenerate the evidence report. An unbounded new
field or stale options fail instead of silently becoming a callback.

`--codec-only` is a development aid: its report explicitly says
`codec_only_incomplete` and cannot stand in for the full S0 evidence. The
[legacy v0.2 schema fixture](../../tests/contract/fixtures/legacy_motion_v02.proto)
comes from documentation revision `95c2592`; its conservative size bounds are
retained for comparison, not represented as valid admitted legacy messages.
