# Project status and stage ledger

[Documentation home](../README.md) · [Stage definitions](project-stages.md) · [Contribution workflow](contribution-workflow.md)

**Active stage: S0 — Shared baseline.**

**Last evidence review: 2026-10-26.** The [technical S0 baseline](s0-baseline.md) now contains the proposed v0.3 full-match schema/profile, generated Python/C host-codec evidence, bounded-resource calculations, offline semantic fixtures and all five component reviews/S1 handoffs. No shared stage gate has yet been accepted. S0 remains open for human acceptance of this exact baseline and its versioned assumptions; S1 is not released. No device or gameplay runtime was added.

This is the sole mutable stage ledger. Component guides link here rather than maintaining separate active-stage flags. Record the exact documentation revision read in each task. A pinned status snapshot supplied with an authorized task is acceptable for an isolated/offline checkout; a stale link or memory is not evidence of a later stage release.

## Stage state

| Stage | State | Evidence / missing gate |
| --- | --- | --- |
| S0 | Active, incomplete | Technical evidence prepared: versioned full-match schema/profile, generated host-codec/size/resource checks and component reviews. Human adoption/acceptance remains pending. |
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
| documentation | Proposed v0.3 full-match schema/profile, generated host codecs, offline semantic oracle/fixtures, resource evidence, documentation/freshness checkers | Present [S0 evidence](s0-baseline.md), ADR 0011 and versioned assumptions for human acceptance. |
| motion-tennis-controller | Documentation, contract review and S1 acquisition handoff; no firmware/build setup | Review supplied boundary/acceptance evidence; actual board/pins remain prerequisites for its S1 slice. |
| motion-tennis-camera-tracking | Documentation, contract review and recorded-input S1 handoff; no capture/inference runtime | Review supplied pose identity, timestamp/quality/calibration and fixture acceptance cases. |
| motion-tennis-physics-engine | Documentation, producer-side contract review and deterministic S1 core handoff; no runtime service | Review the complete-state, ordering, periodic work, rollback and state-stream contract evidence. |
| motion-tennis-game-engine | Documentation, consumer-side contract review and headless S1 store handoff; no service or renderer | Review the full-match snapshot/atomic commit/publication and duplicate/recovery evidence. |
| debug-units | Existing offline trace checker, synthetic fixture and nine tests; full-match trace specification, contract review and S1 handoff | Existing checks remain reproducible; implement the broader planned marker/map/match audit only after S1 release. |

This table records evidence, not person assignments. Claim a task and its file scope through the existing human coordination channel or review system using the [task template](contribution-workflow.md#task-brief). Do not invent contributor names, deadlines or tickets.

## Active gate checklist

**Checklist stage: S0.**

- [x] A common stage sequence, local orientation/workflow and agent entry instructions exist in all six repositories.
- [x] Specify and technically review the versioned roster/avatar/serve/score extension with physics/game producer and consumer boundaries and the diagnostic contract; v0.3 source and review findings are in the S0 baseline.
- [x] Pin compatible schema/profile and validation-source hashes, define fixtures and verify generated host-codec maximum encodings and contract-storage bounds, including eight-query/full-match cases. ADR 0011 explicitly resolves the state-message size conflict.
- [x] Record stage-blocking interface decisions as the proposed v0.3 baseline and versioned assumptions with later measurement gates; numerical performance targets remain proposed.
- [x] Collect all five component technical reviews and define bounded first S1 tasks, dependencies and acceptance evidence.
- [ ] Record human acceptance of the S0 baseline, ADR 0011 and documented assumptions; then release S1.

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
