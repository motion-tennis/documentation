# Motion Tennis master plan

[Documentation home](../README.md) · [Reference profile](../spec/reference-profile.json) · [Shared stages](project-stages.md) · [Current stage](project-status.md)

Current proposed profile: `webcam-pi3-doubles-v3`, 2026-10-26. [ADR 0011](adr/0011-full-match-contract-and-state-stream.md) adds the full-match contract and dedicated bounded state stream. [ADR 0008](adr/0008-mpu6050-zephyr-prototype.md) records the user-selected MPU-6050/Zephyr first prototype, revising the hardware/runtime metadata of the original 2026-10-24 profile. The [independent IMU markers](imu-trigger-markers.md) and [IMU assessment](imu-selection.md) define its integration gates. Other runtime choices and numerical limits below are **Proposed reference design**, unless explicitly user-confirmed. They are concrete implementation defaults to evaluate, not measured capabilities. **Implemented:** documentation, documentation/host-contract checkers and the small offline trace tool in `debug-units`; no controller, tracker, physics service or game implementation exists yet.

## Confirmed constraints and superseded assumptions

- Four players must use wireless, battery-powered handheld controllers.
- The game is **2v2 doubles** with automatic avatar court movement, controller-lift toss and overhead serving, normal tennis scoring, explicit team assignment and two elevated views behind the teams. Physical players remain in their tracking stations; [ADR 0010](adr/0010-doubles-auto-movement-gameplay.md) records the decision.
- The available physics computer is a **Raspberry Pi 3 Model B**.
- The game client, renderer and UI must use **Unity with C#**, replacing the SDL3 proposal; the committed-state service remains a separate process. [ADR 0012](adr/0012-unity-game-engine.md) records the user selection on 2026-10-29.
- The application host is the user's **Windows laptop with an RTX 5080**. The exact GPU variant, VRAM, driver, Windows version and performance are not inspected.
- The first tracking implementation uses a webcam and **calibrated 2.5D gameplay**; genuine 3D tracking is a later stage. An Elgato Facecam or another webcam is a candidate; its exact model is not confirmed.
- The first controller prototype uses **MPU-6050 over I²C with Zephyr**. The exact ESP32 board, breakout and dependency versions remain open; selection is not a claim that parts were purchased or tested.
- Preserve the continuous 200 Hz gameplay stream while adding a configurable hardware acceleration-threshold IRQ as an independent, fully traceable diagnostic marker. Implement and validate the MPU-6050 motion-trigger extension, shared-INT handling and early timestamp capture in Zephyr.
- Use the Pi monotonic clock as the shared time reference. Correct source-clock offset and drift through versioned mappings, preserve original timestamps, and expose time uncertainty and mapping validity in the debug tool. See [ADR 0009](adr/0009-pi-reference-clock-mapping.md).

This supersedes Kinect-only tracking and Linux-first PC deployment from the earlier design. The mandatory **physics-to-game ball-state request and response remain**. The supplied sequence image is a conceptual reference: its German labels and older Kinect hardware are not copied into repository diagrams. The image's parallel feedback/update branches are refined by a proposed commit acknowledgement so an uncommitted hit is not confirmed to a player.

## Device and software allocation

| Device / repository | Reference implementation | Owns | Must not own |
| --- | --- | --- | --- |
| Four ESP32 handhelds, S3 board proposed / `motion-tennis-controller` | MPU-6050 over I²C with Zephyr selected for the first prototype; UDP transport; bounded local output driver | Unchanged 200 Hz samples, independent threshold markers, original timestamps, transaction IDs, local RTT, battery/error state, LED and haptic actuation | Hit calculation, world position inferred from unbounded acceleration integration |
| Windows laptop / `motion-tennis-camera-tracking` | Native Media Foundation capture adapter; Python RTMO-m/rtmlib worker using verified ONNX Runtime GPU; continuous identity association | Webcam frame times, 17-joint observations, track IDs, quality, frame-drop counters | Authoritative ball physics; invented metric depth |
| Pi 3 Model B / `motion-tennis-physics-engine` | Native C++20, CMake; fixed-size buffers; nonblocking I/O and 200 Hz scheduler | Time alignment, person/team association, delayed pose/IMU fusion, automatic avatar movement, ball/contact/serve/rule/score calculation and ordered batch proposals | Neural inference, rendering, disk writes on the critical path |
| Windows laptop / `motion-tennis-game-engine` | Unity/C# game client and UI selected; separate native C++20 state service proposed | Sole committed v0.3 match snapshot, atomic validation, event history, team lobby and two team views | Independently calculating ball/avatar/score changes; coupling query replies to GPU frames |
| Windows laptop / `debug-units` | Python offline checker now; collector/viewer/replay/fault harness planned | Run manifests, merged traces, packet evidence, percentile/error reports, simulation tools | Blocking gameplay to save logs; interpreting packet ACK as completed physics |
| Workstation / `documentation` | Markdown, reference profile and proposed Protocol Buffers schema | Shared contracts, timing definitions, acceptance gates, ADRs | Claims of hardware support without evidence |

Exact dependency versions must be pinned from a verified installation in each implementation repository. These are explicit stack choices for the reference design; runtime executable entry points and build files do not exist yet. Offline contract-validation entry points are documented in [S0 evidence](s0-baseline.md). See [hardware](hardware.md), [tracking stack](tracking-stack.md), [physics](physics.md) and [game integration](game-engine.md).

The machine-readable profile retains MPU-6050/I²C and Zephyr as the agreed first-prototype selection. The v0.3 revision changes schema/profile identities and the Pi/PC state transport explicitly, while preserving the selected IMU, 200 Hz stream and existing timing targets. BMI270/ESP-IDF are historical recommendations. The [IMU assessment](imu-selection.md) retains LSM6DSV16X/32X as later alternatives if measured constraints require another sensor. First validate the selected MPU-6050's explicit DLPF/divider setup, shared INT, detector semantics and Zephyr motion/early-timestamp extension; selection does not assert that these gates have passed.

## Doubles interaction and player assignment

Use four humans, one controller and one persistent avatar per person, split into two teams. Players supply body-relative racket motion and timing; the Pi moves their avatars to cover the court. Controller lift initiates the assigned server's toss, followed by an overhead stroke attempt. The continuous 200 Hz input and diagnostic-only IRQ marker remain unchanged. Normal tennis point progression, doubles service/receive order, first/second serve, net/out, service let and second-bounce handling are defined in [gameplay](gameplay.md). Best-of-three sets with a tie-break at 6-all is a proposed configurable match default, not a user-selected match length.

Startup uses the [existing explicit association workflow](player-assignment.md): choose Team A/B and an available stable slot, identify controller and tracked person through guided motion, confirm hand/calibration, then complete Association installation ACK and resume readiness. Proposed slot encoding is `1=A1`, `2=A2`, `3=B1`, `4=B2`. All four confirmed players are needed for a normal match; one-to-three-controller trials remain integration tests. Repositioning, changing ends or changing front/back roles never silently changes player/team identity.

Render one shared match in two elevated views, each behind its own team's current court end. A horizontal A-above/B-below split is the proposed arrangement; both show the same ball, committed score and event history. Real camera tracking remains active for local gestures and identity. It does not command virtual running or measure unrestricted human depth.

The v0.3 [match contract](protocol.md#doubles-match-contract-extension) carries roster, avatar, serve and score state with [generated host-codec and atomic-state fixtures](s0-baseline.md). Device interoperability and gameplay runtimes remain unimplemented. [ADR 0011](adr/0011-full-match-contract-and-state-stream.md) records the explicit state transport revision.

## Network decision

Retain Wi-Fi as the agreed near-term transport. **Variant A, initial baseline:** a dedicated external 2.4 GHz access point serves the four controllers, with Pi and Windows host wired to its LAN/switch. **Variant B, planned comparison:** the Pi 3 B hosts the controller WLAN on its onboard radio, while the laptop remains wired to the Pi. The [controlled A/B plan](networking.md#external-ap-versus-pi-hotspot-comparison) compares complete latency, failures and Pi load under identical application traffic; hotspot endpoint/route/debug reachability must be proven first. Neither variant has measured performance evidence. The Pi 3's 100 Mb/s Ethernet is sufficient for the proposed compact sensor traffic by bandwidth arithmetic; latency under load remains a measurement gate. Keep webcam video local to the laptop.

Use **UDP with bounded Protocol Buffers messages** for controller/pose/feedback traffic, at most 1,200 application bytes per datagram. The v0.3 Pi/PC query/commit leg uses a dedicated TCP state connection with four-byte length framing and at most 8,192 envelope bytes. Use separate TCP control connections for setup, pairing, calibration, recovery and run control. The state-stream revision preserves required exchanges, atomicity and the existing sampling/deadline profile. Every runtime must use the same [protocol](protocol.md), [schema](../spec/motion.proto), and profile hash.

Wi-Fi is retained because wireless battery operation is mandatory and its performance can be measured with the existing device family. It is not deterministic. ESP-NOW and other radio alternatives are deferred outside the current A/B work package; reopening them requires an explicit later decision. USB is only a stationary diagnostic reference. The A/B experiment keeps 200 Hz transactions, Protobuf payloads, ports, queues/deadlines and diagnostic markers unchanged. See [networking tradeoffs and exact ports](networking.md) and [ADR 0007](adr/0007-wifi-topology-comparison.md).

## Pi-reference time synchronization

**Agreed design:** map each ESP32 and laptop clock domain into Pi monotonic time using `T_pi = a * t_source + b`, correcting offset and drift while retaining the original source counter. The Pi owns runtime mappings and their reference epoch; the collector/viewer consumes the same immutable versions. Four-timestamp `ClockExchange` messages use the existing TCP control connections. The proposed Pi-initiated exchange keeps all four timestamps at the mapping owner. No clock fitting, live exchange or uncertainty-aware viewer is implemented yet.

Refresh mappings every 1 s; expire them after 5 s without a valid update or sooner when uncertainty becomes unacceptable. Source restarts invalidate that source's future mapping; a Pi reference-session restart requires all participants to establish new mappings. Preserve historical versions within their original validity intervals. The existing 2 ms/source target is a measurement gate, not a synchronization guarantee. Cross-source uncertainty combines conservatively; two sources at ±2 ms can have ±4 ms relative mapping uncertainty before event-capture uncertainty is included.

The debug timeline must show uncertainty bands, numeric bounds, offset/drift, mapping age/ID and validity for each source. Retain causal links by transaction/marker IDs even when no valid shared-time position exists; show local lanes and omit unsupported cross-device durations. Local ESP32 sample and marker intervals remain available without a mapping. Camera exposure timing requires separate characterization. See the [clock contract](coordinates-and-time.md#pi-reference-clock-mapping) and [debug design](debugging.md). Gameplay payloads, 200 Hz sampling and transaction expiry remain unchanged.

## Four-player scheduling without losing measurement identity

Four 200 Hz controllers generate **800 measurement transactions/s**. Every regular sampling boundary starts its own transaction with `t0`, session and sequence; bundling must not silently redefine a transaction as four samples. The additional threshold IRQ creates a diagnostic marker with `t_trigger`, not another gameplay transaction.

Every 5 ms, the Pi selects an ordered batch: normally four inputs, at most eight, with at most two per controller. Each selected transaction has an explicit logical ball query. One framed `ball_state_request` carries those query entries; `ball_state_response` echoes them and supplies one atomic common snapshot. This is transport batching of the required exchange, not its removal.

Physics orders the inputs deterministically, integrates once, evaluates sequentially against the snapshot and any preceding candidate changes, then proposes one atomic `state_update` containing the final ball state and ordered event list. The game commits the entire batch against its base version and returns `state_commit_result`. Only then are individual `feedback_result` messages sent. A batch shares one committed version; `event_index` records intra-batch order.

Only one state batch is in flight. A busy scheduler skips and counts releases rather than spawning concurrent ball writers. At most four fixed steps may be caught up; lag beyond 20 ms pauses gameplay. Queues hold four pending inputs per controller. Overflow, stale inputs and expired work receive explicit outcomes where delivery is possible; controller expiry completes the accounting otherwise. Eight batch slots give recovery headroom over the nominal four arrivals per tick; this is not proof of capacity. See [consistency and arbitration](physics.md).

## Fusion and gameplay geometry

The Pi maintains 256 IMU samples per controller and eight pose observations per person. It aligns a delayed pose with historical IMU samples at the pose's capture time, updates the plane-position estimate, and replays inertial orientation to the current evaluation time. Accelerometer corrections are gated during dynamic swings; yaw uses a neutral-grip heading reference and drift/recalibration limits. Do not claim a six-axis IMU observes absolute yaw.

Pixel observations are calibrated rays intersected with a physical station plane. Feet/floor calibration can locate the station; a floor homography must not be applied to airborne hands as though they lie on the ground. Estimate body-relative wrist/arm motion in the constrained `plane_2_5d` model and combine it with the Pi-controlled avatar root and heading. Station location does not place or move the avatar around the virtual court. Racket orientation comes from calibrated local IMU orientation transformed through the avatar frame; a 2D elbow/wrist line does not fully determine it.

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

The [marker contract](imu-trigger-markers.md) adds session-scoped trigger IDs and explicit links to regular samples. Trace the existing full query/response/commit/feedback path without changing payloads, sample rate, ordering, priorities or expiry. Keep per-sample timing and trigger-to-linked-response or semantic-cue timing separate; unknown links and failed/absent endpoints remain visible. The 5 ms sample period does not establish sensor detection latency.

The debug environment has three independent evidence layers: application event traces, packet captures, and GPIO/optical/mechanical measurements. A trace joins controller/session/request, source sample, pose frame, query, batch, base/committed version and event index. It includes dropped logs and failed/expired inputs. Collection is buffered and outside the control path.

The [shared S0–S7 stages](project-stages.md) define the implementation sequence and gate evidence; the [central ledger](project-status.md) records the active stage. In order: complete the shared contract baseline, build isolated component slices, prove device/transport feasibility, integrate one diagnostic controller, deliver playable four-person doubles, perform matched measurement/hardening, then freeze a reproducible demonstrator. True 3D and alternative hardware/radio work remain separately scoped extensions.

Use each repository's orientation and workflow to choose one bounded slice. Keep parallel camera, controller and Pi/state feasibility work within the released stage. Trace emission begins with the isolated components, collection supports feasibility probes, and the first integrated path already requires a viewer with visible clock uncertainty and explicit marker links. Do not postpone evidence until final evaluation or read this complete-system plan as authorization for all implementation stages.

For each of one through four controllers, perform three 10-minute baseline runs after declared warmup. At 200 Hz, a four-controller run offers 480,000 transactions. Proposed pass criteria include p99 targets, at most 1% late-or-failed attempts, zero wrong-player associations, zero duplicate commits and no unexplained log loss. Publish all denominators, failures and censored timeouts. Fault runs test bounded recovery, not necessarily the same performance targets. See [testing](testing.md), [debugging](debugging.md) and [roadmap](roadmap.md).

No procurement, camera inference, radio experiment, hardware timing or runtime integration was performed by writing this plan. A perfect measured budget cannot be inferred from a GPU model name; the plan makes each claim testable and each fallback explicit.
