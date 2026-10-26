# S0 technical baseline and review evidence

[Documentation home](../README.md) · [Central status](project-status.md) · [Protocol](protocol.md) · [ADR 0011](adr/0011-full-match-contract-and-state-stream.md)

Evidence date: 2026-10-26. This user-authorized S0 task supplies the full-match contract, generated host-codec checks, offline semantic fixtures, resource bounds, component reviews and bounded S1 handoffs. It does not implement firmware, tracking, simulation, networking, rendering or a complete rules engine. The project user accepted this baseline on 2026-10-26; the [central gate decision](project-status.md#s0-accepted--2026-10-26) releases S1.

## Task and compatible baseline

The allowed scope is shared schema/profile, contract-validation tools/fixtures and coordinated documentation across all six repositories. Dependencies are the existing agreed doubles, association, continuous IMU, diagnostic marker and Pi-reference clock contracts. No later-stage exception is needed: these are S0 validation artifacts. The accepted artifact is `motion.v03`, protocol `0.3-proposed`, profile `webcam-pi3-doubles-v3`; all numeric performance targets remain proposed and unmeasured. The original proposal/status labels remain in the byte-pinned schema/profile as provenance; the central ledger records their subsequent adoption. Acceptance changes no payload, profile value or evidence hash.

| Repository | Inspected base revision | Compatible S0 revision | Included changes |
| --- | --- | --- | --- |
| documentation | `95c2592` | `d1b0c099c95571615a5ec09697146fe972b952be` | v0.3 schema/profile, tools, fixtures and central evidence |
| motion-tennis-controller | `a4efd91` | `f8fc435230f7befeb01b5ff7864067098348135d` | Component review and S1 handoff |
| motion-tennis-camera-tracking | `d7e91b2` | `e2dce918b8fa7b8d494ac36c2f91e4f84df3aacc` | Component review and S1 handoff |
| motion-tennis-physics-engine | `55c64e5` | `c4202506870fa45aa007f840275eddf58f1d3df5` | Component review, transport alignment and S1 handoff |
| motion-tennis-game-engine | `80fe7ec` | `4564102386c26049b951c5e0ef1e78ab6216b9a3` | Component review, transport alignment and S1 handoff |
| debug-units | `9a7f27d` | `1cd720f9f1b217ce06793b188c0fb245a47c9b58` | Component review, full-match trace provenance and S1 handoff |

The inspected base commits alone do not contain the accepted S0 artifact. The compatible revisions above were committed locally at the user's request and are pinned by the human gate decision. Use that documentation revision with the exact schema/profile and validation-source SHA-256 values in the machine-readable [contract report](../evidence/s0-contract-report.json). Later acceptance-record edits do not change those contract bytes. Pin both the accepted contract revision and current stage/task revision when beginning an S1 slice.

The earlier local commit step preserved the reviewable artifact; the subsequent explicit human decision accepted S0 and released S1. No push was performed. The documentation checker detects changed, missing or newly added contract sources against the saved report.

## Implemented artifacts and coverage

- [Schema](../spec/motion.proto) and [profile](../spec/reference-profile.json): typed immutable setup, four player bindings, full ball/avatar/serve/rally/score state, separate rule events, configuration hashes/revisions and writer/session fences.
- [Generated-codec checker](../scripts/contract/check_contract.py): actual Python Protobuf and nanopb C generation, compilation, byte-equal round trips, conservative maximum encodings, rejection fixtures and measured host `sizeof` values. All variable fields have [static options](../scripts/contract/motion.options); no callback/dynamic collection is emitted.
- [Semantic oracle](../scripts/match_contract.py) and [inspectable synthetic fixtures](../tests/match/fixtures.py): full-candidate structural/correlation checks and a test-only atomic store. It consumes prepared results and does not compute tennis rules, hits, movement or clock fits.
- [Semantic tests](../tests/match/test_match_contract.py): setup digest/uniqueness, state completeness, required query correlation, eight inputs/two per controller, periodic-only work, rule-event identity, invalid-input accounting, stale versions, exact duplicate/changed-payload behavior, full visible-state rollback, writer restarts, technical-pause/score distinctions and bounded retention pressure.
- [Evidence freshness checks](../scripts/check_contract_evidence.py) and [tests](../tests/test_contract_evidence.py): stale schema/profile/tool/test content, incomplete reports and missing/new sources invalidate the saved evidence.

The suite's codec maxima are **structural upper bounds**, with every bounded collection/field populated and maximum-width legal integer types. Those witnesses need not be valid game situations. Separate semantically valid fixtures pass the offline validator before cross-codec comparison. The report labels both populations explicitly.

## Size and resource results

The exact output and environment are retained in the [report](../evidence/s0-contract-report.json); rerun it when any contract input changes. A valid high-width eight-decision full-match envelope is **1,434 bytes**, so retaining the old 1,200-byte state datagram would reject a permitted batch. [ADR 0011](adr/0011-full-match-contract-and-state-stream.md) therefore specifies the accepted dedicated 8,192-byte framed TCP state channel. Controller input/feedback and pose/status retain their 1,200-byte UDP limit, rates and deadlines.

The final run passed **27 Python/C round trips, 62 rejection/envelope cases and 32 semantic tests**. The separate freshness suite passed six tests. The existing debug suite passed all nine tests and its synthetic audit retained expected outcome accounting.

| Envelope | Conservative maximum bytes | Channel cap bytes |
| --- | --- | --- |
| Controller input | 225 | 1,200 UDP |
| Controller feedback | 338 | 1,200 UDP |
| One-person skeleton | 584 | 1,200 UDP |
| Eight-query request | 486 | 8,192 state TCP |
| Complete-state response | 1,465 | 8,192 state TCP |
| Full-match update with eight decisions and sixteen rule events | 2,779 | 8,192 state TCP |
| Full publication | 2,770 | 8,192 publication TCP |

The generated C envelope occupies 4,376 host-ABI bytes. Conservative modeled contract storage is 25,446 bytes for the controller, 2,690,110 bytes for physics and 2,522,406 bytes for the game service. All declared budgets pass. The report records each formula and its individual terms. Contract-storage budgets are 64 KiB for the controller and 8 MiB each for Pi/game, with a 16 KiB ceiling for one generated envelope structure. These are versioned contract allocations, not measured available device RAM. Queue/history/retention products include declared framing and bookkeeping allowances. They exclude code, call stacks, network/OS heaps, image/model buffers, runtime logging and device-specific ABI padding. The offline C harness itself uses workstation buffers and is not controller firmware.

A host pass proves bounded schema representation and declared allocation products. S1 must repeat codec/ABI/build checks on the chosen target toolchains and retain linker/stack/heap evidence; S2 must measure actual memory headroom, rates, deadlines and state-stream blocking/recovery. No physical board, camera, Wi-Fi, clock accuracy or latency test was performed here.

## Versioned assumptions and later gates

| Area / decision register | S0 disposition | Required later evidence |
| --- | --- | --- |
| Full-match and size, O-10/O-19 | Accepted v0.3 typed contract, exact-hash negotiation and bounded state stream in ADR 0011; host fixtures/resource model supplied | S1 target codecs/ABI, S2 state capacity and transport, S4 full gameplay |
| Match format, O-18 | Standard advantage games and tie-break sets; supported sets-to-win 1/2/3, default 2. Match length remains a reviewable profile assumption | Chosen run configuration and complete S4 rules/serve/end-change acceptance |
| Motion, calibration and confidence, O-05/O-06/O-18 | SI/body-local 2.5D, immutable tuning hash and explicit invalidity; synthetic fixtures use an identified placeholder tuning hash | Versioned concrete parameter/calibration artifact and recorded-input S1/S2 evidence, then S4 tuning; no fabricated accuracy |
| Boards, sensors, dependencies, O-01/O-02/O-03/O-04/O-14 | Pi 3 B, webcam/Windows direction, MPU-6050/I2C/Zephyr fixed; exact board/pins/model/runtime manifests remain per-task prerequisites | Pin actual parts and toolchains before the corresponding S1 slice; S2 capture/IMU/GPU/shared-INT feasibility |
| Timing/marker/clock parameters, O-07/O-13/O-15/O-17 | Preserve 200 Hz, independent markers, Pi affine maps, raw identities and uncertainty. Existing numerical targets remain provisional | S1 synthetic rejection/conformance, S2 real capture/IRQ/map bounds, S3 integrated trace, S5 measured timing |
| Power and output, O-08 | Battery operation and bounded safe outputs remain required; no capacity/duration assumption treated as evidence | S1 safe startup/failure behavior; S2 electrical/current/onset measurements |
| Trust and deployment, O-09/O-16 | Controlled LAN with bound sender/session; same v0.3 application profile in both WLAN variants. No cryptographic authentication claim | S2 reachability/isolation and reconnect proof, S5 matched topology evaluation; trust-boundary changes need a new profile |
| Debug viewer and extensions, O-11/O-12 | Trace-v1 match/clock/marker provenance defined; current auditor coverage remains limited | S1 offline conformance, S2 collection, S3 viewer; hardware/model/radio alternatives stay separately scoped |

No blocker is hidden by an invented measurement. Parameters that do not change the interface may remain versioned assumptions with a named later gate. A failed size/resource/semantic fixture must be repaired or reviewed as an explicit contract revision.

## Component reviews and S1 handoffs

All five documents are AI technical reviews of their producer/consumer boundary. The subsequent human acceptance is recorded separately in the [central ledger](project-status.md#s0-accepted--2026-10-26). The physics/game reviews cover both ends of the shared complete-state interface; other reviews preserve the unchanged controller/pose contracts and diagnostic provenance.

| Component | Reviewed handoff | First bounded S1 outcome |
| --- | --- | --- |
| Controller | [Review and acceptance cases](https://github.com/motion-tennis/motion-tennis-controller/blob/main/docs/s0-contract-review.md) | Local MPU-6050/Zephyr acquisition, identities and safe outputs; actual board/pins required |
| Tracking | [Review and acceptance cases](https://github.com/motion-tennis/motion-tennis-camera-tracking/blob/main/docs/s0-contract-review.md) | Recorded-input adapter and identity/time/quality rejection fixtures |
| Physics | [Review and acceptance cases](https://github.com/motion-tennis/motion-tennis-physics-engine/blob/main/docs/s0-contract-review.md) | Deterministic minimal batch core with fake adapters and complete candidate rollback |
| Game | [Review and acceptance cases](https://github.com/motion-tennis/motion-tennis-game-engine/blob/main/docs/s0-contract-review.md) | Headless state store with a mock Pi writer; no rule calculation |
| Debug | [Review and acceptance cases](https://github.com/motion-tennis/debug-units/blob/main/docs/s0-contract-review.md) | Offline marker-link conformance; map/match checks in separate S1 slices |

Review found and repaired two identity/connection gaps: rejected `BallStateResponse` now echoes its top-level game session, and a new state stream explicitly attaches through `hello`/`hello_result` to the existing control-registered writer session/epoch. Typed match setup also carries the current writer epoch and exact command/digest retry identity. Component guides and the [full-match trace contract](https://github.com/motion-tennis/debug-units/blob/main/docs/trace-format.md#full-match-v03-provenance) reflect these boundaries.

## Reproduce the contract evidence

Run from the documentation repository. Host verification used Python 3.14 and a C11 compiler on Linux; exact package/compiler versions are in the report. The documentation checker alone still needs only Python 3.9+ and the standard library. Initial toolchain installation needs network access or equivalent predownloaded packages/archive; the actual check is offline. Keep generated code and binaries in the checker's temporary directory.

```sh
python3 -m venv /tmp/motion-tennis-s0-venv
/tmp/motion-tennis-s0-venv/bin/python -m pip install -r scripts/contract/requirements.txt
/tmp/motion-tennis-s0-venv/bin/python scripts/contract/fetch_nanopb.py /tmp/nanopb-0.4.9.1
/tmp/motion-tennis-s0-venv/bin/python scripts/contract/check_contract.py --nanopb-root /tmp/nanopb-0.4.9.1 --report evidence/s0-contract-report.json
python3 -m unittest discover -s tests -p 'test_contract_evidence.py' -v
python3 scripts/render_progress.py
python3 scripts/check_docs.py
git diff --check
```

The [package pins](../scripts/contract/requirements.txt) and [nanopb source/archive lock](../scripts/contract/nanopb-source.lock.json) fix the toolchain inputs; the fetcher verifies hashes and preserves the dependency license. An existing verified archive can be supplied with `--archive`. Updating profile bounds requires review and an explicit `--update-options` run; ordinary checking refuses stale options. `--codec-only` is a development aid and cannot produce accepted complete S0 evidence.

The existing debug audit/tests are run separately from `debug-units` using its real README commands. Their pass does not add marker, clock or full-match conformance to that older auditor. S0 defines those fixtures and handoffs; the broader implementation belongs to S1.

## Gate disposition

**S0 accepted; S1 released on 2026-10-26.** The project user approved the complete-match contract, dedicated TCP state channel and use of this baseline for isolated component development. The [central ledger](project-status.md#s0-accepted--2026-10-26) retains the completed S0 checklist, exact revisions/hashes, evidence and limitations. The active S1 checklist starts with no implementation items complete. Hardware, performance and full gameplay gates remain in their named later stages.
