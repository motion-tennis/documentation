# Overview and terminology

[Documentation home](../README.md) · [Master plan](master-plan.md)

## Scope and current direction

Motion Tennis is a multiplayer tennis demonstrator for up to four players, focused on observable distributed processing, latency, data freshness and synchronization. The confirmed reference context is four wireless battery controllers, the available Raspberry Pi 3 Model B, and a Windows laptop with an RTX 5080. Webcam tracking starts with calibrated 2.5D gameplay; true 3D is a later phase.

The agreed game is [2v2 doubles](gameplay.md): humans remain in physical tracking stations while their avatars run automatically. Body-relative hand/arm observations combine with IMU data for racket gestures and overhead serving. The Pi computes ball, avatar, serve/rule and score changes; the game state service stores committed snapshots and answers explicit ball-state requests. Two elevated rear views show the same match from the respective team ends. [Player assignment](player-assignment.md) reuses the existing controller/person confirmation and activation workflow. Rendering and camera inference are separate laptop processes. `debug-units` records and analyzes the chain without becoming part of its synchronous critical path.

The proposed v0.3 full-match contract and its offline host checks establish an interface for those requirements; no working match or renderer is implied. One-to-three-controller runs remain diagnostic integration tests, while a normal match requires four confirmed players.

**Implemented:** documentation, schema/profile design files, a documentation checker, and an offline debug trace checker with synthetic tests. No real controller firmware, tracking pipeline, physics service or game state/renderer is implemented. **Agreed design:** hardware context, webcam/2.5D direction and [MPU-6050 over I²C with Zephyr for the first prototype](adr/0008-mpu6050-zephyr-prototype.md). Remaining reference stack choices, timing limits and algorithms are **Proposed**; the chosen prototype still requires implementation and validation. See [status vocabulary](../README.md#status-vocabulary).

## Repository inspection evidence

The first documentation phase inspected five repositories containing only `README.md` and `LICENSE`. The later masterplan inspection found `documentation` committed at `98e43f5` (`Structure`), four component READMEs still carrying existing uncommitted documentation changes, and a new clean `debug-units` checkout at `4ec9ed1`. Those existing changes were preserved. All six `origin` remotes are under `git@github.com:motion-tennis/` and observed `main` branches track `origin/main` with `origin/HEAD -> origin/main`; remote availability/new upstream commits were not fetched to infer this.

| Repository | Inspected HEAD for masterplan | License attribution |
| --- | --- | --- |
| `documentation` | `98e43f5` | MIT, Motion Tennis Group, 2026 |
| `motion-tennis-camera-tracking` | `d313246` | MIT, Viktor Hofer, 2026 |
| `motion-tennis-game-engine` | `56fc310` | MIT, Viktor Hofer, 2026 |
| `motion-tennis-physics-engine` | `85e4721` | MIT, Viktor Hofer, 2026 |
| `motion-tennis-controller` | `5b4e572` | MIT, Viktor Hofer, 2026 |
| `debug-units` | `4ec9ed1` | MIT, Motion Tennis Group, 2026 |

The [repository map](../README.md#repositories-and-roles) derives from those remotes. Existing licenses remain unchanged. Historical ADRs explicitly identify the superseded Kinect/Linux and TCP/JSON assumptions rather than silently presenting both as current.

## Terminology

| Term | Meaning |
| --- | --- |
| Measurement transaction | One controller IMU boundary, `t0`, unique session/request key and terminal result/failure |
| Batch | Up to eight logical transactions sharing a required state query/response snapshot and one atomic commit; never a replacement for individual IDs |
| Application response time | `tr - t0`, same ESP32 timer; includes query/response, batching and commit waiting |
| Electrical cue time | `t1 - t0` for an explicitly eligible output; noneligible samples have no invented `t1` |
| Capture / arrival / completion | Separate sensor acquisition, receiver receipt and processing events, each with its own clock domain |
| Simulation tick | Logical fixed-step physics time, distinct from clock time and commit version |
| State owner / writer | Windows game service owns committed state; Pi physics calculates and proposes all changes |
| Event identity | Game session, writer epoch, batch ID and event index |
| Association | Explicit versioned controller-session to tracker-session/person/hand/lane binding |
| Calibration | Versioned camera, plane, sensor, grip, racket and world transformations |
| 2.5D | Declared plane/lane constraint used to estimate motion; not measured free-space metric depth |
| Deadline-aware service | Measured timing targets with explicit expiry/failure handling; not proof of hard real-time bounds |
| Trace | Source-clock event records joined by transaction and batch identity; complementary to packet capture and electrical evidence |

A miss is a valid no-collision decision. Missing tracking, invalid geometry, overload, stale state and communication failure are separate outcomes. A completed missed swing may emit one cue while ordinary no-contact samples remain noneligible. No measurement may disappear because it made the latency distribution look worse.

## Scope boundaries

Prioritize traceable behavior, four-player identity, temporal alignment, consistency and measurable feedback. No photorealistic artwork, full competitive tennis rules, internet multiplayer or proven worst-case wireless guarantee is part of this first profile. Retain a realistic extension path to true 3D and improved hardware without presenting those extensions as already working.
