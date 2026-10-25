# Working across repositories with people and AI agents

[Documentation home](../README.md) · [Project stages](project-stages.md) · [Current stage](project-status.md) · [Development setup](development.md)

Each task should produce one reviewable result in an identified repository and stage. Split a large milestone into small tasks with explicit inputs, outputs, dependencies and acceptance evidence. The specifications describe eventual behavior; a linked backlog does not authorize implementing all of it.

## Before starting

1. Read the target repository's `AGENTS.md`, `docs/orientation.md` and `docs/workflow.md`. Inspect the actual branch, status, existing code and applicable instructions; preserve other contributors' work.
2. Read [project status](project-status.md) and the relevant [stage gate](project-stages.md). Record the documentation revision and schema/profile versions used. With isolated checkouts, use a pinned, verified snapshot supplied in the task. If status cannot be established, continue useful inspection/planning and obtain the missing baseline before assuming runtime scope.
3. Bound the task using the brief below. If a user already supplied sufficient scope or explicitly authorized a named later-stage slice, use that authorization; do not request it again. Record any stage exception and keep all unrelated later work deferred.
4. Identify the repository/file area being edited and the responsible contributor in the team's existing coordination channel. Avoid overlapping writes; parallel agents should own disjoint paths or separate worktrees/branches as appropriate. A multi-repo contract change needs an explicit list of affected producers and consumers.

There is no assumed task-tracking service or mandatory branch naming scheme. Do not send external messages, create remote issues or push branches merely to satisfy this document without the relevant user authorization.

## Task brief

Copy this into the task or existing issue/review description, replacing the placeholders with actual values. It need not become a new permanent repository file for every small change.

```text
Task / contributor:
Repository and allowed file/component scope:
Stage and central status/documentation revision:
Human-authorized later-stage exception, if any:
One observable outcome:
Required inputs and dependency revisions:
Applicable spec sections and schema/profile versions/hashes:
In scope:
Explicitly deferred:
Acceptance checks and evidence to save:
Handoff consumer and remaining dependencies:
```

A useful S0 example is: “Review the game/physics complete-match query and atomic commit contract; define valid, stale-version and duplicate fixtures; report payload/resource gaps. Do not build either service.” A future S1 controller example is: “Implement local MPU-6050 sampling at the agreed cadence and capture IDs/timestamps using the pinned board/Zephyr configuration; prove measured cadence and bounded output safety. Defer WLAN, threshold-driver integration and gameplay.” The examples define scope, not a release of S1 today.

## Implement and review one slice

Work within the stated outcome and active gate. Prefer a small complete path with fixtures and explicit failures over many unfinished features. Add trace identities, raw timestamp boundaries and loss accounting with the first runtime slice; do not postpone observability until final integration.

When another repository is not ready, use an explicitly labeled contract-compatible fixture or adapter. Record what it substitutes and which claims remain unverified. A mock pass is not an integrated pass, and a successful build is not hardware/timing evidence. Avoid ad hoc message shapes that bypass the canonical schema just to connect a demo.

Keep routine implementation choices, repairs and focused validation inside the already-authorized task. If the task reveals a prerequisite outside its scope, record the dependency, continue unaffected work and request only the missing decision or scope. Do not start the next stage just because the local task is finished.

## Shared contract changes

The `documentation` repository owns the shared contracts; component repositories own their implementations. A contributor can propose a contract change, but cannot silently redefine another component's interface in a local README or codec.

1. Describe the incompatibility, affected producers/consumers, versions, units, identities, limits and failure/recovery semantics centrally. Use an ADR for significant semantic choices.
2. Prepare the schema/profile/trace specification, positive and negative fixtures and encoded-size/resource evidence together. Explicitly identify effects on the unchanged continuous IMU stream, diagnostic markers and clock mappings.
3. Obtain review of both ends of the interface. Record compatible repository revisions and unresolved dependencies; keep old versus new compatibility explicit. Do not claim an unimplemented consumer already supports the extension.
4. Schedule each implementation slice in the appropriate released stage. A contract edit or accepted schema does not itself release all consumers' runtime work.

Use verified repository URLs and revision references in a handoff. `main` links are navigation aids; a reproducibility record pins exact commits/hashes. Do not assume separate repositories commit or merge atomically. For a coordinated change, record the compatible set and integration order; do not run a mixed set as if it had passed validation.

## Review and handoff

The implementing contributor supplies a reviewable diff and results. Review should check scope/stage compliance, contract compatibility, ownership, expected errors and the evidence's limits. A second person or agent can provide technical review; only the recorded human project decision releases a shared stage. Agents may record an explicit human decision on that person's behalf.

```text
Task / stage / scope exception:
Changed repositories and revisions (or clearly marked uncommitted work):
Observable result and affected contracts:
Checks actually run, environment and results:
Fixtures/mocks versus real-device evidence:
Known gaps, blocked dependencies and deferred work:
Next bounded task and consuming repository:
Shared stage gate impact: evidence added / still blocked / ready for human review
```

For documentation-only work, the central documentation checker and focused content/whitespace review are appropriate. For runtime work, add real build/test commands when they exist and link the relevant [acceptance cases](testing.md). Do not claim a planned command was executed. Keep task result, local component readiness and global gate acceptance distinct.

Update [project status](project-status.md) when implementation evidence or a gate decision changes, not merely to advertise an agent starting work. The [roadmap](roadmap.md) is the future backlog and open decision register; it does not replace this workflow or the stage ledger.
