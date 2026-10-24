# Overview and terminology

[Documentation home](../README.md)

## Scope and status

**Agreed design.** Motion Tennis supports one to four players using ESP32 handheld controllers and active Kinect v2 skeleton tracking. A Raspberry Pi calculates physics; a PC stores the committed ball state and visualizes the scene. The project focuses on observable distributed real-time behavior.

The demonstrator should let an operator connect a visible movement or feedback event to its sensor samples, network transaction, skeleton frame, ball-state snapshot, and latency record. A miss is a valid gameplay decision. Missing tracking, invalid data, and communication errors are separate outcomes.

**Implemented at inspection:** repository scaffolding only. This documentation adds specifications and a documentation checker, not firmware, networking, pose estimation, physics, or rendering. There are no selected frameworks or package versions to install yet.

## Inspection evidence

Inspection date: 2026-10-24. Each repository had exactly `README.md` and `LICENSE` tracked, no uncommitted changes, no `AGENTS.md`, no application source, and no dependency, build, test, or workflow files. Parent directories contained no applicable `AGENTS.md`. Each checked-out `main` tracks `origin/main`, with `origin/HEAD` pointing to `origin/main`. These observations concern local checkouts; no remote availability or new upstream commits were checked.

| Repository | Inspected commit | Original README | License attribution |
| --- | --- | --- | --- |
| `documentation` | `440112e` | Title and `test` | MIT, Motion Tennis Group, 2026 |
| `motion-tennis-camera-tracking` | `d313246` | Repository name | MIT, Viktor Hofer, 2026 |
| `motion-tennis-game-engine` | `56fc310` | Repository name | MIT, Viktor Hofer, 2026 |
| `motion-tennis-physics-engine` | `85e4721` | `New Readme` | MIT, Viktor Hofer, 2026 |
| `motion-tennis-controller` | `5b4e572` | Repository name | MIT, Viktor Hofer, 2026 |

The [repository map](../README.md#repositories-and-roles) uses the real `git@github.com:motion-tennis/<repository>.git` remotes. Existing license files must remain unchanged.

## Goals and boundaries

- Make latency, jitter, scheduling, queueing, stale inputs, loss, and clock uncertainty observable.
- Preserve a complete controller-to-physics-to-game query transaction, with matching controller feedback.
- Combine body/joint tracking with controller measurements for player and racket movement.
- Evaluate one through four active controllers under reproducible network and CPU/rendering loads.
- Provide a simple scene and diagnostic UI that expose event identity and state freshness.

**Outside the initial scope:** competitive tennis simulation, polished artwork, internet matchmaking, and implementing entire subsystems as part of this documentation change. Transport security for networks outside a controlled laboratory is an open deployment decision; Wi-Fi membership alone is not application authentication.

## Terminology

| Term | Meaning |
| --- | --- |
| Controller | ESP32 handheld with IMU, LED, and motor; never the Raspberry Pi |
| Physics component | Software on the Raspberry Pi that computes all proposed ball changes |
| Game engine | PC component that stores committed snapshots and renders them; no framework selected |
| Tracking service | Software producing continuous Kinect-derived skeleton frames |
| Transaction | One controller measurement request through its matching application result |
| Application response time | `tr - t0`, measured by the same controller clock |
| Electrical feedback time | `t1 - t0`, ending at the defined output activation boundary |
| Capture time | Timestamp for a sensor acquisition boundary, whose meaning must be documented by the adapter |
| Arrival time | Local receipt timestamp at a component; does not replace capture time |
| Simulation tick | Logical physics time index, distinct from host wall time and state version |
| State version | Monotonically increasing committed revision within a game session |
| State owner | Game component holding the single committed ball snapshot |
| State writer | Physics component calculating and proposing changes to that snapshot |
| Association | Explicit binding between a controller session and a tracked person |
| Calibration | Versioned mapping between sensor, body, controller, racket, and world frames |
| Deadline miss | An outcome exceeding a declared target; timeouts are also reported separately |

## Reading design claims

Every page uses **Implemented**, **Agreed design**, **Proposed**, and **Open** as defined on the [home page](../README.md#status-vocabulary). Agreed choices are recorded separately from proposed mechanisms in the [ADRs](adr/README.md). Proposed interfaces are consistent enough to review and implement, but their presence in Markdown is not evidence of interoperability.
