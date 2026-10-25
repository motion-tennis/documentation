# Implementation work packages and remaining decisions

[Documentation home](../README.md) · [Master plan](master-plan.md) · [ADRs](adr/README.md)

The reference is concrete enough to divide work without inventing running software. Hardware availability and webcam/2.5D/wireless direction are confirmed; component implementations and measured timing remain absent. [ADR 0008](adr/0008-mpu6050-zephyr-prototype.md) fixes MPU-6050 over I²C with Zephyr for the first prototype. Exact board/breakout, dependency versions and measured marker feasibility remain open. Dates and staffing are not invented.

## Delivery order

The [shared S0–S7 stages](project-stages.md) are the single development sequence. Read [current project status](project-status.md) before selecting work and use the [task/handoff workflow](contribution-workflow.md). Every repository has a local orientation and stage workflow. The former M0–M6 work packages are mapped to the new sequence in the [migration table](project-stages.md#migration-from-earlier-roadmap-labels); they are not a second schedule.

S0 establishes contracts, S1 builds isolated slices, S2 proves hardware and transports, S3 integrates one diagnostic controller, S4 delivers playable doubles, S5 measures and hardens the whole system, and S6 makes it reproducible. S7 holds separately authorized extensions. Local completion does not automatically advance the global stage.

Wi-Fi remains selected for near-term work. Use the [external-AP/Pi-hotspot comparison](networking.md#external-ap-versus-pi-hotspot-comparison): A is the initial baseline, B is a feasibility/evaluation candidate, and the laptop stays wired in both. S2 contains the reachability pilot; S5 contains the matched comparison with identical 200 Hz streams, protocol, marker behavior and workload. ESP-NOW is deferred outside this work package.

## Concrete component backlog

These are eventual capabilities across multiple stages, not a task to implement in one pass. Select only the slice allowed by the central stage and the repository workflow.

- **Controller:** board/power design; [selected MPU-6050/I²C prototype](imu-selection.md) with pinned Zephyr/HAL/driver; explicit DLPF/divider initialization and readback; motion-trigger extension and shared-INT source attribution; regular-sample ISR/clock/session IDs; early threshold capture and explicit trace links; bounded UDP/control codec, pending table, association installation ACK, semantic cue scheduler, trace exporter and physical test points. Preserve the continuous gameplay stream.
- **Tracking:** Media Foundation adapter and rectification, latest-frame handoff, pinned RTMO-m/ORT GPU manifest, identity association, per-person publication, clock/uncertainty characterization and pairing diagnostics.
- **Physics:** native receiver, Pi-reference clock coordinator with offset/drift estimation and versioned uncertainty records, IMU/pose histories, delayed fusion, calibrated plane mapping, swing/contact state machines, single batch writer, query/commit recovery, fixed-step simulation and buffered trace integration.
- **Game:** native snapshot/commit service, persistent-for-session dedup cache, control/readiness/reset handling, separate minimal SDL3 renderer, state/pose diagnostics and presentation markers.
- **Debug:** runtime emitters/collector, source registry, protobuf packet decoding and pcap joining, timeline/UI/reporting, virtual controllers/poses/game, deterministic replay, packet/message fault injector and evidence bundles. Display the runtime's Pi-reference mapping versions, offset/drift, age/status and uncertainty bands; retain unmapped local lanes and test overlapping intervals. Add marker/link integrity checks and separate trigger-to-response/swing/cue reporting under the [marker contract](imu-trigger-markers.md). Offline checker/tests are the only implemented subset; they do not yet audit marker or clock-mapping semantics.
- **Documentation:** pin decisions, review cross-repository schema changes, keep English instructions and exact measured validation status, publish no fake build commands or benchmarks.

## Open decision register

| ID | Remaining decision | Recommended starting point / resolving evidence |
| --- | --- | --- |
| O-01 | Exact webcam and playing distance | Validate actual Facecam generation/mode or alternative at full lane distance; focus/FOV and motion blur gate |
| O-02 | Exact controller board, MPU-6050 breakout, actuator and power parts | MPU-6050/I²C is selected; ESP32-S3 DevKitC + DRV2605L/LRA remain references. Confirm actual parts, I²C/shared-INT wiring, battery/power schematic and ratings; selection does not establish procurement |
| O-03 | Exact OS/kernel/driver and dependency versions | Pi3 64-bit OS Lite; Windows native state/capture plus GPU runtime; pin proven manifests, evaluate PREEMPT_RT |
| O-04 | Model artifact license/checksum and GPU binary compatibility | RTMO-m 640 candidate, no silent CPU fallback; measure four-person tails with renderer active |
| O-05 | Physical station and local-gesture calibration | Fixed physical planes/stations, body-relative wrist/arm scale and reach, neutral heading/drift and residuals; avatar roots move independently; reject unverified true human-depth claims |
| O-06 | Model confidence and dynamic fusion/swing tuning | Replay dataset with labeled faults and motion, not arbitrary interpretation of model score as probability |
| O-07 | Refined physical budgets and thresholds | Start from reference profile; measure30/40/50 ms and data-age gates before accepting or revising |
| O-08 | Battery duration and haptic drive calibration | Actual current/energy and onset tests; no mAh-only runtime promise |
| O-09 | Source authentication and deployment isolation | Controlled dedicated LAN baseline; stronger authenticated profile if trust boundary changes |
| O-10 | Maximum encoded-size and resource proof | Generated codecs/nanopb limits,8-entry worst-case message fixtures, bounded memory/retention pressure |
| O-11 | Debug viewer technology and collection implementation | Follow debug-units module plan and trace-v1; keep rendering/export off critical path |
| O-12 | Hardware/radio/model upgrade decision | Change only the measured bottleneck; faster Pi does not resolve radio nondeterminism or monocular depth |
| O-13 | IMU threshold semantics and detector latency | [Selection study](imu-selection.md): exact 200 Hz sampling, absolute per-axis threshold versus change/magnitude, gravity/filter/duration/rearm settings, measured pre-IRQ and IRQ capture delay |
| O-14 | Pinned Zephyr setup and MPU-6050 driver extension | Zephyr is selected; pin board/Zephyr/driver/HAL versions, verify 200 Hz DLPF/divider setup, implement motion handling and early capture, and validate concurrent sampling/marking with one shared INT |
| O-15 | Marker correlation and event acceptance limits | [Marker contract](imu-trigger-markers.md): validate first-capture-at-or-after link, uncertainty, full path, marker loss, optional swing/cue endpoints and explicit observation cutoff; existing sample targets remain unchanged |
| O-16 | External AP versus Pi hotspot deployment | Run the matched WLAN A/B plan; prove B's interface/address/route and Windows collector reachability, then compare full-path p99/failures, Pi headroom, recovery and setup complexity under unchanged application traffic |
| O-17 | Clock estimator parameters and demonstrated uncertainty | Pi reference, drift correction and visible uncertainty are agreed in [ADR 0009](adr/0009-pi-reference-clock-mapping.md); pin exchange cadence within refresh windows, sample count, fit/filter/window, drift-growth bound and timestamp implementation; validate asymmetry and source/reference restarts against independent evidence |
| O-18 | Doubles tuning and match format | 2v2, automatic movement, overhead gesture serve, normal score and two team views are agreed; tune coverage/speed, local motion scale, shot transfer/assistance and serve windows. Best-of-three sets and horizontal A/B split are proposed defaults |
| O-19 | Versioned full-match wire contract | Extend current ball-only state with roster/avatar/serve/score and rule-event identities; validate atomic query/commit/publication, size/memory limits, rollback, deduplication and clock/assignment provenance before implementation |

## Recording changes

Use an [ADR](adr/README.md) to supersede a reference choice or change protocol semantics. Update schema/profile hashes, component READMEs, debug fixtures and relevant acceptance gates together. A chosen design is not an implemented capability; a successful synthetic test is not a live hardware result. Preserve original licenses and avoid introducing institutional or assumed staffing context.
