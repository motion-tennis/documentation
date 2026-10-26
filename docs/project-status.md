# Project status and stage ledger

[Documentation home](../README.md) · [Stage definitions](project-stages.md) · [Contribution workflow](contribution-workflow.md)

**Active stage: S1 — Isolated component slices.**

**Last evidence review: 2026-10-26.** The project user explicitly accepted the [S0 baseline](s0-baseline.md), including the dedicated Pi/PC TCP state channel in ADR 0011, and authorized its use for S1. S0 is accepted; S1 is released and incomplete. The accepted artifacts include the complete v0.3 contract, generated host-codec/size/resource evidence, offline semantic fixtures and all five component reviews/S1 handoffs. No S1 runtime slice or hardware result is established by this acceptance. The exact revisions, hashes, evidence and retained limitations are recorded below.

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
| motion-tennis-camera-tracking | Documentation, contract review and recorded-input S1 handoff; no capture/inference runtime | Build the recorded-input adapter and identity/time/quality rejection fixtures. |
| motion-tennis-physics-engine | Documentation, producer-side contract review and deterministic S1 core handoff; no runtime service | Build a deterministic minimal batch core with fake adapters, periodic work, ordering and complete candidate rollback. |
| motion-tennis-game-engine | Documentation, consumer-side contract review and headless S1 store handoff; no service or renderer | Build the headless state store with a mock Pi writer and atomic accept/reject, duplicate and recovery fixtures. |
| debug-units | Existing offline trace checker, synthetic fixture and nine tests; full-match trace specification, contract review and S1 handoff | Implement bounded offline marker-link conformance first; map/match audit extensions remain separate S1 slices. |

This table records evidence, not person assignments. Claim a task and its file scope through the existing human coordination channel or review system using the [task template](contribution-workflow.md#task-brief). Do not invent contributor names, deadlines or tickets.

## Active gate checklist

**Checklist stage: S1.**

- [ ] Deliver the controller's bounded local acquisition and safe-output slice with pinned board/Zephyr/toolchain inputs and explicit synthetic versus device evidence.
- [ ] Deliver the tracking recorded-input adapter with identity, timestamp, quality/calibration and invalid-input fixtures.
- [ ] Deliver the deterministic minimal physics batch core using fake adapters, explicit query/commit correlation, ordered and periodic work, and complete candidate rollback.
- [ ] Deliver the headless game state store with a mock Pi writer, atomic acceptance/rejection, duplicate/session/epoch handling and bounded retention cases.
- [ ] Deliver the scoped offline debug conformance checks for marker links and separately bounded clock/map/match fixtures, preserving current audit coverage.
- [ ] Collect reproducible local build/check commands, pinned compatible revisions/dependencies/fixtures, bounded memory/queues, success/failure cases and correlation/timestamp evidence across the S1 contributions.
- [ ] Record human acceptance of the shared S1 evidence and release S2.

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
