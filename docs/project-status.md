# Project status and stage ledger

[Documentation home](../README.md) · [Stage definitions](project-stages.md) · [Contribution workflow](contribution-workflow.md)

**Active stage: S1 — Isolated component slices.**

**Last evidence review: 2026-11-19.** The project user accepted the [S0 baseline](s0-baseline.md) on 2026-10-26, including the dedicated Pi/PC TCP state channel in ADR 0011. S1 is active. The [current checklist](#active-gate-checklist) records the results of the physics and game regressions and the remaining requirements for S1 acceptance.

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
| motion-tennis-camera-tracking | Offline adapter and bounded trace-v1 exporter at `5a72519`, with 64 passing Python tests, generated v0.3 codec evidence and completed technical physics/debug handoff review | Camera contribution, pinned commits, tests and resource evidence are included in the [shared S1 review](s1-review.md). No camera-only S1 work remains in this reviewed slice; live capture, inference and transport retain their later gates. |
| motion-tennis-physics-engine | Deterministic batch core and typed tracking bridge. The repair at `08d59a7` prevents one controller transaction from producing multiple contacts and retains the original terminal feedback. | Exercise the common v0.3 game fixture, including explicit rejected-input accounting and emitted query/commit evidence. |
| motion-tennis-game-engine | In-memory C# store with active and completed tiebreak counters validated through the unsigned 56-bit limit. All 16 mock-Pi host checks pass at `a3b6eb6`. | Exercise the common v0.3 physics fixture and retain correlated committed events and diagnostics. |
| debug-units | Delivered offline core, marker, clock-map and pipeline/match-provenance profiles at `84c3c2a`; four synthetic fixtures and 72 passing tests; scoped tracking trace handoff technically reviewed | Complete controller/physics/game exporter-profile adoption and their shared S1 evidence; the exercised tracking profile is recorded in the [shared review](s1-review.md). Live collection and hardware remain later work. |

This table records evidence, not person assignments. Claim a task and its file scope through the existing human coordination channel or review system using the [task template](contribution-workflow.md#task-brief). Do not invent contributor names, deadlines or tickets.

### Local S1 debug evidence — 2026-11-08

The bounded marker-link, clock-map and pipeline/match-provenance slices were implemented on `task/s1-marker-conformance` in `debug-units`, with related documentation and the Windows freshness fix on the same named documentation branch. Bases are debug `62d4cb3` and documentation `3260994`; implementation/review and local commits were complete. The `debug-units/docs/s1-clock-pipeline.md` handoff and exporter review package records the explicit offline profiles, fixtures, exact base revisions and remaining dependencies. At the original 2026-11-08 handoff, public remote publication was blocked by automatic approval review pending explicit push authorization. The user subsequently authorized publication: debug `84c3c2a0289011764980de44575bdb14c7d83376` and the related documentation changes are now on remote `main`, verified again on 2026-11-11. The historical local-only delivery notes describe that earlier handoff, not the current publication state. No stage was released by publication.

All 72 debug tests, ten freshness-checker tests and four synthetic CLI fixtures passed. The Windows S0 freshness failure was repaired using portable path identities and LF/CRLF text handling, with substantive changes and path collisions still rejected. Historical S0 evidence and all contract sources are unchanged. The full local documentation check passes; unavailable component checkouts remain skips. This is synthetic offline evidence, not validated real exports, clock fitting, hardware timing, complete tennis rules or a running game. Producer-owner review and the other component S1 gates remain open.

### S1 tracking evidence — 2026-11-11

The offline recorded/synthetic Python pose adapter is implemented in tracking commit `0509fbd8cc15dd7b5a1a640814b66e890aef1ca3`, prepared on `task/s1-recorded-pose-adapter` from tracking `a7ae1bd` and shared `documentation@e541fd2`. It preserves session/frame/person identities and native timestamps, validates coordinate/quality/calibration and timing evidence, bounds the latest-frame handoff and retains explicit rejection/loss diagnostics. The [pinned component handoff](https://github.com/motion-tennis/motion-tennis-camera-tracking/blob/0509fbd8cc15dd7b5a1a640814b66e890aef1ca3/docs/s1-recorded-pose-adapter.md) records source, fixtures, reproducible commands and evidence. On 2026-11-11, the project user explicitly authorized Codex to commit this slice and push both tracking and documentation to remote `main`; Git commit/ref state records publication separately from validation.

Host validation on 2026-11-11 used Windows and Python 3.14.3: all 47 API/fixture/CLI tests passed. A separate environment with pinned development dependencies passed generated-codec checks for six cases and twenty envelopes, including four-person and maximum-counter cases. The largest exercised encoded envelope was 497 bytes, below the 1200-byte cap. At that initial adapter handoff, the checks established the exercised Python host-codec boundary while Pi/debug fixture and diagnostic-format review and shared S1 acceptance were pending; the subsequent scoped consumer work and technical reviews are recorded below. These initial checks do not establish nanopb/C, target-device or live transport interoperability, and this record does not accept a component or shared stage gate.

The user's report of an available working Xbox Kinect is recorded separately in [hardware evidence](hardware.md#available-kinect-and-evidence-boundary). This slice uses controlled observations and does not establish live capture, inference, body tracking, hardware timing or networking. The webcam-first 2.5D baseline and accepted schema/profile remain unchanged.

### S1 tracking consumer compatibility — 2026-11-11

The user authorized the typed physics pose handoff, bounded trace-v1 exporter, validation fixes and real consumer checks, then explicitly authorized committing, merging and pushing tracking, physics and documentation to remote `main`. The [compatibility handoff](s1-tracking-consumer-compatibility.md) pins tracking `5a72519d0441e88fb359b7f98a57b1f1f2581478`, physics `d6d71436f30a1effd1572b85daaf560ebaf40ba1` and unchanged debug `84c3c2a0289011764980de44575bdb14c7d83376`, together with the original baselines. The work was prepared on `task/s1-tracking-consumer-compatibility`; containing commits and remote refs establish publication. The schema/profile are unchanged. Source hashes and environment in the saved report describe the dated validation snapshot, including its then-uncommitted working-tree state.

All 64 tracking Python tests passed. Generated Python checks passed six cases and twenty envelopes, with a largest exercised size of 497 bytes including the envelope. The actual typed physics bridge/core passed seventeen compatibility cases across five adapter-produced frames and fifteen generated/decoded envelopes; the actual debug auditor passed seven compatibility cases. A deliberate overflow case correctly failed trace completeness: seventy-two lost records matched seventy-two source-sequence gaps and log-drop accounting. These checks use explicit synthetic controller, confirmed-binding and Pi-map fixtures. They establish the exercised offline handoff, not actual clock fitting/accuracy, hardware, live networking, calibrated fusion, target C-codec interoperability or shared S1 acceptance.

The typed bridge now rejects pose-calibration mismatch, invalid or excessively uncertain maps/captures, unavailable required joints, future processing/send boundaries and stale observations, including after state waiting. It preserves raw capture/session/clock and immutable Pi-map provenance, and frame-status/restart fences invalidate unsupported cached poses. Tracking trace export preserves producer sequences before loss and keeps unknown lifecycle timing as explicit untimed metadata. Broader producer-profile adoption and the remaining physics/game/controller contributions stay open.

### Camera contribution to shared S1 review — 2026-11-11

The user requested completion of the physics/debug handoff review and inclusion of camera commits, tests and resource evidence. The [shared S1 review packet](s1-review.md) now records both completed Codex technical receiver reviews, the compatible published revisions and a [fresh consumer report](../evidence/s1-camera-handoff-results.json) captured against clean source checkouts at documentation `0df5399`. The rerun passed 64 tracking tests, seventeen physics cases, seven debug cases and twenty generated envelopes. Separate receiver checks passed all 57 physics checks and all 72 debug tests plus four synthetic CLI fixtures. Host layout measurements, fixed capacities, toolchain/dependency versions and unmeasured target limits are recorded with the camera contribution.

The exercised camera-to-physics and camera-to-debug technical handoffs have no blocking review findings and are complete for S1 controlled fixtures. The generic debug audit must be paired with inspection of tracking completeness/untimed metadata; a tracking-only trace remains insufficient controller measurement evidence. This is an agent technical review authorized by the user, not human acceptance of the shared stage. Other producer adoption and the complete all-component evidence package remain open.

## Course M3 and Mx design reports - 2026-11-17

The course submission is due 19 November 2026 at 23:59 Europe/Vienna. It is separate from the internal S0-S7 implementation stages. On the user's request, the existing M3 design was revised to R5 against the newer M2 F-01-F-21 / NF-01-NF-15 baseline, and a separate Mx R1 integration-debugging concept was prepared. The confirmed team display name is Motion Tennis; report filenames use the established compact MotionTennis token.

- [M3 report source](m3-system-design-integration-tests.md) and [standalone PDF](DRS_M3_MotionTennis.pdf): architecture, transaction/stage budgets, global time, interfaces, twelve integration tests, full requirement traceability and consistency findings.
- [Mx report source](mx-integration-test-debugging-concept.md) and [standalone PDF](DRS_Mx_MotionTennis.pdf): bench, trace points, diagnostic order, verdict classification, reproducibility and proposed role-owned tool readiness dates.
- [Preparation and validation handoff](milestone-report-handoff.md): pinned documentation baseline, generation method, review scope and unresolved acceptance decisions.

On 18 November 2026 the project user confirmed Mx team acceptance, available logic analyzer/oscilloscope/photodiodes and assigned hardware responsibility. Mx R2 records the accepted tool/measurement plan, stopping acquisition with Windows-host loss (post-failure evidence remains incomplete), and initial operating limits set under explicit user authorization. M3 R6 aligns the related test/status text; The project user subsequently confirmed M3 as-is on 18 November 2026. M3 and Mx are accepted and course Gate 2 is complete; R7/R3 record this decision. CR-04/09/10 retain the listed implementation/evidence prerequisites; acceptance is not evidence that hardware tests passed. Exact assembly ratings, calibration, protection implementation and hardware/WCET evidence remain execution prerequisites. The report work makes no implementation-stage transition and does not release S2. No runtime code or other component repository was changed by this reporting task.

## Physics replay and game score regressions — 2026-11-19

The tested changes were committed as physics `08d59a71704f4fe3272a97c3893465f09b87f84e` (base `d6d7143`) and game `a3b6eb6eceae4e27aefaa552c11a4ec2c7ece114` (base `f34c226`). The review used documentation base `afcb301`, controller `8370c26`, tracking `5a72519` and debug `84c3c2a`.

- **Physics.** The same scripted hit, offered again during processing and after commit, produced three contacts on the base and one on the repaired core. The pending replay emitted no early feedback. The completed replay returned the original result, including its event and cue identities. Each bound controller retains its 16 most recent terminal results. Once a result is evicted, packets at or below its retired sequence are declined unless the original key is still pending or retained.
- **Game.** Both new checks failed on the base and passed with the repair. The snapshot API accepted a legal active `100:99` tiebreak and scores at the unsigned 56-bit limit. A completed tiebreak above the limit for either team left the committed snapshot intact. The 16 mock-Pi checks ran on .NET SDK 10.0.401 targeting `net8.0`. The tested Git blob IDs are `5a591ec1ed0749ded4787bbd3e712e52f2788912` for `GameStateStore.cs` and `3c51337419c696c41a5a6b4c999b4ee737df50a3` for the test harness `Program.cs`.

| S1 host check | November 19 result |
| --- | --- |
| Physics Release build and CTest | 26 batch-core checks and 34 tracking-bridge checks passed. |
| Tracking and its two receivers | 64 tracking tests, 20 generated wire envelopes, 17 physics cases and 7 debug cases passed. The [dated consumer report](../evidence/s1-camera-handoff-2026-11-19.json) records the tested source hashes. On Windows x64, `sizeof(BatchCore)` rose from 68,968 to 90,040 bytes. The bridge measured 18,144 bytes and a pose observation 704 bytes. Pi memory headroom still requires a device measurement. |
| Debug auditor | 72 tests passed. All four synthetic CLI traces passed with zero errors. |
| Shared documentation and contract | The documentation checker passed across six repositories, along with 32 match-contract tests and 10 evidence-freshness tests. |

## Active gate checklist

**Checklist stage: S1.**

Checked delivery items establish the named bounded implementation and its local evidence. Cross-component profile adoption, compatible fixture/timestamp evidence and human stage acceptance remain separate requirements below.

- [ ] Deliver the controller's bounded local acquisition and safe-output slice with pinned board/Zephyr/toolchain inputs and explicit synthetic versus device evidence.
- [x] Deliver the tracking recorded-input adapter with identity, timestamp, quality/calibration and invalid-input fixtures. Current `5a72519`: 64 host tests and 20 generated Python codec envelopes passed; physics/debug technical handoff, seventeen physics cases, seven debug cases and resource evidence are included in the [shared S1 review](s1-review.md). The earlier `0509fbd`/47-test result remains historical evidence.
- [x] Deliver the deterministic minimal physics batch core using fake adapters, explicit query/commit correlation, ordered and periodic work, and complete candidate rollback. The local regressions cover replays before and after commit, terminal failures and retention under queue pressure.
- [x] Deliver the headless game state store with a mock Pi writer, atomic acceptance/rejection, duplicate/session/epoch handling and bounded retention cases. The 16 local checks include long active tiebreaks, completed-score bounds and rollback on rejection.
- [x] Deliver the scoped offline debug conformance checks for marker links and separately bounded clock/map/match fixtures, preserving current audit coverage. Verified at `84c3c2a`: 72 tests and all four synthetic CLI fixtures passed.
- [ ] Collect reproducible local build/check commands, pinned compatible revisions/dependencies/fixtures, bounded memory/queues, success/failure cases and correlation/timestamp evidence across the S1 contributions.
- [ ] Record human acceptance of the shared S1 evidence and release S2.

### Remaining S1 work at this review

- **Controller:** the checkout at `8370c26` remains documentation-only. Pin the actual board/pins and Zephyr toolchain, then deliver acquisition, safe-output and failure/overflow evidence under its existing handoff.
- **Physics and game fixture.** Run both components against the same v0.3 configuration and transaction identities. Include a batch where physics removes an ineligible input. Show that the game accepts the surviving decisions and accounts for the rejected input. The current physics fixture uses a placeholder configuration digest and the game fixture uses a typed JSON fingerprint for retries.
- **Trace evidence and review.** Have controller, physics and game emit records that can be joined from sample through query, rejection or commit, publication and feedback. Verify native timestamps, map versions and producer completeness with the offline auditor. Collect compatible component revisions, fixture identities, dependency versions, resource bounds and reproduction commands in the shared S1 review. The [camera handoff](s1-review.md) already provides its controlled-input contribution.
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
