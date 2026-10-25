# Shared project stages

[Documentation home](../README.md) · [Current stage and evidence](project-status.md) · [Task and handoff workflow](contribution-workflow.md) · [Open decisions](roadmap.md)

This is the common delivery sequence for all six repositories. Contributors work on bounded tasks within a stage, review their evidence, and integrate that stage before expanding the project. The detailed specifications describe the destination; they are not an instruction to implement every feature in one task.

The [status ledger](project-status.md) is the single authority for the active stage and accepted gates. This document defines stages, not their completion. Each repository's `docs/orientation.md` explains its role; `docs/workflow.md` translates these stages into local deliverables. The working plan introduces no dates, staffing assumptions, branch protection or CI enforcement.

## Stage sequence and acceptance gates

| Stage | Bounded outcome | Evidence required to accept the shared gate | Deliberately later |
| --- | --- | --- | --- |
| **S0 — Shared baseline** | Agree component boundaries, this workflow, trace/clock/marker contracts and the versioned doubles wire contract. Define fixtures, resource limits and the testable S1 slices. | Reviewed schema/profile versions and hashes; full roster/avatar/serve/score query/commit/publication contract; generated-codec contract fixtures and worst-case encoded-size/resource checks; compatible producer/consumer expectations; every repo has orientation and staged workflow. Resolve or explicitly version any contract-blocking open decision. | New firmware/services, live networking and gameplay implementation. Small contract validation tools/fixtures are in scope when explicitly tasked. Documentation alone does not pass this gate. |
| **S1 — Isolated component slices** | Build the smallest testable part of each component using controlled inputs: local controller acquisition/output, tracking adapter fixtures, deterministic Pi core, headless state store and offline trace conformance. | Reproducible local build/check commands, pinned dependencies where used, contract-compatible input/output fixtures, bounded memory/queues, success and failure cases and emitted correlation/timestamp records. Mocks and real hardware evidence are distinguished. | Live end-to-end integration, complete doubles rules, live viewer and polished rendering. |
| **S2 — Device and transport feasibility** | Prove the actual devices and isolated links: Windows four-person tracking; Pi/state synthetic capacity; one battery controller with WLAN, marker IRQ and safe outputs; Pi-reference drift/uncertainty mapping; bounded collection. | Actual device/version manifests; measured capture/sample/timestamp behavior; nominal 800 transaction/s Pi/state probe with atomic ordering and overload outcomes; clock-bound/asymmetry/restart evidence; shared-INT attribution and unchanged sampling; topology/control/debug reachability pilot. | A playable integrated match, four-controller human trials and final WLAN performance conclusions. |
| **S3 — One-controller integration** | Connect one real controller, real tracking, Pi processing and PC state service as a diagnostic fixture. Provide a usable trace timeline with visible time uncertainty. | Trace a regular sample through pose selection, required `ball_state_request`/`ball_state_response`, calculation, accepted atomic commit, matching response and eligible electrical feedback. Verify explicit trigger links, same-ESP timing, map versions, invalid/expired mappings, hits/misses, faults, loss and unresolved commits. Record missing evidence rather than filling gaps. | Full four-human doubles, final performance acceptance and visual polish. One controller is not a normal match. |
| **S4 — Playable four-player doubles** | Integrate four confirmed A1/A2/B1/B2 players, automatic avatar movement, gesture toss/overhead serve, normal tennis scoring and two elevated rear team views. | Deterministic serve/let/fault/scoring/side-change and assignment fixtures plus a real four-player functional run. Pi alone calculates complete match changes; both PC views consume one committed state. Demonstrate pause/rebind/recovery and traced rule/score events. | Acceptance-grade timing claims, topology winner, advanced assets, alternate game modes and true 3D. |
| **S5 — Measurement and hardening** | Evaluate the complete system and repair observed faults within the agreed design. Compare external AP (A) and Pi hotspot (B) under matched conditions. | The [test matrix](testing.md): three 10-minute baseline trials for each controller count 1–4 per variant, declared warmup, matched load/fault trials, complete denominators, loss/censoring, clock bounds, marker evidence and separate response/electrical metrics. Evaluate the agreed-for-run targets and publish failures as well as passes. Record the deployment decision. | Unmeasured performance promises, sample-rate reduction as a hidden optimization or hardware/radio redesign without a recorded decision. |
| **S6 — Reproducible demonstrator** | Package the proven configuration so another contributor can build, start, pair, diagnose and reproduce it. | Pinned revisions of all repos, schema/profile hashes, dependencies/devices, real setup/build/run commands, startup/recovery/shutdown instructions and a successful independent reproduction with evidence. Preserve limitations and failed cases. | Automatic expansion of the project after the demonstrator is complete. |
| **S7 — Deferred extensions** | Separately scoped true 3D, measured hardware/model/radio changes or other approved extensions. | A new explicit scope decision, updated ADR/profile/contracts and extension-specific accuracy, compatibility and timing evidence. | Starting this work merely because S6 passed. S7 is a parking area, not an automatically released next stage. |

All performance numbers remain proposed reference targets until accepted for a run and measured. A test failure requires a correction or a visible, reviewed change to the criterion; it cannot be made a pass by silently weakening the profile. Full-match wire evolution must preserve the agreed continuous controller stream and independent diagnostic marker semantics.

## Parallel work and dependencies

At S0, component contributors review their own side of the shared contracts in parallel. At S1, local slices can proceed independently against the same pinned fixtures. At S2, camera, controller and Pi/state feasibility are parallel work lanes; clock and diagnostic work accompanies them. Missing hardware can block one lane while another proceeds within the active stage. A blocked item is not a passed gate.

S3 starts only after the shared S2 gate is accepted. This brings basic trace emission into S1, collection into S2 and the trace viewer into S3, so integration has evidence from its first transactions. S4 adds full game behavior only after the diagnostic path works. S5 measures that integrated behavior; S6 documents a configuration that has actually been reproduced.

The S2 topology pilot checks feasibility and reachability; it does not replace the matched S5 comparison. Likewise, an S2 synthetic 800 transaction/s test does not establish S5 wireless four-player latency. One-to-three-controller runs remain diagnostic workloads throughout the plan.

## Shared definition of done

For each task, attach the implementation or documentation diff, exact repository/dependency revisions, checks performed, results and known gaps. Check at least one relevant failure case for behavior-changing work. Use existing focused checks for low-impact documentation changes; do not invent tests merely to mirror an edit.

For a stage gate, reconcile all repository contributions and their integration evidence in [project status](project-status.md). Required contributions need reproducible evidence; a repository with no new work at a gate may be explicitly marked not applicable with a reason. A component passing its local tests does not release the next shared stage.

A responsible human records acceptance, evidence and the next active stage in the central ledger. An explicitly authorized agent may record that decision on their behalf; passing its own tests is not authorization to release itself. A human task can authorize a named, bounded later-stage exception, which is recorded in the task/handoff without advancing the global stage. Routine decisions and fixes inside an authorized task do not require another permission request. See the [contribution workflow](contribution-workflow.md).

## Migration from earlier roadmap labels

The former M0–M6 labels remain understandable in historical records, but new tasks use S0–S7. There is one delivery sequence, not two competing schedules.

| Previous work package | Current placement |
| --- | --- |
| M0 shared baseline | S0 contract baseline; S1 component conformance |
| M1a camera, M1b Pi/state, M1c handheld feasibility | S1 minimal local foundations; S2 measured feasibility |
| M1d shared time | S0 contract; S1 synthetic mapping/conformance; S2 real clock evidence; S3 integrated visibility |
| M1e doubles contract and rules | S0 versioned contract and fixture definitions; S4 complete rule implementation and game acceptance |
| M2 one-controller integration | S3 |
| M3 debug environment | S1 offline conformance; S2 collector; S3 usable timeline; S4 match traces; S5 full replay/fault evaluation |
| M4 four-player evaluation | S4 playable functional gate; S5 matched evaluation |
| M5 reproducible demonstrator | S6 |
| M6 true 3D | S7, deferred |
