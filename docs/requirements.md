# Requirements and acceptance contract

[Documentation home](../README.md) · [Master plan](master-plan.md) · [Timing](timing.md) · [Testing](testing.md)

**Agreed direction:** four wireless battery controllers, Pi 3 Model B, Windows RTX 5080 laptop, webcam-first 2.5D then true 3D. **Proposed reference:** specific stacks, algorithms, rates, thresholds, batch and transport details below. **Implemented:** documentation and offline tooling only. Performance targets become acceptance claims only after measured evidence.

## Functional requirements

| ID | Requirement | Evidence |
| --- | --- | --- |
| F-01 | Support one through four active wireless battery controllers | Separate keys/person associations and complete outcome ledger under each player count |
| F-02 | Preserve one measurement transaction per defined regular IMU sampling boundary | Source `t0`, sequence/sample IDs, generated/dropped/terminal counts; separate threshold markers do not create transactions |
| F-03 | Combine active camera body/joint tracking with IMU data on Pi | Delayed-pose/historical-IMU provenance, calibrated 2.5D geometry, explicit stale/invalid outcomes |
| F-04 | Every valid physics transaction has a logical ball-state request and matching response | Batched query entries retain every key and echo the shared state version/tick |
| F-05 | Pi calculates hit/miss and resulting ball motion | Deterministic fixtures, collision/contact-latch and fusion tests |
| F-06 | Every generated transaction ends in a correlated result or counted local failure | Includes misses, invalid inputs, overload, loss, timeout and reporting-cutoff pending work |
| F-07 | Feedback distinguishes hits, completed missed swings and faults | Bounded semantic cues, eligibility flags, electrical traces; no 200 Hz pulse assumption |
| F-08 | Windows stores sole committed match state and provides UI/visualization | Versioned v0.3 match contract; atomic ball/avatar/serve/score tests and independent renderer |
| F-09 | Resolve four-player concurrency and periodic motion without competing state writers | Ordered atomic batches, CAS/version checks, bounded catch-up, session/epoch fencing |
| F-10 | Preserve original capture timestamps and source IDs through processing | Separate capture/arrival/compute/simulation trace fields with clock domains |
| F-11 | Explicit connection, association, calibration, loss and restart handling | Readiness barriers; no silent nearest-person reassignment or replayed haptics |
| F-12 | Provide a debug environment across all six repositories | Emitters, collector, decoder, viewer, replay/fault modules specified; offline audit implemented |
| F-13 | Keep current webcam output honestly 2D/2.5D | No invented metric wrist depth; true 3D requires new calibrated profile |
| F-14 | Add a configurable hardware acceleration-threshold marker without changing the continuous gameplay stream | Independent `t_trigger`, explicit sample/transaction link and full-path trace; unchanged cadence, payload, priority, processing and expiry; see [marker contract](imu-trigger-markers.md) |
| F-15 | Use Pi-reference time mapping with offset/drift correction and visible debug uncertainty | Pi-owned versioned maps for ESP32/laptop clocks; preserved raw timestamps and sessions; timeline error bands, numeric bounds, mapping status and explicit unmapped events; see [clock contract](coordinates-and-time.md#pi-reference-clock-mapping) |
| F-16 | Play 2v2 doubles with automatic avatar locomotion | Four confirmed humans and stable team/player/avatar slots; Pi-owned movement plus body-relative human gestures; physical players need not run after the ball |
| F-17 | Serve through controller lift/toss and an overhead stroke | Assigned-server gesture state machine; abandoned toss, attempted miss, first/second fault and let remain distinct; no IRQ-triggered extra transaction |
| F-18 | Apply ordinary tennis scoring and fault semantics | Love/15/30/40, deuce/advantage, service/receiver rotation, line/net/out/second-bounce rules; versioned match-format configuration; technical failures do not award points |
| F-19 | Show one shared match from both teams' elevated rear views | Two labeled viewports consume the same committed version; end changes alter camera placement, not teams, handedness or authoritative geometry |
| F-20 | Reuse explicit controller/person association for team setup | [Assignment contract](player-assignment.md), uniqueness, guided identification, operator confirmation, install ACK/resume and four-ready start; no silent reassignment |

F-04 does not require invalid inputs to query the game before rejection. The required exchange cannot be replaced by an old pushed snapshot or transport acknowledgement. A batched framed state message must still contain every selected logical query.

F-16 through F-20 are agreed gameplay requirements described in [gameplay](gameplay.md). The proposed v0.3 schema covers their match-state interface; generated host fixtures validate the contract, while their runtime behavior remains unimplemented. Keep the unchanged IMU stream and explicit transaction accounting while extending atomic state/query/publication contracts. Full doubles needs four humans; one-to-three-controller capacity/fault trials remain diagnostic integration cases.

## Nonfunctional requirements

| ID | Requirement | Reference acceptance |
| --- | --- | --- |
| N-01 | Controller-local application and electrical timing | p99 response ≤30 ms; eligible electrical ≤40 ms; local expiry 50 ms; full [timing definitions](timing.md) |
| N-02 | Explicit sensor age/alignment/uncertainty | Gates in [reference profile](../spec/reference-profile.json), conservative upper-bound checks |
| N-03 | Bounded memory and scheduling | 4/controller Pi queue, 8/batch, max 2/controller, 1 state batch,finite histories/retention; overflow visible |
| N-04 | Complete failure accounting | Median/tails/max plus drops/timeouts/conflicts/tracking failures/log loss; no successful-only claims |
| N-05 | Reproducible builds and runs | Source/model/schema/profile hashes, dependency locks, calibration, hardware/driver/network manifests |
| N-06 | Bounded observation overhead | Buffer logs off path; compare timing with logging disabled/enabled and record losses |
| N-07 | Compatible interfaces across component owners | One canonical schema/profile, shared fixtures and reviewed changes |
| N-08 | English-only project edits | Documentation, code, identifiers, comments and examples; C/C++ comments use `//` |
| N-09 | Hardware-safe feedback and battery behavior | Reviewed selected power/driver design, default-off, local pulse cap and low-battery tests |
| N-10 | Honest real-time classification | Deadline-aware soft service with firm stale-work rejection; no unproven hard E2E guarantee |
| N-11 | Qualified cross-device timing | Existing reference gates: refresh maps every 1 s, expire after 5 s without valid refresh, validate at most 2 ms mapping uncertainty per source; account for drift/age and capture uncertainty, reject unsupported cross-device timing while retaining local intervals |

## Rate and capacity requirements

The proposed 200 Hz per controller produces 800 transactions/s. The 5 ms scheduler normally receives 4 inputs and can process up to 8 per batch with max 2/controller. Every input still receives a result or recorded failure. Target p99 batch service≤ 4 ms; if the measured service time cannot sustain the load, report failure and choose an explicit revised profile. Do not silently decimate inputs, omit required queries, hide stalled simulation with render extrapolation, or remove failure samples.

Camera capture 60 Hz desired, GPU pose output ≥ 30 Hz sustained with 4 people, render 60 Hz target. These rates are independent. A 200 Hz IMU does not create 200 fresh images/s; delayed historical fusion handles the difference and may reject unsuitable observations.

The additional threshold detector has its own rate, filter and duration characteristics; 200 Hz regular sampling means a 5 ms nominal interval, not a proven 5 ms threshold-to-IRQ latency. MPU-6050 over I²C with Zephyr is selected for the first prototype. Confirm DLPF/divider setup and readback, actual sample cadence, motion-trigger driver coverage and shared-INT timestamp attribution before acceptance; no silent rate substitution or sample decimation is allowed. See [IMU selection](imu-selection.md).

## Acceptance gates

1. **Specification:** schema/profile agreement, complete repository navigation and valid examples; clear current versus historical decisions.
2. **Hardware/runtime feasibility:** actual webcam focus/FOV/timestamps, four-person GPU path, controller parts/power and Pi 3 scheduling/wired-state capacity.
3. **Component correctness:** bounded codecs, maximum-size 8-entry updates, deterministic physics, mapping/association barriers, duplicate/failure tests.
4. **One-player integration:** full ball query/response/commit chain and electrical markers, including misses and tracking failure.
5. **Four-player measurement:** three 10-minute runs per controller count, declared warmup; reference p99 and ≤ 1% late-or-failed criterion, no wrong associations/duplicate commits/unexplained evidence loss. Fault runs demonstrate bounded failure/recovery.
6. **Handover:** real pinned setup/build/run commands and recorded evidence; full collector/viewer/replay delivered before claiming a complete runtime debug environment.

The earlier 25 ms IMU-to-Pi and 15 ms decision-to-electrical values are retained as historical design discussion in [timing](timing.md), not active guarantees or an additive 40 ms bound. No hardware performance gate has been passed by this documentation change.
