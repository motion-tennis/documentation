# Project status and stage ledger

[Documentation home](../README.md) · [Stage definitions](project-stages.md) · [Contribution workflow](contribution-workflow.md)

**Active stage: S0 — Shared baseline.**

**Last evidence review: 2026-10-25.** The current request establishes orientation and staged delivery documentation. It does not release runtime implementation. No shared stage gate has yet been accepted. S0 remains open because the existing ball-only wire schema does not encode the selected full doubles game and the contract/resource checks are not complete.

This is the sole mutable stage ledger. Component guides link here rather than maintaining separate active-stage flags. Record the exact documentation revision read in each task. A pinned status snapshot supplied with an authorized task is acceptable for an isolated/offline checkout; a stale link or memory is not evidence of a later stage release.

## Stage state

| Stage | State | Evidence / missing gate |
| --- | --- | --- |
| S0 | Active, incomplete | Orientation, workflow, specifications and existing offline checks available. Versioned complete-match schema/profile, codec/resource proof and cross-component acceptance still required. |
| S1 | Not released | Needs accepted S0 and bounded local implementation tasks. |
| S2 | Not released | Needs accepted S1 and actual device/transport feasibility evidence. |
| S3 | Not released | Needs accepted S2; no live end-to-end path exists. |
| S4 | Not released | Needs accepted S3; no playable doubles implementation exists. |
| S5 | Not released | Needs accepted S4; no measured WLAN comparison or system acceptance runs exist. |
| S6 | Not released | Needs accepted S5 and an independently reproducible configuration. |
| S7 | Deferred | Requires a separate extension decision; S6 acceptance does not release it. |

## Repository evidence at this review

| Repository | Implemented artifacts | Next bounded S0 contribution |
| --- | --- | --- |
| documentation | Architecture/specification documents, proposed ball-only schema and reference profile, documentation checker, orientation/workflow | Specify and review the versioned complete-match contract; resolve blocking wire/trace decisions and define conformance fixtures/resource limits. |
| motion-tennis-controller | Documentation and license; no firmware/build setup | Review controller-facing sample/result/control contracts, selected MPU-6050/Zephyr boundaries and the local acquisition acceptance checklist. |
| motion-tennis-camera-tracking | Documentation and license; no capture/inference runtime | Review pose identity, timestamp/quality/calibration contract and recorded-input fixture requirements. |
| motion-tennis-physics-engine | Documentation and license; no fusion/simulation service | Review complete-state query/commit semantics, ordering, periodic work, time maps and deterministic input/output fixture requirements. |
| motion-tennis-game-engine | Documentation and license; no state service or renderer | Review full-match snapshot/atomic commit/publication and the producer/consumer contract with physics; define headless store cases. |
| debug-units | Offline trace checker, synthetic fixture and nine unit tests, plus documentation | Review trace coverage and planned marker/clock/match fixtures. Existing checks do not implement the collector, viewer or new marker/clock semantics. |

This table records evidence, not person assignments. Claim a task and its file scope through the existing human coordination channel or review system using the [task template](contribution-workflow.md#task-brief). Do not invent contributor names, deadlines or tickets.

## Active gate checklist

**Checklist stage: S0.**

- [x] A common stage sequence, local orientation/workflow and agent entry instructions exist in all six repositories.
- [ ] Review the versioned roster/avatar/serve/score extension with both physics and game consumers and the diagnostic contract. Current `motion.proto` and `reference-profile.json` are not a completed doubles baseline.
- [ ] Pin compatible schema/profile revisions and hashes, define fixtures and verify maximum encoded messages and resource bounds, including the eight-query batch and the complete match state. Resolve any size conflict explicitly through the contract process.
- [ ] Resolve stage-blocking open decisions or record versioned assumptions and their later measurement gates; proposed numerical targets must stay visibly proposed.
- [ ] Collect component contract reviews and define the first bounded S1 tasks, their dependencies and acceptance evidence.
- [ ] Record human acceptance of S0 and release S1. This planning edit does not supply that acceptance.

## Gate decision record

No stage acceptance decisions have been recorded. On acceptance, append a record here and update the stage table and active-stage line together. Use:

```text
Stage reviewed:
Decision: accepted / changes required
Decision date and responsible human:
Documentation revision and schema/profile hashes:
Repository revisions and evidence links:
Required gate criteria and their results:
Open limitations and explicitly justified not-applicable contributions:
Next released stage (if accepted):
```

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
