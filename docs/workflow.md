# Documentation repository workflow

[Orientation](orientation.md) · [Shared stages](project-stages.md) · [Current stage](project-status.md) · [Task and handoff workflow](contribution-workflow.md)

The central stage ledger defines what is released. This guide allocates documentation responsibilities within each gate; it does not maintain another schedule or authorize future work. Start with the shared task brief, pin relevant revisions, make one reviewable change and attach evidence before choosing another task.

| Stage | Local deliverable | Local review evidence | Deferred boundary |
| --- | --- | --- | --- |
| S0 | Repo orientation/workflows, central ledger, versioned doubles contract/profile, fixture/resource definitions and interface reviews. | Documentation checks; both producer and consumer reviews; exact hashes; codec/size/resource results when implemented under a contract-validation task; unresolved decisions visible. | Runtime implementation in component repositories and claims that current ball-only artifacts already support doubles. |
| S1 | Keep approved contracts aligned with the first isolated component slices; record actual build/check entry points and fixture coverage. | Source-backed implementation labels, compatible fixture revisions and local results linked from component handoffs. | Documenting planned executables as existing; integrating every component in one task. |
| S2 | Record device/toolchain/model manifests, timestamp semantics, topology reachability and feasibility results. | Reproducible Pi/state, controller, camera and clock evidence; failed gates and unmeasured assumptions retained. | Declaring integrated gameplay or a winning WLAN topology from isolated probes. |
| S3 | Turn the implemented one-controller path into a diagnostic startup/recovery guide; document trace/viewer coverage and gaps. | Reproduction of the complete transaction and failure cases with immutable time-map and marker provenance. | Calling a single-controller fixture full doubles or publishing final latency conclusions. |
| S4 | Align rules, assignments, match contract and two-view documentation with the implemented four-player game. | Functional four-player evidence plus deterministic scoring/serve/assignment cases and same-state view checks. | New modes, advanced graphics, final performance acceptance or true 3D. |
| S5 | Publish matched experiment procedures/results and the evidence-based AP/hotspot deployment decision. | Full run manifests, denominators, failures, distributions, uncertainty and raw evidence references; no invented measurements. | Silently revising targets to make runs pass or hiding fault runs. |
| S6 | Freeze a reproducible demonstrator guide and compatible six-repo revision set. | Another contributor's successful build/start/pair/diagnose/reproduce record, with remaining limitations. | Automatically releasing extensions. |
| S7 | For an explicitly released extension, update ADRs/contracts/profile and new acceptance criteria. | Separate scope decision and extension-specific results. | Treating the future backlog as permission to implement it. |

Run the [available checks](orientation.md#available-checks) and inspect affected component links after edits. Use [validation records](validation.md) for completed checks and [project status](project-status.md) for current implementation/gate evidence; do not overwrite historical results with present-day claims.

When a contract changes, use the [shared contract workflow](contribution-workflow.md#shared-contract-changes). Record the affected producers/consumers and compatible revisions. Update the central status only when evidence changes or a human stage decision has been authorized; ordinary task completion does not advance the project.
