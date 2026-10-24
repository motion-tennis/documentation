# Motion Tennis master plan

[Documentation home](../README.md) · [Reference profile](../spec/reference-profile.json) · [Implementation gates](roadmap.md)

Revision: `webcam-pi3-wireless-v1`, 2026-10-24. All runtime choices and numerical limits below are **Proposed reference design**, unless explicitly user-confirmed. They are concrete implementation defaults to evaluate, not measured capabilities. **Implemented:** documentation, a documentation checker and the small offline trace tool in `debug-units`; no controller, tracker, physics service or game implementation exists yet.

## Confirmed constraints and superseded assumptions

- Four players must use wireless, battery-powered handheld controllers.
- The available physics computer is a **Raspberry Pi 3 Model B**.
- The application host is the user's **Windows laptop with an RTX 5080**. The exact GPU variant, VRAM, driver, Windows version and performance are not inspected.
- The first tracking implementation uses a webcam and **calibrated 2.5D gameplay**; genuine 3D tracking is a later stage. An Elgato Facecam or another webcam is a candidate; its exact model is not confirmed.
- Controller board and IMU are not yet owned/selected. The bill of materials below is a reference recommendation, not an inventory claim.

This supersedes Kinect-only tracking and Linux-first PC deployment from the earlier design. The mandatory **physics-to-game ball-state request and response remain**. The supplied sequence image is a conceptual reference: its German labels and older Kinect hardware are not copied into repository diagrams. The image's parallel feedback/update branches are refined by a proposed commit acknowledgement so an uncommitted hit is not confirmed to a player.

## Device and software allocation

| Device / repository | Reference implementation | Owns | Must not own |
| --- | --- | --- | --- |
| Four ESP32-S3 handhelds / `motion-tennis-controller` | ESP-IDF, C/C++; BMI270 SPI sampling; UDP transport; bounded local output driver | 200 Hz samples, original timestamps, transaction IDs, local RTT, battery/error state, LED and haptic actuation | Hit calculation, world position inferred from unbounded acceleration integration |
| Windows laptop / `motion-tennis-camera-tracking` | Native Media Foundation capture adapter; Python RTMO-m/rtmlib worker using verified ONNX Runtime GPU; continuous identity association | Webcam frame times, 17-joint observations, track IDs, quality, frame-drop counters | Authoritative ball physics; invented metric depth |
| Pi 3 Model B / `motion-tennis-physics-engine` | Native C++20, CMake; fixed-size buffers; nonblocking I/O and 200 Hz scheduler | Time alignment, controller/person association, delayed pose/IMU fusion, collision, all ball integration, ordered batch proposals | Neural inference, rendering, disk writes on the critical path |
| Windows laptop / `motion-tennis-game-engine` | Native C++20 state service plus separate C++/SDL3 simple renderer process | Sole committed ball snapshot, atomic batch validation, event history, UI and scene | Independently integrating authoritative ball state; coupling query replies to GPU frames |
| Windows laptop / `debug-units` | Python offline checker now; collector/viewer/replay/fault harness planned | Run manifests, merged traces, packet evidence, percentile/error reports, simulation tools | Blocking gameplay to save logs; interpreting packet ACK as completed physics |
| Workstation / `documentation` | Markdown, reference profile and proposed Protocol Buffers schema | Shared contracts, timing definitions, acceptance gates, ADRs | Claims of hardware support without evidence |

Exact dependency versions must be pinned from a verified installation in each implementation repository. These are explicit stack choices for the reference design; executable entry points and build files do not exist yet. See [hardware](hardware.md), [tracking stack](tracking-stack.md), [physics](physics.md) and [game integration](game-engine.md).

## Network decision

Use a dedicated 2.4 GHz access point for the four controllers. Wire both the Pi and Windows host to its LAN/switch. The Pi's onboard Wi-Fi does not serve as the access point. The Pi 3's 100 Mb/s Ethernet is sufficient for the proposed compact sensor traffic by bandwidth arithmetic; latency under load remains a measurement gate. Keep webcam video local to the laptop.

Use **UDP with bounded Protocol Buffers messages** for live controller/pose/query/commit/feedback traffic, at most 1,200 application bytes per datagram. Use separate TCP control connections for setup, pairing, calibration, recovery and run control. This replaces the earlier proposed length-prefixed JSON live transport. Every runtime must use the same [protocol](protocol.md), [schema](../spec/motion.proto), and profile hash.

Wi-Fi is retained because wireless battery operation is mandatory and its performance can be measured with the existing device family. It is not deterministic. ESP-NOW is an alternative experiment, not a guarantee: it uses the same radio band, needs a Pi gateway and still needs application correlation. USB is only a stationary diagnostic reference. See [networking tradeoffs and exact ports](networking.md).

## Four-player scheduling without losing measurement identity

Four 200 Hz controllers generate **800 measurement transactions/s**. Every IMU interrupt starts its own transaction with `t0`, session and sequence; bundling must not silently redefine a transaction as four samples.

Every 5 ms, the Pi selects an ordered batch: normally four inputs, at most eight, with at most two per controller. Each selected transaction has an explicit logical ball query. One `ball_state_request` datagram carries those query entries; `ball_state_response` echoes them and supplies one atomic common snapshot. This is transport batching of the required exchange, not its removal.

Physics orders the inputs deterministically, integrates once, evaluates sequentially against the snapshot and any preceding candidate changes, then proposes one atomic `state_update` containing the final ball state and ordered event list. The game commits the entire batch against its base version and returns `state_commit_result`. Only then are individual `feedback_result` messages sent. A batch shares one committed version; `event_index` records intra-batch order.

Only one state batch is in flight. A busy scheduler skips and counts releases rather than spawning concurrent ball writers. At most four fixed steps may be caught up; lag beyond 20 ms pauses gameplay. Queues hold four pending inputs per controller. Overflow, stale inputs and expired work receive explicit outcomes where delivery is possible; controller expiry completes the accounting otherwise. Eight batch slots give recovery headroom over the nominal four arrivals per tick; this is not proof of capacity. See [consistency and arbitration](physics.md).

## Fusion and gameplay geometry

The Pi maintains 256 IMU samples per controller and eight pose observations per person. It aligns a delayed pose with historical IMU samples at the pose's capture time, updates the plane-position estimate, and replays inertial orientation to the current evaluation time. Accelerometer corrections are gated during dynamic swings; yaw uses a neutral-grip heading reference and drift/recalibration limits. Do not claim a six-axis IMU observes absolute yaw.

Pixel observations are calibrated rays intersected with a declared player interaction plane. Feet/floor calibration can locate a lane; a floor homography must not be applied to airborne hands as though they lie on the ground. Initial gameplay uses fixed lane assignment and a constrained depth model; projected wrist/racket position is explicitly `plane_2_5d`, not measured 3D. Racket orientation comes from the calibrated IMU; a 2D elbow/wrist line does not fully determine it.

Position prediction is constant velocity in the plane, capped at 50 ms including uncertainty. Maximum pose age is 80 ms; IMU age 30 ms. Historical IMU/pose alignment error plus uncertainty must be at most 25 ms. Network clock mapping uncertainty must be at most 2 ms per source; camera timestamp uncertainty at most 8 ms after characterization. Both age and prediction gates apply, so the tighter one controls eligibility. Unknown timing, ambiguous identity or unsuitable tracking causes an explicit error. These initial limits require measured eligibility and collision tests, not just a smooth avatar.

## Real-time contract and feedback

This architecture targets **deadline-aware soft real-time service with firm expiry of stale gameplay work**, not a proven hard real-time end-to-end system. Windows scheduling, GPU inference and wireless contention prevent an unconditional deadline guarantee. PREEMPT_RT can improve the Pi's scheduling behavior; it does not change that fact.

| Observable requirement | Initial reference target | Failure behavior |
| --- | --- | --- |
| Controller sample cadence | 200 Hz | Count skipped IRQs/samples and saturation; no invented samples |
| Physics release cadence | 5 ms; batch service p99 at most 4 ms | Count missed releases; bounded catch-up, pause above lag limit |
| Application response `tr - t0` | p99 at most 30 ms | Count late and failed transactions in the service objective |
| Eligible electrical cue `t1 - t0` | p99 at most 40 ms | Suppress expired cues; count missed/absent output |
| Local controller expiry | 50 ms | Terminal timeout; no subsequent gameplay actuation for that transaction |
| Pose output with four visible people | At least 30 Hz sustained; 60 Hz preferred | Count skipped frames and tracking failures; reject stale observations |
| Rendering | 60 Hz target independent of state replies | Record frame delays; do not stall the state service |

`tr` and `t1` use the same ESP32 monotonic clock as `t0`. No device synchronization is needed for those local differences. The RTT includes the required query and response, batch waiting, calculation and commit wait; it does not automatically include camera/IMU work preceding `t0`. Full physical motion-to-vibration or display latency is a separate experiment.

Every measurement gets a correlated outcome, but **800 outcomes/s do not mean 800 physical motor pulses/s**. The status LED reflects current state; distinct haptic cues are emitted once per semantic hit or completed missed swing. Each result declares cue eligibility. Non-eligible samples have no `t1`; the debug report counts them explicitly. Tracking/communication errors have distinct fault patterns and suppress ordinary hit/miss cues. See [controller behavior](controller.md).

## Debug environment and implementation order

The debug environment has three independent evidence layers: application event traces, packet captures, and GPIO/optical/mechanical measurements. A trace joins controller/session/request, source sample, pose frame, query, batch, base/committed version and event index. It includes dropped logs and failed/expired inputs. Collection is buffered and outside the control path.

Implement in this order:

1. Lock this profile and schema revision; establish a run manifest and synthetic trace checks in all six repositories.
2. On the actual Windows laptop, prove four-person webcam inference, whole-body focus/FOV, timestamp uncertainty and 2.5D calibration. On the Pi 3, prove scheduler and wired state-query/commit capacity with a simulator.
3. Build one battery controller and measure IMU/IRQ/output boundaries and wireless RTT against the simulated game/pose services.
4. Integrate one controller with real tracking and ball-state service, including hits, misses and all failure paths.
5. Integrate four controllers; exercise batch ordering, load, interference, drops, duplicates, stale frames, power changes and restarts.
6. Only after passing recorded gates, freeze reproducible build/run commands and choose whether to upgrade the Pi, model, camera or radio based on the bottleneck evidence.

For each of one through four controllers, perform three 10-minute baseline runs after declared warmup. At 200 Hz, a four-controller run offers 480,000 transactions. Proposed pass criteria include p99 targets, at most 1% late-or-failed attempts, zero wrong-player associations, zero duplicate commits and no unexplained log loss. Publish all denominators, failures and censored timeouts. Fault runs test bounded recovery, not necessarily the same performance targets. See [testing](testing.md), [debugging](debugging.md) and [roadmap](roadmap.md).

No procurement, camera inference, radio experiment, hardware timing or runtime integration was performed by writing this plan. A perfect measured budget cannot be inferred from a GPU model name; the plan makes each claim testable and each fallback explicit.
