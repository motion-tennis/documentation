# Timing requirements and measurement methodology

[Documentation home](../README.md) · [Network profile](networking.md) · [Controller](controller.md) · [Clock domains](coordinates-and-time.md) · [Test matrix](testing.md)

**Agreed design:** measure the complete application transaction, preserve sensor and transaction identity, and account for unsuccessful observations. **Proposed reference targets:** the rates, latency targets, cutoffs and stage allocations on this page. **Implemented:** no timing hooks, running gameplay services or hardware measurements exist. The available hardware does not establish any of these performance figures.

The reference deployment uses four wireless battery-powered ESP32 controllers, a Raspberry Pi 3 Model B for fusion/physics, and a Windows RTX 5080 laptop for continuous webcam pose estimation, committed ball state and visualization. It is a deadline-aware real-time design: expired gameplay results lose their value and must not actuate late. It is not a demonstrated hard end-to-end real-time system. Wireless contention, a general-purpose Windows host, GPU inference and camera/display pipelines do not currently have proven worst-case bounds.

## Primary controller measurements

Use one monotonic ESP32 timer and the same boot/session for all three timestamps:

| Timestamp | Event and recording rule |
| --- | --- |
| `t0` | The specified regular IMU data-ready interrupt/sampling boundary starting the identified transaction. Prefer hardware capture if supported; otherwise timestamp the earliest bounded interrupt handler and characterize its delay from the physical interrupt edge. |
| `tr` | Complete application-message receipt for the matching `feedback_result`. Capture a candidate time when the full UDP payload or bench-transport frame becomes available, then retain it as `tr` only after protocol, identity, payload and expiry validation. A transport receipt acknowledgement is not this event. |
| `t1` | The electrical transition that activates the selected feedback output, such as LED drive or motor-driver enable/PWM start. A function call that only queues output is not electrical actuation. Verify timestamp placement against an electrical trace. |

Application response time is `L_response = tr - t0`. Time to electrical feedback is `L_electrical = t1 - t0`. Both use one ESP32 clock, so no device-to-device synchronization is needed for these differences. Timer scale error, wrap handling and event-placement error still matter; never subtract timestamps across controller boots.

The `tr` boundary excludes validation that happens after complete message reception. Record `t_validated` separately when needed. That validation, output scheduling and electrical delay are included in `t1 - tr`. Malformed, expired, wrong-session and duplicate responses retain diagnostic receive times but do not become a new successful completion or a repeated actuation.

Keep `t_led` and `t_motor` separately when their outputs differ, and state which defines the reported `t1`. If a policy intentionally leaves the motor off, use `null`/not applicable for its timestamp. A local timeout may produce a visible error without any application response; retain its deadline and fault-output times while `tr` remains absent.

Every 200 Hz IMU boundary has its own transaction and accounting record. Radio or Pi batching must not move `t0` to a later send time, suppress intermediate transaction IDs, or omit delay spent waiting for a batch.

## Complete measured path

The agreed [threshold-marker extension](imu-trigger-markers.md) adds a separate `t_trigger` on the same ESP32 clock. It leaves every regular `t0`, transaction and deadline unchanged. The proposed primary marker metric is `tr_linked - t_trigger`, where an explicit link identifies the first regular sample captured at or after the trigger. Include the wait for that sample and its ordinary processing; do not use the next arriving response. Uncertain links remain unresolved. Semantic swing/cue endpoints need their own explicit links and separate distributions. The existing 30/40 ms targets and 50 ms expiry do not become trigger-relative limits.

At 200 Hz the nominal sample period is 5 ms. Hardware detector rate, filtering, duration and IRQ handling are separate sources of latency; a delayed RTOS callback cannot stand in for the IRQ edge. Measure pre-IRQ detection delay separately from event-to-response time. The [IMU study](imu-selection.md) records limits and required Zephyr integration for the selected MPU-6050 prototype, including uncertainty when motion and data-ready share its single INT.

The response interval includes controller work after `t0`, wireless delivery, receiver scheduling, Pi queueing, pose lookup and any permitted waiting, the **required ball-state request and response**, fusion/collision calculation, the proposed atomic commit exchange, feedback transmission and complete reception. Electrical-feedback time additionally includes local validation and output scheduling. Retries and queueing are part of the path, not removable measurement overhead.

```mermaid
sequenceDiagram
    participant C as ESP32 controller clock
    participant T as Continuous webcam pose service
    participant P as Raspberry Pi 3 B physics
    participant G as Windows game state service
    participant O as Electrical output
    Note over T,P: Capture and inference run continuously; source time is preserved
    T-->>P: Pose observation with frame ID, quality and clock identity
    Note over C: IMU boundary t0; assign transaction and sample IDs
    C->>P: controller_input
    P->>P: Bounded wait for batch; choose suitable buffered pose
    P->>G: ball_state_request with each transaction query entry
    G-->>P: ball_state_response with shared snapshot and matched entries
    P->>P: Recheck freshness; ordered fusion and collision decisions
    P->>G: Atomic state_update for ordered batch outcomes
    G-->>P: state_commit_result
    P-->>C: Matching feedback_result completely received at tr
    C->>C: Validate and schedule permitted feedback
    C->>O: Electrical output activation t1
    Note over O: Vibration onset and emitted light are separate physical events
```

The diagram shows an accepted batch member. Invalid inputs/tracking can terminate earlier with a correlated failure. Missing delivery terminates locally at the response cutoff, with a counted timeout. Neither becomes an ordinary miss. The per-transaction query identity remains explicit even when several queries share a framed state message and match snapshot.

## Reference timing requirements

All targets are **provisional engineering choices requiring validation** on the actual Pi 3 B, laptop, AP and controllers. A percentile target is a statistical acceptance criterion for a stated experiment, not a guarantee for every transaction. A local expiry is intended program behavior that must itself be verified under overload.

| ID | Start and end event | Reference target or limit | Clock domain | Included and excluded stages | Validation method | Implementation / verification |
| --- | --- | --- | --- | --- | --- | --- |
| T-01 | Controller `t0` to valid matching `tr` | p99 at most 30 ms in the baseline; local timeout at 50 ms | Same ESP32 monotonic clock/session | All application waits, required ball query and commit path; excludes pre-`t0` acquisition, post-receive validation and physical output | Complete transaction ledger, software timestamps and receive marker | Not implemented; not measured |
| T-02 | Controller `t0` to selected electrical `t1` | p99 at most 40 ms for eligible feedback; no gameplay actuation at or after local 50 ms expiry | Same ESP32 clock; common analyzer for electrical verification | T-01 plus validation, scheduling and output delay; excludes physical vibration/light onset | Timestamp plus LED/motor drive trace | Not implemented; not measured |
| T-03 | Successive IMU transaction boundaries | 200 Hz per controller, 5 ms nominal interval; all four controllers yield 800 logical transactions/s | Each ESP32 monotonic clock | Sensor notification/capture and local release behavior; does not prove 800 completed results/s | Interrupt/sample sequence, release jitter and dropped-event counters | Firmware and sensor configuration absent |
| T-04 | Successive physics batch releases and logical steps | 5 ms nominal release/step; batch-service p99 at most 4 ms; at most four catch-up steps and 20 ms simulation lag | Pi monotonic time plus separate logical simulation time | Query, pose validation/fusion, collision and commit service time; collection wait is separate | Release/service/commit traces, queue depth, skipped releases and lag | Scheduler and state service absent |
| T-05 | `t0` to complete input available at Pi application boundary | Routine design allocation 5.5 ms; independently measure its distribution | ESP32 and Pi mapped clocks with uncertainty, or common instrument | Controller preparation and wireless delivery; excludes Pi queue/pose/query/calculation | Mapped software records and GPIO reference where possible | No clock mapping or link measurement |
| T-06 | Physics decision completion to electrical `t1` | p99 at most 15 ms in the baseline | Pi and ESP32 mapping or common instrument | Commit wait, feedback delivery, validation and output scheduling; excludes prior query/fusion and mechanical onset | Decision marker, accepted-commit trace and electrical output | No evidence yet |
| T-07 | Original IMU/pose capture to decision; alignment of a delayed pose with historical IMU | IMU age at most 30 ms; pose age at most 80 ms; plane-position prediction at most 50 ms; historical capture alignment at most 25 ms; network mapping uncertainty at most 2 ms/source and camera timestamp uncertainty at most 8 ms | Mapped source clocks with declared uncertainty | Acquisition age and estimator/transport delay; apply age/alignment/prediction limits including uncertainty; arrival freshness is not capture freshness | Retain capture semantics, mapping IDs, historical sample selection and uncertainty intervals; unknown timing fails the gate | Camera/provider and fusion validation pending |
| T-08 | Identified physical movement to actual LED/display light or vibration | Open: physical-onset target and detection threshold | Independent calibrated instrument/reference | Includes sensor and actuator/display dynamics outside T-01/T-02 | Light barrier/common trigger plus photodiode or vibration sensor | Equipment and experiments not validated |
| T-09 | Query send to complete matching snapshot response | One retry at 2 ms; expiry at 5 ms | Pi local monotonic clock | Both network directions and Windows snapshot-service scheduling | Query identity and local send/receive records | Proposed policy only |
| T-10 | Update send to resolved commit result | Identical retries at 2 ms and 4 ms; pause on ambiguity at 8 ms | Pi local monotonic clock | Network, game commit and response processing | Update identity, deduplication and lost-response injection | Proposed policy only |

For each of one through four controllers, perform three 10-minute baseline runs after separately recorded warmup. One four-controller run nominally starts 480,000 transactions. Require at most 1% late-or-failed attempts, the T-01/T-02 percentile targets, complete failure accounting, zero lost logs for acceptance, and zero observed wrong-player associations, duplicate state commits or stale gameplay actuation. The room, tracking eligibility, input load and rendering/inference workloads must be declared. Report every tracking failure rather than filtering it away; a fault-injection run evaluates correct failure behavior and need not meet the clean-baseline success ratio. These are proposed gates, not evidence that the system passes.

The earlier 25 ms IMU-to-physics discussion is retained as historical context, not the reference's routine uplink allocation. The 15 ms decision-to-electrical target remains a provisional sub-path target. Neither a 25+15 ms sum nor any sum of isolated component percentiles establishes a 40 ms whole-transaction guarantee.

## Routine-path engineering budget

This allocation guides implementation and diagnosis. It is **not measured**, not a worst-case proof, and not a set of independent p99 values that can be added into an end-to-end p99 claim. Measure T-01 and T-02 directly on every controller.

| Stage | Routine allocation | Responsibility |
| --- | --- | --- |
| Interrupt boundary to encoded input handed to transport | 0.5 ms | Zephyr controller interrupt/task/MPU-6050 I²C path; allocation requires measurement |
| Controller-to-Pi wireless and receive scheduling | 5.0 ms | Controller radio, selected external AP or Pi hotspot, and Pi receiver; same provisional allocation for both comparison variants |
| Wait for next eligible 5 ms batch | 5.0 ms | Pi admission/scheduler |
| Pose selection and validity checks | 0.5 ms | Pi fusion input stage |
| Required ball snapshot query and response | 1.0 ms | Wired LAN and independent Windows state service |
| Ordered fusion/collision work for the batch | 0.5 ms | Native Pi physics path |
| Atomic update and commit response | 1.0 ms | Wired LAN and Windows state service |
| Feedback transmission and controller reception | 5.0 ms | Pi sender, AP and controller radio |
| Validation and electrical-output scheduling | 1.5 ms | Controller response and output tasks |
| Routine subtotal through electrical output | 20.0 ms | Complete path |
| Diagnostic margin for ordinary variation | 10.0 ms | Must remain visible in measurements |

The batch service subset above is 3 ms, leaving a 1 ms planning margin against the 4 ms service p99 gate. The separate 40 ms electrical acceptance target leaves room for variation, but it must not justify unbounded feedback queues. Query and commit retries are recovery behavior outside this routine allocation; their local expiry policies protect bounded operation, not successful-delivery deadlines.

Windows snapshot service performance and Pi service time are early feasibility gates. If they cannot meet the measured service profile, first fix avoidable blocking/allocation and separate rendering/inference contention. A slower profile or lower sample rate must be a named, recorded mode with revised requirements; never silently decimate inputs and continue claiming 200 Hz complete processing.

## Bounded scheduling and overload

Four 200 Hz controllers offer 800 logical requests/s. The reference Pi batch has normal occupancy four and capacity eight, at most two per controller, with a queue limit of four per controller. The extra batch capacity permits limited recovery after jitter. One batch is in flight at a time; the PC request and commit remain explicit.

When a batch finishes late, record the missed release. Catch up at most four fixed 5 ms simulation steps without duplicating already integrated time. If lag exceeds 20 ms or a commit remains ambiguous, pause/degrade rather than build an unbounded queue. Identified rejected inputs receive `overloaded`, `stale_input`, `timeout` or the applicable explicit outcome; delivery failure still ends in the controller's own timeout ledger. Never overwrite an admitted request silently with a newer one.

A 5 ms simulation step is a logical resolution, not proof that each network-dependent cycle finishes in 5 ms. The Pi's local scheduler, wired PC exchange, radio path and camera pipeline have separate measurements. `PREEMPT_RT`, CPU affinity and priority can improve local behavior but do not establish a hard bound for the whole system. See [network and host scheduling](networking.md#host-scheduling-profile).

Haptic output cannot produce an independently resolved long vibration pulse for every 5 ms sample. Every transaction still needs a result and receipt timestamp; the reference policy emits a physical cue once per semantic hit or completed missed swing and marks cue eligibility in each result. Non-eligible samples have no `t1` and are counted separately. A dedicated measurement marker may expose per-result receipt without pretending it is motor actuation. A queued or merged effect is not a fabricated electrical response for every input. Hardware-safe pulse duration and event-to-cue behavior require separate validation; see [controller feedback](controller.md).

## Sensor-age and measurement boundaries

The primary transaction does not automatically include IMU conversion, filtering or FIFO residence before `t0`, nor camera exposure and inference that completed before the transaction. A camera frame can be old even when an application RTT is short. A transaction does not trigger a new exposure. Any wait for a usable pose after `t0` remains included in its measured latency.

Preserve source capture time and its meaning, receiver arrival, processing start/completion, send/receive and logical simulation time as distinct fields. The reference fusion aligns each delayed pose with historical IMU observations from the 256-sample controller history, updates the plane-position estimate, then replays inertial orientation to the evaluation time. Do not compare a delayed camera frame only to the latest IMU sample and call the unavoidable sensor-rate difference a synchronization failure. Retain eight poses per person and log the chosen history IDs, input ages, alignment residual and uncertainty. Two old samples can align closely while both are unsuitable. Recheck these conditions after the ball-state response and before committing a candidate. Pose age and prediction limits both apply; the stricter gate controls eligibility.

Single-camera pose inference does not remove time or depth uncertainty. If the camera API only exposes a host-arrival timestamp, record that limitation and characterize the acquisition delay; do not relabel receipt as exposure. A measured exposure-to-pose delay belongs beside the application RTT distribution, not hidden inside a claimed timer resolution.

The agreed clock design maps each source to the Pi monotonic reference as `T_pi = a * t_source + b`, with offset and drift correction. Preserve original times and the Pi-issued mapping ID, source/reference sessions, fit and validity intervals, age and uncertainty. The debug viewer uses the same mapping version as the runtime and shows uncertainty bands and numeric bounds; source/reference restarts and expired or excessive-uncertainty maps forbid future cross-device timing claims while retaining valid historical evidence. Do not use a newly fitted map silently on older events. Local Pi query and commit RTT measurements remain valid without cross-device mapping, but do not separate uplink and downlink latency. See [clock mapping](coordinates-and-time.md#pi-reference-clock-mapping).

For a cross-source interval, conservatively combine the endpoint mapping and event-capture uncertainties without double-counting shared components. Two source bounds of ±2 ms permit ±4 ms relative mapping uncertainty; they do not establish a global ±2 ms timeline. Overlapping time intervals cannot establish a strict temporal order, even when message IDs establish causality. Report unresolved duration/order rather than clamp a negative estimated duration to zero. Same-clock durations avoid cross-source offset error and must be computed directly; local timer scale and boundary uncertainty still apply. These bounds require validation, including asymmetric network delays, rather than a symmetry assumption or RTT/2 claim.

Electrical motor activation differs from physical vibration onset. Processing a scene update differs from display photons. A microsecond-resolution counter does not prove microsecond accuracy. An observed maximum describes a finite experiment, not a proven worst-case bound.

## Practical instrumentation plan

1. Record hardware, firmware/OS/kernel, repository revisions, AP/channel, camera mode/exposure, model/runtime, GPU configuration, player count, workload and all rate/queue/deadline values in a run manifest. Retain warmup and inference/model initialization separately from steady-state trials.
2. Add bounded monotonic timestamps at interrupt, complete message receipt, admission, batch release, query/response, decision, update/commit, feedback and output boundaries. Preserve full correlation identity; do not match traces solely by nearby times.
3. Keep the critical path allocation-bounded and use buffered trace records. Export asynchronously; count trace-buffer overflow, dropped telemetry and capture losses. Compare instrumented versus minimally instrumented runs using external markers.
4. Use GPIO markers and a logic analyzer for the real IMU interrupt, firmware boundary, matching-result receipt and actual LED/motor drive. Record marker skew, instrument sampling rate, timebase accuracy and electrical/reference compatibility.
5. Optionally use photodiodes for LED emission and a dedicated display patch tied to an event ID. Record display refresh, scan position and onset threshold. Frame submission is not a photon timestamp.
6. Optionally measure vibration onset with an independent accelerometer or equivalent sensor. Declare mounting, power, threshold and filtering; distinguish requested intensity, electrical drive and measured motion.
7. For full movement-to-feedback experiments, use an independent calibrated light barrier or equivalent reproducible physical reference. Characterize the relationship between its trigger and the intended swing event, then observe that trigger and output on a common instrument.
8. Exercise the [integration matrix](testing.md) with one through four controllers, simultaneous inputs, CPU/GPU/render load, wireless impairment, stale state/pose, clock faults, overload and service restart. Export raw evidence and report failures.

Packet capture identifies which messages reached an observation point; it does not by itself reveal interrupt time, application processing, commit acceptance or physical actuation. Combine captures with component event records and clock-domain metadata. Keep collector/export work out of the gameplay service path.

## Complete accounting and reporting

Join each measurement by controller ID, controller session and request sequence. Preserve IMU sample IDs, tracking session/frame/person, association and calibration IDs, query and batch IDs, base/committed state version and tick, update/event identity and result. A shared batch ID or event ID cannot replace the per-controller transaction key.

Each started measurement ends in a matching gameplay result, a matching explicit failure, a local terminal failure/timeout, or a still-pending record at the reporting cutoff. Count locally dropped input, remote overload, malformed/unmatched responses, duplicates, stale frames, clock-invalid data, state conflicts, late feedback, trace loss and reconnects separately. A late response is an additional event for an already timed-out transaction, not a second completion.

Report sample counts, median, p95, p99 and observed maximum for application response and eligible electrical feedback, broken down by controller, controller count, condition and outcome. State the percentile estimator and sample population. Include explicit failure responses in overall response distributions and show accepted hit/miss distributions separately. Publish target misses and all failure counts with their denominators.

Timeouts are censored observations: actual response latency is unknown beyond the local cutoff. Do not fill them with zero, the cutoff value or an invented completion, and do not present successful-only percentiles as all-request performance. For electrical metrics, report intentionally absent, suppressed/coalesced and unexpectedly missing outputs separately. A 50 ms timeout does not prove that physical execution always reacts precisely at 50 ms; verify the local watchdog and output cutoff under load.

Report batch occupancy, per-controller queue residence, query/commit RTT, computation time, scheduler lateness, missed releases, catch-up count, simulation lag, pose age, clock uncertainty and observer overhead. Zero observed failures in one run remains evidence only for that run's workload and duration.

## Illustrative arithmetic only

Suppose one controller session records `t0 = 1,000,000 us`, a complete valid response at `tr = 1,024,000 us`, validation completion at `1,025,000 us`, and selected electrical activation at `t1 = 1,027,000 us`. Then application response time is 24 ms and electrical-feedback time is 27 ms. No cross-device clock subtraction is required. These synthetic values are not project measurements and prove nothing about earlier camera/IMU latency or physical output onset.
