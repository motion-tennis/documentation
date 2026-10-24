# Timing requirements and measurement methodology

[Documentation home](../README.md) · [Controller](controller.md) · [Clock domains](coordinates-and-time.md) · [Test matrix](testing.md)

**Agreed design:** evaluate the complete application transaction and its electrical feedback, preserve measurement identities and source timestamps, and account for failures. **Proposed:** precise instrumentation boundaries, stage metrics, and the experimental procedure below. **Open:** final deadlines, allowable miss rates, clock uncertainty limits, and hardware instrumentation. **Implemented:** no firmware timing hooks, running services, or hardware measurements exist; numerical values on this page are targets or illustrative arithmetic, never measured performance.

## Primary controller measurements

Use the same monotonic ESP32 timer and the same controller boot/session for all three timestamps:

| Timestamp | Event and recording rule |
| --- | --- |
| `t0` | The specified IMU interrupt or measurement boundary that starts the identified transaction. Prefer a hardware-captured interrupt edge if the selected board supports it; otherwise record the earliest bounded handler timestamp and characterize its delay from the electrical interrupt edge. Declare the chosen boundary in every run. |
| `tr` | End of reception of the complete matching `feedback_result` at the controller's application receive boundary. Capture the candidate time when the complete framed message becomes available, then retain it as `tr` only after identity, protocol, payload, and expiry validation succeed. A receipt acknowledgement or an incomplete message is not this event. |
| `t1` | The electrical transition that starts the selected feedback output for this transaction, such as the LED drive transition or motor-driver enable/PWM start. A function call that merely queues output is not electrical actuation. Record a software timestamp at the closest supported boundary and verify the difference with an electrical trace. |

**Application response time:** `L_response = tr - t0`.

**Time to electrical feedback:** `L_electrical = t1 - t0`.

These local differences do **not** require synchronized clocks across the ESP32, Raspberry Pi, Kinect, or PC. They do require a monotonic timer, correct wrap handling, stable units, and no subtraction across reboots. A local timer's scale error still affects elapsed-time accuracy. See [clock domains](coordinates-and-time.md).

The proposed `tr` boundary excludes parsing/validation that occurs after the complete message becomes available. Record optional `t_validated` on the same timer to expose that work. Validation, feedback queueing, and output scheduling are included in `t1 - tr`. Discarded malformed, expired, wrong-session, or duplicate messages retain diagnostic receipt timestamps but do not become a new `tr` or a new actuation. If an implementation chooses completion of validation as its application boundary instead, name that metric separately and never mix its samples with this definition.

When LED and motor activate at different times, retain `t_led` and `t_motor`, report both relevant intervals, and state which defines the headline `t1`. A motor-off error policy has `t_motor = null`/not applicable; do not manufacture an actuation timestamp. A visible error pattern can still have a valid `t_led`, reported in its own outcome population. A local timeout may produce a fault indication without a received application response: record its deadline and output times while leaving `tr` absent.

## Included stages and boundaries

The application measurement includes controller acquisition work after `t0`, transmission, Wi-Fi and receiver scheduling, physics queueing, association and pose selection, any bounded pose wait, the **required ball-state request and response**, physics calculation, result transmission, and application reception on the controller. The [proposed consistency model](physics.md) also waits for a state update and commit result before normal hit/miss feedback; that additional PC exchange is included. Retransmissions, contention, and associated waiting are part of the measured path, not removable overhead.

`L_electrical` additionally includes response validation after `tr`, local feedback queueing, actuator scheduling, and electrical output delay. Concurrent feedback must have identifiable per-event boundaries; merged or overwritten pulses cannot silently stand in for individual measurements.

```mermaid
sequenceDiagram
    participant S as IMU / earlier sensor processing
    participant C as ESP32 clock and controller
    participant T as Continuous Kinect tracking
    participant P as Raspberry Pi physics
    participant G as PC game state
    participant O as Electrical feedback output
    S->>C: Specified interrupt / measurement boundary t0
    Note over C: Begin application response and electrical-feedback intervals
    C->>P: controller_input
    T-->>P: Buffered skeleton frame with original capture timestamp
    Note over T,P: Capture can precede t0; pose waiting after t0 is included
    P->>G: ball_state_request (required)
    G-->>P: ball_state_response (required)
    P->>P: Calculate result; record decision completion
    P->>G: state_update (proposed commit path)
    G-->>P: state_commit_result (proposed)
    P-->>C: Complete matching feedback_result at tr
    Note over C: Application response time ends at tr
    C->>C: Validate, match and schedule output
    C->>O: Electrical transition at t1
    Note over C,O: Electrical-feedback interval ends at t1
    Note over O: Light emission and vibration onset are separate physical events
```

The diagram shows a successful valid-input path. Invalid tracking or input can terminate earlier with a correlated error; absence of any timely matching response ends in a counted timeout. Neither is silently reclassified as a normal miss.

The following are outside the primary measurement unless separately instrumented:

- IMU conversion, filtering, FIFO residence, and physical movement before `t0`. An interrupt may report a sample captured earlier.
- Kinect exposure and skeleton processing that occurred before the transaction. Continuous tracking does not acquire a new frame just because a controller sends a request. Capture age is a separate metric; any wait for an acceptable frame during the transaction remains included.
- Mechanical motor vibration onset after the electrical drive transition. Motor ramp-up depends on the chosen hardware, power, mounting, and detection threshold.
- LED light emission after the electrical transition, and actual PC display photons. Game acceptance, scene processing, render submission, and screen presentation are distinct boundaries.

A timestamp with microsecond resolution does not establish microsecond accuracy. Interrupt scheduling, software placement, electrical marker skew, quantization, oscillator error, instrument bandwidth, and reference calibration all contribute error. An observed maximum is the largest value in a stated finite experiment; it is not a proven worst-case execution-time or end-to-end bound.

## Timing requirements table

Every implementation/verification cell remains unavailable until code and evidence exist. Targets need a declared workload, sample population, and acceptable miss rate before they can become performance acceptance criteria. The four numbers from the initial discussion are **provisional design targets**, not demonstrated capabilities.

| ID | Start and end event | Target | Clock domain | Included and excluded stages | Validation method | Current implementation and verification |
| --- | --- | --- | --- | --- | --- | --- |
| T-01 | `t0` to `tr` | **Open:** complete application deadline and allowed miss rate | One ESP32 monotonic clock/session | Includes queueing, pose waiting, required ball query/response, calculation and proposed commit exchange; excludes pre-`t0` acquisition, post-`tr` validation and physical output | Correlated software trace plus controller GPIO/analyzer check; all outcomes and censored timeouts | Not implemented; no measurements |
| T-02 | `t0` to chosen electrical `t1` | **Open:** complete feedback deadline and allowed miss rate | One ESP32 clock; electrical verification uses one analyzer timebase | T-01 plus validation and output scheduling; excludes vibration/light onset after the transition | Software markers compared with actual LED/motor drive traces | Not implemented; no measurements |
| T-03 | Successive controller processing releases and their execution | **Provisional:** 200 Hz nominal processing, equivalent to a 5 ms period; execution deadline open | ESP32 monotonic clock | Local processing cadence; does not require or prove 200 completed network transactions per second | Release/start/finish logs, jitter and skipped-release counters under load | No scheduler or firmware; not verified |
| T-04 | Successive periodic physics releases and logical simulation steps | **Provisional:** 5 ms nominal tick; allowed release jitter, commit delay and lag open | Pi monotonic scheduler clock plus separate logical simulation ticks | Periodic release and fixed integration step; query/commit waiting must be reported separately and may prevent this cadence | Release/compute/commit trace, missed ticks and simulation-lag measurement | No scheduler or simulation; not verified |
| T-05 | Specified controller `t0` to complete `controller_input` available at the Pi application receive boundary | **Provisional:** at most 25 ms; permissible miss rate open | ESP32 and Pi require a validated mapping with uncertainty, or a common instrument | Includes post-`t0` controller work, transport and scheduling up to complete application receipt; excludes later Pi validation/queueing, pose wait, ball query, decision and feedback | Mapped software timestamps and, where practical, GPIO/common-reference measurement | No transport or mapping; not verified |
| T-06 | Physics calculation complete to selected electrical `t1` | **Provisional:** at most 15 ms; permissible miss rate open | Pi and ESP32 require validated mapping or a common instrument | Includes proposed state commit round trip, feedback transmission, validation and actuation queueing; excludes earlier pose/query/calculation and later vibration onset | Decision marker, mapped controller timestamp and output trace | No calculation or commit path; not verified |
| T-07 | Selected IMU/skeleton capture to physics decision; difference between selected capture times | **Open:** maximum IMU age, pose age, alignment error and mapping uncertainty | Source clocks mapped into common experiment time | Includes source acquisition age, buffering and transport; arrival freshness cannot replace capture age | Preserve source timestamps and mapping IDs; report age/alignment intervals and rejected-data counts | No provider, fusion or synchronization; not verified |
| T-08 | Identified movement reference to actual LED/display light or vibration onset | **Open:** full physical response targets and detection thresholds | Independent calibrated reference/instrument timebase | Includes physical acquisition and output dynamics excluded by T-01/T-02; each output is a distinct metric | Calibrated light barrier/common trigger plus photodiode or vibration sensor | No physical experiment or apparatus selected; not verified |

T-05 and T-06 do not cover the middle stages of a transaction and must not be added to claim a 40 ms end-to-end guarantee. A 5 ms logical physics step does not imply every network-dependent query/commit finishes in 5 ms. Similarly, 200 Hz local processing does not establish a transaction admission rate: four controllers at 200 requests/s would offer 800 full transactions/s to one serialized physics writer. Measure achievable capacity and settle admission policy before claiming support.

## Correlation and stage timestamps

Join a measurement by `(controller_id, session_id, request_seq)`, preserving IMU sample IDs, tracking session and skeleton frame/person ID, association/calibration version, ball query ID, base and committed state version, simulation tick, and update/gameplay/feedback event identity. Use the [protocol](protocol.md) for exact fields. An event ID alone cannot replace the originating request key.

Keep original sensor and frame timestamps unchanged. Append arrival, processing start/completion, send/receive, queue occupancy, and commit timestamps with their clock domain and event meaning. Logical simulation time describes which simulated state was evaluated; it is not a wall-clock timestamp. Log the difference between the selected simulation evaluation instant and mapped sensor capture time so delayed processing remains visible.

For each decision, record IMU age, skeleton age, capture-time alignment residual, mapping uncertainty, selection policy, and any interpolation/prediction horizon. Close temporal alignment does not establish freshness: two equally old samples may align perfectly. Reject missing, stale, or unacceptably uncertain inputs under the [temporal fusion policy](coordinates-and-time.md#temporal-fusion-policy).

Cross-device subtraction requires an explicit clock mapping or synchronization method and an uncertainty estimate valid for that interval. Neither recent packet arrival nor an unsynchronized timestamp is evidence of capture freshness. Do not assume half the RTT equals one-way delay; asymmetric wireless paths, queueing, and endpoint scheduling make that unsupported. A local Pi measurement of query send to matching response receipt is valid without clock synchronization, but cannot separate the two one-way network delays.

## Practical measurement plan

1. **Specify the run.** Record component revisions, hardware, firmware/OS, sensor/backend configuration, network topology, controller count, input rate, load/fault parameters, sample count or duration, warm-up policy, deadlines, queue bounds, calibration, and clock mapping. Declare the precise `t0`, `tr`, `t1`, decision-completion, and capture boundaries before collecting results.
2. **Add bounded software timestamps.** Capture monotonic timestamps at those boundaries and at queue, query/response, compute, commit, and render stages. Keep interrupt work short. Preserve complete transaction identities; do not associate records merely by nearby timestamps.
3. **Verify with GPIO markers and a logic analyzer.** Mark interrupt handling, result reception, calculation completion where accessible, and output scheduling. Observe the actual IMU interrupt and LED/motor drive signals as well. Use one instrument timebase for signals that can be safely connected; verify ground/reference and electrical compatibility for the selected hardware. Measure marker-to-event skew and instrumentation overhead.
4. **Measure optical output when needed.** Use a photodiode with a recorded threshold to detect LED emission or a controlled display patch tied to a specific event. Display buffering, refresh, scan position, and sensor response affect the result. Align the optical trace to the same reference trigger; rendering code completion is insufficient.
5. **Measure vibration onset separately when needed.** Use an independently mounted accelerometer or another suitable sensor, declare an onset threshold and filtering method, and control mounting and power. Separate commanded drive, electrical motor activation, and detected motion. Do not assume a firmware pulse establishes perceptible vibration.
6. **Run a full movement-to-feedback experiment.** Use an independent calibrated light barrier or equivalent physical reference crossed by a repeatable moving target. Define the reference's geometric relationship to the swing/collision event and characterize sensor/detection delay. Capture its trigger and the chosen optical or mechanical response with a shared timebase. This tests the physical path without redefining `t0` as an unmeasured motion onset.
7. **Buffer and quantify observation overhead.** Write fixed-size timestamp/identity records to bounded memory, then flush outside the critical path or after the trial. Avoid synchronous console, disk, or network logging on the measured path. Count dropped log records and compare an instrumented run against a minimally instrumented run using external markers. Report any change caused by logging.
8. **Run the complete matrix.** Follow [testing](testing.md), including one through four controllers, simultaneous events, tracking loss, CPU/rendering load, wireless impairments, stale versions/frames, queue overload, and service restarts. Repeat runs and retain failures and the raw evidence.

The GPIO/analyzer path provides an independent check on software timestamp placement, not automatic calibration of all sensor and clock errors. Report instrument sample rate, timing uncertainty, threshold choice, reference calibration, wiring-induced delay where relevant, and clock-mapping uncertainty. State whether uncertainty is bounded analytically, calibrated, or estimated from observed residuals.

## Complete accounting and reporting

Every started measurement must end in a correlatable application result, including valid misses and invalid-input/tracking outcomes, or an explicit local terminal failure when a response cannot be delivered. Count locally dropped inputs, service rejections, missing responses, timeouts, and discarded late/wrong-session/duplicate responses. Keep pending-at-cutoff records visible. A late response can add reconciliation information but cannot become a second completion or trigger expired gameplay feedback.

Report sample count, median, p95, p99, and observed maximum for `L_response` and applicable `L_electrical`, with the percentile method and workload. Break them down by controller count, load/fault condition, and outcome. Include explicit failure responses in the overall response distribution, and show successful hit/miss distributions separately. Report deadline misses with denominators, timeouts, tracking failures, overload, state conflicts, dropped inputs, discarded responses, and missing/log-overflow records alongside the distributions.

A timeout is a **censored observation**: no valid response arrived within the declared interval, and its eventual completion latency may be unknown. Do not insert zero or the deadline as a fabricated completion latency, omit its count, or present successful percentiles as the experience of all requests. For electrical statistics, declare the population eligible for actuation and report both intentionally absent outputs and unexpectedly missing outputs. Once deadlines are agreed, count timeouts beyond a service deadline against its service objective according to the published rule.

Also report queue residence, local query and commit round trips, computation duration, scheduling jitter, effective periodic intervals, missed ticks, simulation lag, input ages/alignment, and uncertainty where available. Observing no deadline miss in a finite run is evidence only for that workload and duration, not proof of a hard real-time bound.

## Illustrative arithmetic only

The following values are synthetic and do not describe project performance. Suppose one controller session records `t0 = 1,000,000 us`, complete valid response reception `tr = 1,042,000 us`, validation completion at `1,043,000 us`, and motor electrical activation `t1 = 1,045,000 us`.

- Application response time is `42 ms`.
- Time to electrical feedback is `45 ms`.
- Validation and output scheduling after reception occupy `3 ms`, including `1 ms` through validation completion in this example.

No cross-device synchronization is needed for those subtractions. They say nothing by themselves about the IMU's earlier internal latency, the selected skeleton's age, one-way network delay, actual vibration onset, display photons, or satisfaction of a complete transaction deadline, which remains open. If a different request times out, it adds a censored outcome and failure count rather than a fabricated fourth timestamp.
