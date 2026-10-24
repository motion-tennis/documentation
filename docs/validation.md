# Masterplan validation record

[Documentation home](../README.md) · [Inspection evidence](overview.md#repository-inspection-evidence) · [Runtime acceptance plan](testing.md)

Date: 2026-10-24. Scope: coordinated masterplan changes across six accessible repositories, plus a small offline trace-audit implementation in `debug-units`. This record concerns static documentation and synthetic tool validation, not hardware acceptance.

The documentation checkout started this revision clean at `98e43f5`; four component READMEs already contained uncommitted work from the preceding documentation phase and were preserved/updated. `debug-units` started at `4ec9ed1` with README/license only. No commits, pushes, repository-settings changes, procurement or deployments were performed in this revision. Existing licenses remain unchanged.

## Reviewed changes

| Repository | Result |
| --- | --- |
| documentation | English master plan, reference hardware, explicit budgets and fusion, coordinated UDP/Protobuf design/schema/profile, six-repository debug/integration plan, updated instructions and superseding ADR |
| camera tracking | Windows webcam/RTMO reference, rectification ownership, four-person identity, 2.5D geometry and true 3D migration, exact hardware/runtime feasibility gates |
| controller | Proposed battery ESP32-S3/BMI270 stack, 200 Hz transactions, bounded pending/outputs, semantic cues and local timing |
| physics | Confirmed Pi 3 B target, native delayed-pose fusion, ordered atomic batches with logical queries, staged gameplay state, pause/recovery |
| game engine | Windows native state-service/SDL3 renderer separation, versioned ownership, batch query/commit and independent visual timing |
| debug-units | Runnable offline trace auditor, normalized trace-v1, synthetic four-controller fixture, integrity tests, future collector/viewer/replay/fault plan |

Earlier Kinect/Linux and TCP/JSON assumptions are preserved only in explicitly historical/superseded ADR context. User-confirmed webcam-first 2.5D, wireless battery operation, Pi 3 B and Windows host take precedence. The required game-state query and response remain in architecture and timing diagrams and per-input query records.

Independent review prompted: post-network freshness checks; atomic staging/rollback of contact/swing/cue state; association installation acknowledgement and retirement of old cues; simulation-time anchors rebased after pause; writer-epoch matching on ball responses; and bounded uint64 wire values to keep varint sizes controlled. Exact generated-code maximum-size checks remain a runtime contract gate.

## Checks executed

| Command/check | Result and scope |
| --- | --- |
| `python3 scripts/check_docs.py` in documentation | Passed across six repositories: local/mapped links, anchors, navigation, JSON/fences, Mermaid block structure, reference-profile capacity/deadline checks and schema presence |
| `python3 scripts/check_docs.py --workspace /tmp` | Passed standalone-documentation mode, with explicit missing-sibling skips |
| `python3 scripts/check_trace.py examples/synthetic-trace.jsonl` in debug-units | Passed trace integrity: 5 starts, 3 responses, 1 timeout, 1 local drop; intentionally includes a response over the 30 ms target |
| `python3 -m unittest discover -s tests -v` in debug-units | Nine tests passed for accounting, mixed clocks, duplicate actuation, missing terminal records, expired responses, sequence gaps, duplicate JSON keys, empty input and unmatched old responses |
| `git diff --check` in each repository | Passed tracked whitespace checks |
| `git diff --exit-code -- LICENSE` in each repository | Passed; existing license contents unchanged |
| UTF-8/final-newline/trailing-whitespace and Python AST inspection | Passed, including new untracked files |
| Invalid-profile experiments | Too-small pending table, oversized payload, per-controller batch exceeding queue and nonfinite JSON were rejected |

The synthetic fixture's timing values are fabricated known-answer inputs. Its 32 ms response intentionally fails the 30 ms target while preserving trace integrity. A zero exit from the trace audit means the trace is internally valid, not that a real game met a performance acceptance gate. Read the report's target/failure fields separately.

## Limits and checks not performed

- No Mermaid renderer/parser is installed; diagrams received structural and manual checks only. Full rendering remains an explicit publishing check.
- No `protoc`, `grpc_tools` or generated protobuf codecs are available here. Schema syntax/fields and bounded wire-size reasoning were reviewed, but compilation, inter-language round trips and maximum-size encoding must run with actual implementation dependencies before interoperability claims.
- No Windows laptop, RTX inference, Pi 3, ESP32, battery, webcam, AP, logic analyzer or physical reference was connected/tested by these changes. No hardware/network/timing benchmark is claimed.
- The live debug collector, packet decoder, viewer, simulator/replay/fault harness and production emitters are designed but not implemented. The offline checker does not prove complete batch correctness or discover an entirely absent expected source without a future source registry.
- Primary-source facts were researched and linked in hardware, networking and tracking-stack pages. External URL reachability, private repository access and remote anchors were not comprehensively tested; local links do not imply unpublished files already exist remotely.
- Python checks ran with the available Python 3.14 interpreter; the declared 3.9 minimum was not separately exercised. Existing gameplay test suites do not exist.

## Remaining gates

Resolve exact procurement/power parts, webcam generation/focus/FOV and lighting, model/GPU compatibility and license manifest, calibration/confidence settings, clock uncertainty, actual Pi/Windows batch capacity and radio tails. Then implement/pin components and the complete runtime debug environment in the [delivery order](roadmap.md). These are observable implementation gates, not hidden assumptions in a claimed perfect real-time system.
