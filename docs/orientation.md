# Documentation repository orientation

[Documentation home](../README.md) · [Local workflow](workflow.md) · [Current project stage](project-status.md)

## Responsibility and boundaries

This repository is the shared context for people and AI agents working in the six Motion Tennis repositories. It owns architecture, requirements, interface/time/measurement contracts, ADRs, stage definitions and the central evidence ledger. It defines compatible behavior; firmware, tracking, simulation, state service/rendering and diagnostic runtimes belong in their component repositories.

The full system uses four continuously sampling ESP32 controllers, Windows webcam tracking, a Raspberry Pi 3 B for fusion and sole match-state calculation, and a Windows committed-state service plus two team views. `debug-units` correlates their evidence. The required Pi-to-PC ball-state request/response stays in every applicable transaction; the independent IMU IRQ is a trace marker and never an extra gameplay sample. Pi-reference time maps correct offset/drift and expose uncertainty. See [architecture](architecture.md) and [master plan](master-plan.md).

## Read first

1. [AGENTS.md](../AGENTS.md), [project status](project-status.md), [shared stages](project-stages.md) and this repository's [workflow](workflow.md).
2. [Contribution workflow and task template](contribution-workflow.md), then the [master plan](master-plan.md) and [requirements](requirements.md).
3. The contract sections relevant to the task: [protocol](protocol.md), [physics consistency](physics.md), [coordinates/time](coordinates-and-time.md), [markers](imu-trigger-markers.md), [gameplay](gameplay.md) and [assignment](player-assignment.md).
4. [Test matrix](testing.md), [open decisions](roadmap.md), [ADRs](adr/README.md) and the affected component guides.

Do not copy every specification into every task. Pin the shared revision and link the sections needed for the assigned slice.

## Files and current implementation

| Location | Purpose / evidence |
| --- | --- |
| `docs/` | Shared designs, stage/status/workflow guidance and recorded validation; design text is not runtime proof. |
| `spec/motion.proto` | Existing proposed ball-only wire schema. Full doubles state needs a reviewed versioned extension before runtime implementation. |
| `spec/reference-profile.json` | Existing reference values and selected hardware metadata; numerical targets are unmeasured. |
| `scripts/check_docs.py` | Implemented local Markdown/link, JSON/profile and basic Mermaid structure checker. |
| `scripts/render_progress.py`, `assets/project-progress.svg` | Generate the README progress view from the central ledger; the documentation checker detects stale views. See [dashboard updates](project-status.md#updating-the-readme-dashboard). |
| `docs/validation.md` | Historical checks and explicit validation limitations. |

No game or device runtime is implemented here. The only current runtime-adjacent tool outside this repository is the offline trace auditor in `debug-units`. Inspect [project status](project-status.md) and current source before updating implementation claims.

## Available checks

From this repository, with Python 3.9+:

```sh
python3 scripts/check_docs.py
git diff --check
```

The checker inspects available sibling repositories. Missing siblings are skips, not verified remote content. Check new untracked files separately for UTF-8, trailing whitespace and final newlines. Link/structure success is not Protobuf compatibility, Mermaid rendering, game behavior or hardware/timing validation.

## First bounded work

Consult the active stage instead of choosing an entire component backlog. The remaining S0 work is the reviewed complete-match contract, compatible fixture/resource definitions and component contract reviews. The next task can address one producer/consumer boundary and list its unresolved decisions; it should not implement all consumers. Use the [shared brief and handoff](contribution-workflow.md).
