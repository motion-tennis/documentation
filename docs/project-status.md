# Project status and stage ledger

[Documentation home](../README.md) · [Stage definitions](project-stages.md) · [Contribution workflow](contribution-workflow.md)

**Active stage: S1 — Isolated component slices.**

**Last evidence review: 2026-11-11.** The project user explicitly accepted the [S0 baseline](s0-baseline.md) on 2026-10-26, including the dedicated Pi/PC TCP state channel in ADR 0011, and authorized its use for S1. S0 is accepted; S1 is released and incomplete. The accepted artifacts include the complete v0.3 contract, generated host-codec/size/resource evidence, offline semantic fixtures and all five component reviews/S1 handoffs. No S1 runtime slice or hardware result is established by that S0 acceptance. This review checks tracking and scoped offline debug delivery against current source and passing local evidence; it does not accept the shared S1 gate. The exact revisions, hashes, evidence and retained limitations are recorded below.

This is the sole mutable stage ledger. Component guides link here rather than maintaining separate active-stage flags. Record the exact documentation revision read in each task. A pinned status snapshot supplied with an authorized task is acceptable for an isolated/offline checkout; a stale link or memory is not evidence of a later stage release.

## Stage state

| Stage | State | Evidence / missing gate |
| --- | --- | --- |
| S0 | Accepted | Human acceptance recorded on 2026-10-26 for the pinned full-match contract, ADR 0011, host evidence and versioned assumptions. |
| S1 | Active, incomplete | Released by the S0 decision; isolated component slices, reproducible local evidence and shared S1 review remain outstanding. |
| S2 | Not released | Needs accepted S1 and actual device/transport feasibility evidence. |
| S3 | Not released | Needs accepted S2; no live end-to-end path exists. |
| S4 | Not released | Needs accepted S3; no playable doubles implementation exists. |
| S5 | Not released | Needs accepted S4; no measured WLAN comparison or system acceptance runs exist. |
| S6 | Not released | Needs accepted S5 and an independently reproducible configuration. |
| S7 | Deferred | Requires a separate extension decision; S6 acceptance does not release it. |

## Repository evidence at this review

| Repository | Implemented artifacts | Next bounded S1 contribution |
| --- | --- | --- |
| documentation | Accepted v0.3 contract baseline, generated host codecs, offline semantic oracle/fixtures, resource evidence and documentation/freshness checkers | Keep component slices pinned to the accepted contract and record actual S1 build/test evidence and remaining dependencies. |
| motion-tennis-controller | Documentation, contract review and S1 acquisition handoff; no firmware/build setup | Build the bounded local acquisition/safe-output slice after actual board/pins and toolchain prerequisites are pinned. |
| motion-tennis-camera-tracking | Offline adapter and bounded trace-v1 exporter at `5a72519`, with 64 passing Python tests, generated v0.3 codec evidence and actual consumer compatibility checks | Include the exercised typed physics/debug handoff in shared S1 review; remaining producer profiles, live capture, inference and transport need their own evidence. |
| motion-tennis-physics-engine | Deterministic C++ core and bounded typed tracking bridge at `d6d7143`, with full observation/map provenance and stricter pose validation, exercised by seventeen cross-consumer cases | Fix retained controller-transaction duplicate handling, then close the remaining shared game/physics fixture and emitted-event evidence. |
| motion-tennis-game-engine | In-memory C# S1 store and 14 existing passing mock-Pi host checks at `f34c226`; known score-validation and shared-evidence gaps remain | Fix long-tiebreak and completed-counter validation, then close typed-to-v0.3 fixture/identity and diagnostic/event evidence. |
| debug-units | Delivered offline core, marker, clock-map and pipeline/match-provenance profiles at `84c3c2a`; four synthetic fixtures and 72 passing tests | Review/adopt exporter profiles with controller/physics/game/tracking owners and include evidence in the shared S1 review; live exports and hardware remain later work. |

This table records evidence, not person assignments. Claim a task and its file scope through the existing human coordination channel or review system using the [task template](contribution-workflow.md#task-brief). Do not invent contributor names, deadlines or tickets.

### Local S1 debug evidence — 2026-11-08

The bounded marker-link, clock-map and pipeline/match-provenance slices were implemented on `task/s1-marker-conformance` in `debug-units`, with related documentation and the Windows freshness fix on the same named documentation branch. Bases are debug `62d4cb3` and documentation `3260994`; implementation/review and local commits were complete. The `debug-units/docs/s1-clock-pipeline.md` handoff and exporter review package records the explicit offline profiles, fixtures, exact base revisions and remaining dependencies. At the original 2026-11-08 handoff, public remote publication was blocked by automatic approval review pending explicit push authorization. The user subsequently authorized publication: debug `84c3c2a0289011764980de44575bdb14c7d83376` and the related documentation changes are now on remote `main`, verified again on 2026-11-11. The historical local-only delivery notes describe that earlier handoff, not the current publication state. No stage was released by publication.

All 72 debug tests, ten freshness-checker tests and four synthetic CLI fixtures passed. The Windows S0 freshness failure was repaired using portable path identities and LF/CRLF text handling, with substantive changes and path collisions still rejected. Historical S0 evidence and all contract sources are unchanged. The full local documentation check passes; unavailable component checkouts remain skips. This is synthetic offline evidence, not validated real exports, clock fitting, hardware timing, complete tennis rules or a running game. Producer-owner review and the other component S1 gates remain open.

### S1 tracking evidence — 2026-11-11

The offline recorded/synthetic Python pose adapter is implemented in tracking commit `0509fbd8cc15dd7b5a1a640814b66e890aef1ca3`, prepared on `task/s1-recorded-pose-adapter` from tracking `a7ae1bd` and shared `documentation@e541fd2`. It preserves session/frame/person identities and native timestamps, validates coordinate/quality/calibration and timing evidence, bounds the latest-frame handoff and retains explicit rejection/loss diagnostics. The [pinned component handoff](https://github.com/motion-tennis/motion-tennis-camera-tracking/blob/0509fbd8cc15dd7b5a1a640814b66e890aef1ca3/docs/s1-recorded-pose-adapter.md) records source, fixtures, reproducible commands and evidence. On 2026-11-11, the project user explicitly authorized Codex to commit this slice and push both tracking and documentation to remote `main`; Git commit/ref state records publication separately from validation.

Host validation on 2026-11-11 used Windows and Python 3.14.3: all 47 API/fixture/CLI tests passed. A separate environment with pinned development dependencies passed generated-codec checks for six cases and twenty envelopes, including four-person and maximum-counter cases. The largest exercised encoded envelope was 497 bytes, below the 1200-byte cap. These checks establish the exercised Python host-codec boundary; Pi/debug fixture and diagnostic-format review and shared S1 acceptance remain pending. They do not establish nanopb/C, target-device or live transport interoperability, and this record does not accept a component or shared stage gate.

The user's report of an available working Xbox Kinect is recorded separately in [hardware evidence](hardware.md#available-kinect-and-evidence-boundary). This slice uses controlled observations and does not establish live capture, inference, body tracking, hardware timing or networking. The webcam-first 2.5D baseline and accepted schema/profile remain unchanged.

### S1 tracking consumer compatibility — 2026-11-11

The user authorized the typed physics pose handoff, bounded trace-v1 exporter, validation fixes and real consumer checks, then explicitly authorized committing, merging and pushing tracking, physics and documentation to remote `main`. The [compatibility handoff](s1-tracking-consumer-compatibility.md) pins tracking `5a72519d0441e88fb359b7f98a57b1f1f2581478`, physics `d6d71436f30a1effd1572b85daaf560ebaf40ba1` and unchanged debug `84c3c2a0289011764980de44575bdb14c7d83376`, together with the original baselines. The work was prepared on `task/s1-tracking-consumer-compatibility`; containing commits and remote refs establish publication. The schema/profile are unchanged. Source hashes and environment in the saved report describe the dated validation snapshot, including its then-uncommitted working-tree state.

All 64 tracking Python tests passed. Generated Python checks passed six cases and twenty envelopes, with a largest exercised size of 497 bytes including the envelope. The actual typed physics bridge/core passed seventeen compatibility cases across five adapter-produced frames and fifteen generated/decoded envelopes; the actual debug auditor passed seven compatibility cases. A deliberate overflow case correctly failed trace completeness: seventy-two lost records matched seventy-two source-sequence gaps and log-drop accounting. These checks use explicit synthetic controller, confirmed-binding and Pi-map fixtures. They establish the exercised offline handoff, not actual clock fitting/accuracy, hardware, live networking, calibrated fusion, target C-codec interoperability or shared S1 acceptance.

The typed bridge now rejects pose-calibration mismatch, invalid or excessively uncertain maps/captures, unavailable required joints, future processing/send boundaries and stale observations, including after state waiting. It preserves raw capture/session/clock and immutable Pi-map provenance, and frame-status/restart fences invalidate unsupported cached poses. Tracking trace export preserves producer sequences before loss and keeps unknown lifecycle timing as explicit untimed metadata. Broader producer-profile adoption and the remaining physics/game/controller contributions stay open.

## Active gate checklist

**Checklist stage: S1.**

Checked delivery items establish the named bounded implementation and its local evidence. Cross-component profile adoption, compatible fixture/timestamp evidence and human stage acceptance remain separate requirements below.

- [ ] Deliver the controller's bounded local acquisition and safe-output slice with pinned board/Zephyr/toolchain inputs and explicit synthetic versus device evidence.
- [x] Deliver the tracking recorded-input adapter with identity, timestamp, quality/calibration and invalid-input fixtures. Verified at `0509fbd`: 47 host tests and 20 generated Python codec envelopes passed.
- [ ] Deliver the deterministic minimal physics batch core using fake adapters, explicit query/commit correlation, ordered and periodic work, and complete candidate rollback.
- [ ] Deliver the headless game state store with a mock Pi writer, atomic acceptance/rejection, duplicate/session/epoch handling and bounded retention cases.
- [x] Deliver the scoped offline debug conformance checks for marker links and separately bounded clock/map/match fixtures, preserving current audit coverage. Verified at `84c3c2a`: 72 tests and all four synthetic CLI fixtures passed.
- [ ] Collect reproducible local build/check commands, pinned compatible revisions/dependencies/fixtures, bounded memory/queues, success/failure cases and correlation/timestamp evidence across the S1 contributions.
- [ ] Record human acceptance of the shared S1 evidence and release S2.

### Remaining S1 work at this review

- **Controller:** the checkout at `8370c26` remains documentation-only. Pin the actual board/pins and Zephyr toolchain, then deliver acquisition, safe-output and failure/overflow evidence under its existing handoff.
- **Physics:** queue-only controller-transaction deduplication remains: one transaction produced three accepted commits in the earlier probe at `51f1535`, and retained handling after queue selection/in-flight/commit still needs repair. The current uncommitted compatibility slice fixes the pose-calibration/provenance gap with a typed bridge and post-wait eligibility checks; it does not close the whole core contribution. Complete the remaining shared game/physics fixture and emitted-event evidence. See the [component handoff](https://github.com/motion-tennis/motion-tennis-physics-engine/blob/main/docs/s1-batch-core.md) and [current local compatibility evidence](s1-tracking-consumer-compatibility.md).
- **Game:** the existing 14 checks do not cover the defects demonstrated at unchanged revision `f34c226`: a legal active tiebreak at `100:99` was rejected, while completed-tiebreak counters beyond the accepted uint56 range were accepted. Repair these contract checks and retain compatible committed event/diagnostic evidence. See the [component handoff](https://github.com/motion-tennis/motion-tennis-game-engine/blob/main/docs/s1-state-store.md).
- **Shared evidence and review:** prove physics/game agreement with the accepted fixture identities and explicit rejected-input accounting; complete the remaining emitted correlation/timestamp evidence and producer-profile adoption; collect the complete compatible revision, dependency, resource and command/results set. The exercised tracking-to-physics typed bridge and tracking-to-debug trace export now have local consumer evidence; other producer profiles and full shared review remain open. Real exports and hardware/network measurements remain later-stage evidence.
- **Stage decision:** after the remaining work is verified, obtain and record human acceptance of S1 before releasing S2. This checklist update makes no stage decision.

## Gate decision record

### S0 accepted — 2026-10-26

- **Decision:** accepted; S1 released as the active, incomplete stage.
- **Responsible human and authorization:** the project user explicitly approved the explained S0 baseline and dedicated TCP state channel in this chat and agreed to use that basis for S1. Codex records that decision on the user's behalf; acceptance is not inferred from passing tests or from the earlier commit request.
- **Reviewed documentation revision:** `d1b0c099c95571615a5ec09697146fe972b952be`.
- **Schema SHA-256:** `b6728e240316e957f5c5addb973f12f9a57fffbcdacc4331f3db5e06895f360b`.
- **Profile SHA-256:** `a3533462fdebfd4c7c2f87eaa3bd579d3056170e3dcfc6a6c68ed34474c1d969`.
- **Compatible component revisions:** controller `f8fc435230f7befeb01b5ff7864067098348135d`; tracking `e2dce918b8fa7b8d494ac36c2f91e4f84df3aacc`; physics `c4202506870fa45aa007f840275eddf58f1d3df5`; game `4564102386c26049b951c5e0ef1e78ab6216b9a3`; debug `1cd720f9f1b217ce06793b188c0fb245a47c9b58`.
- **Evidence:** [S0 baseline and component reviews](s0-baseline.md), [saved codec/resource/semantic report](../evidence/s0-contract-report.json), [validation record](validation.md#s0-full-match-contract-and-host-evidence-2026-10-26) and [ADR 0011](adr/0011-full-match-contract-and-state-stream.md). The recorded run passed 27 Python/C round trips, 62 rejection/envelope cases and 32 semantic tests. Six freshness tests and the nine existing debug tests passed; all six repositories supplied the required orientation/review/handoff contributions. None was marked not applicable.
- **Adopted interface decision:** complete-match v0.3 setup/state/event semantics with bounded dedicated Pi/PC TCP state messages; controller/feedback and pose/status UDP, continuous sampling, required query/response, marker/clock semantics and existing deadlines remain as specified.
- **Retained limitations:** host-codec/storage evidence does not establish target ABI/device headroom, transport latency, hardware readiness, clock accuracy or a playable rules engine. Numeric performance targets, exact device/dependency choices and gameplay tuning retain their [versioned assumptions and later evidence gates](s0-baseline.md#versioned-assumptions-and-later-gates). Acceptance adopts those assumptions as a development baseline, not as measured outcomes.
- **Released scope:** bounded S1 component slices and their local evidence, following the recorded handoffs. S2 and later stages remain unreleased; S7 remains separately scoped.

The accepted schema/profile bytes and source hashes are unchanged. Their original `0.3-proposed` and proposal-status labels identify the reviewed artifact; this ledger records the subsequent human adoption without creating a new wire/profile identity.

#### Completed S0 gate checklist

- [x] A common stage sequence, local orientation/workflow and agent entry instructions exist in all six repositories.
- [x] Specify and technically review the versioned roster/avatar/serve/score extension with physics/game producer and consumer boundaries and the diagnostic contract; v0.3 source and review findings are in the S0 baseline.
- [x] Pin compatible schema/profile and validation-source hashes, define fixtures and verify generated host-codec maximum encodings and contract-storage bounds, including eight-query/full-match cases. ADR 0011 explicitly resolves the state-message size conflict.
- [x] Record stage-blocking interface decisions as the proposed v0.3 baseline and versioned assumptions with later measurement gates; numerical performance targets remain proposed.
- [x] Collect all five component technical reviews and define bounded first S1 tasks, dependencies and acceptance evidence.
- [x] Record human acceptance of the S0 baseline, ADR 0011 and documented assumptions; then release S1.

Future decisions append a dated record with the responsible human, exact revisions/hashes, gate results, limitations and next released stage. Preserve this acceptance and its evidence when recording later stages.

Repository task completion and stage acceptance are separate records. A later-stage task exception belongs in its task/handoff, with the human authorization and bounded scope; it does not silently change this ledger. When evidence changes, update the affected current rows and retain historical decision records.

## Updating the README dashboard

The README progress panel and `assets/project-progress.svg` are generated views of this ledger and the stage names in [project stages](project-stages.md). Edit the source documents, then run from this repository:

```sh
python3 scripts/render_progress.py
python3 scripts/check_docs.py
```

The first command updates only the SVG and the marked progress block in the README. The second also checks that both views match the source; `python3 scripts/render_progress.py --check` performs just that read-only freshness check. These tools use Python 3.9+ and the standard library, with no external badge service or scheduled job. Regeneration is explicit, not a live GitHub fetch.

Keep one row for each S0–S7 stage. Supported states are `Active, incomplete`, `Blocked`, `Not released`, `Accepted` and `Deferred`. `Deferred` is reserved for S7, which stays deferred until explicitly selected after S0–S6 acceptance. Keep the active-stage line, stage table, evidence-review date and active gate checklist consistent when recording an authorized transition. Update the `Checklist stage` binding and replace the checklist for the new stage while retaining the previous decision/evidence in the gate record. To close delivery, S6 may remain the selected stage with state `Accepted`; S7 still needs separate authorization.

Accepted core gates count S0–S6 only. Checklist counts describe the selected stage and are not effort-weighted. Neither count is an overall completion percentage, and generating the dashboard never accepts a gate or releases work.
