# Implementation work packages and remaining decisions

[Documentation home](../README.md) · [Master plan](master-plan.md) · [ADRs](adr/README.md)

The reference is concrete enough to divide work without inventing running software. Hardware availability and webcam/2.5D/wireless direction are confirmed; component implementations and measured timing remain absent. Dates and staffing are not invented.

## Delivery order

| Gate | Owning repositories | Required deliverable | Exit criterion |
| --- | --- | --- | --- |
| M0: shared baseline | documentation + all components | Profile/schema hashes, trace contract, status labels, fixtures | Documentation checks; contract review; maximum encoded-size validation |
| M1a: camera feasibility | camera tracking + debug | Real Windows capture/model manifest; four-person tracker; calibration dataset | Valid whole-body focus/FOV, GPU provider, sustained pose rate and bounded timestamp uncertainty |
| M1b: Pi/state feasibility | physics + game + debug | Headless synthetic batch producer/state service; baseline scheduler | Ordered atomic commits; nominal800 txn/s capacity gate under Pi3 load |
| M1c: handheld feasibility | controller + debug | One battery board with IMU, driver and explicit timing markers | Safe power/output behavior,200 Hz accounting, local RTT/electrical traces |
| M2: one-player end to end | all six | Real pose fusion plus required state query/commit and feedback | Known hits/misses and all fault paths; no identity ambiguity or silent failures |
| M3: debug environment | debug + instrumented components | Live collector, packet decoder, timeline viewer, run bundles, simulator/replay/fault harness | Source manifest reconciliation, timestamp provenance, bounded log overhead and fault reproduction |
| M4: four-player evaluation | all six | Three10-minute baseline runs at each count and complete fault matrix | Published distributions, ≤1% reference late/failure target, zero correctness/evidence violations |
| M5: reproducible demonstrator | all six | Pinned dependency/build/run manifests, integration startup and diagnostic UI | Another contributor reproduces the documented results |
| M6: true 3D extension | tracking + physics + game | New depth/stereo/multi-view profile and calibration | Verified metric 3D accuracy/identity/time; no guessed z in a 2D schema |

M1a, M1b and M1c can proceed independently after M0. Do not invest in a polished renderer before the camera and Pi 3/state-service gates. Do not claim M3 completed because the offline trace checker exists.

## Concrete component backlog

- **Controller:** board/power design, ESP-IDF manifest, BMI270 adapter, ISR/clock/session IDs, bounded UDP/control codec, pending table, association installation ACK, semantic cue scheduler, trace exporter and physical test points.
- **Tracking:** Media Foundation adapter and rectification, latest-frame handoff, pinned RTMO-m/ORT GPU manifest, identity association, per-person publication, clock/uncertainty characterization and pairing diagnostics.
- **Physics:** native receiver, IMU/pose histories, delayed fusion, calibrated plane mapping, swing/contact state machines, single batch writer, query/commit recovery, fixed-step simulation and buffered trace integration.
- **Game:** native snapshot/commit service, persistent-for-session dedup cache, control/readiness/reset handling, separate minimal SDL3 renderer, state/pose diagnostics and presentation markers.
- **Debug:** runtime emitters/collector, source registry, protobuf packet decoding and pcap joining, timeline/UI/reporting, virtual controllers/poses/game, deterministic replay, packet/message fault injector and evidence bundles. Offline checker/tests are the only implemented subset.
- **Documentation:** pin decisions, review cross-repository schema changes, keep English instructions and exact measured validation status, publish no fake build commands or benchmarks.

## Open decision register

| ID | Remaining decision | Recommended starting point / resolving evidence |
| --- | --- | --- |
| O-01 | Exact webcam and playing distance | Validate actual Facecam generation/mode or alternative at full lane distance; focus/FOV and motion blur gate |
| O-02 | Purchased controller/IMU/actuator/power parts | ESP32-S3 DevKitC + BMI270 SPI + DRV2605L/LRA reference; reviewed battery/power schematic and driver ratings |
| O-03 | Exact OS/kernel/driver and dependency versions | Pi3 64-bit OS Lite; Windows native state/capture plus GPU runtime; pin proven manifests, evaluate PREEMPT_RT |
| O-04 | Model artifact license/checksum and GPU binary compatibility | RTMO-m 640 candidate, no silent CPU fallback; measure four-person tails with renderer active |
| O-05 | Final calibration layout and accuracy | Fixed player planes/lanes, measured geometric residuals, neutral heading and drift; reject unverified true 3D claims |
| O-06 | Model confidence and dynamic fusion/swing tuning | Replay dataset with labeled faults and motion, not arbitrary interpretation of model score as probability |
| O-07 | Refined physical budgets and thresholds | Start from reference profile; measure30/40/50 ms and data-age gates before accepting or revising |
| O-08 | Battery duration and haptic drive calibration | Actual current/energy and onset tests; no mAh-only runtime promise |
| O-09 | Source authentication and deployment isolation | Controlled dedicated LAN baseline; stronger authenticated profile if trust boundary changes |
| O-10 | Maximum encoded-size and resource proof | Generated codecs/nanopb limits,8-entry worst-case message fixtures, bounded memory/retention pressure |
| O-11 | Debug viewer technology and collection implementation | Follow debug-units module plan and trace-v1; keep rendering/export off critical path |
| O-12 | Hardware/radio/model upgrade decision | Change only the measured bottleneck; faster Pi does not resolve radio nondeterminism or monocular depth |

## Recording changes

Use an [ADR](adr/README.md) to supersede a reference choice or change protocol semantics. Update schema/profile hashes, component READMEs, debug fixtures and relevant acceptance gates together. A chosen design is not an implemented capability; a successful synthetic test is not a live hardware result. Preserve original licenses and avoid introducing institutional or assumed staffing context.
