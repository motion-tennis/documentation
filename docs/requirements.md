# Functional and nonfunctional requirements

[Documentation home](../README.md) · [Architecture](architecture.md) · [Acceptance matrix](testing.md)

**Status:** the following functional requirements are agreed design. Runtime implementation and verification are absent. Proposed mechanisms are linked explicitly; numerical targets remain provisional or open.

## Functional requirements

| ID | Requirement | Acceptance evidence needed |
| --- | --- | --- |
| F-01 | Support one through four players, each using an ESP32 IMU controller over Wi-Fi | Runs with each player count, distinct IDs and no cross-controller feedback |
| F-02 | Start each measurement transaction at the specified IMU interrupt/measurement boundary; record `t0` and a unique request identity | Firmware trace plus GPIO timing, including every generated request |
| F-03 | Use Kinect v2 body and joint data actively with controller measurements to estimate player/racket motion | Traces linking IMU samples, skeleton frames, association and calibration to each decision |
| F-04 | Query the PC game engine for a ball snapshot and receive its version/tick during every valid physics transaction | Correlated `ball_state_request` and `ball_state_response` traces |
| F-05 | Calculate hit/miss, outgoing angle/velocity, and updated ball state on the Raspberry Pi | Deterministic physics fixtures, including boundary cases |
| F-06 | Deliver a matching application result for every admitted measurement, including misses and invalid inputs; record communication failures where delivery is impossible | Complete request/outcome ledger, no omitted failures |
| F-07 | Drive LED and motor feedback that distinguishes hits, misses, tracking errors, and communication errors | Electrical traces and observable fault patterns |
| F-08 | Store committed ball state on the PC, apply physics results, and display player/ball movement and gameplay effects | Query/update/render traces with matching versions and event IDs |
| F-09 | Define ordering, conflict handling, periodic ball movement, and restart behavior without competing state integrators | Tests of the [proposed consistency model](physics.md) |
| F-10 | Preserve identifiers and original sensor timestamps throughout the processing path | Schema and end-to-end trace checks |
| F-11 | Handle controller connection changes, tracking loss, and explicit person reassociation | Fault tests proving old sessions/associations cannot trigger normal feedback |

F-04 does not require invalid inputs to query ball state before rejection. Every decision that uses physics must include the query and response. Every rejected measurement still needs a correlated error or a counted local timeout.

## Nonfunctional requirements

| ID | Requirement | Target and validation |
| --- | --- | --- |
| N-01 | Measure application response and electrical feedback on the controller's clock | [Timing requirements](timing.md); full-transaction deadline is open |
| N-02 | Expose freshness and temporal alignment of IMU and skeleton inputs | Record mapped ages, alignment error and clock uncertainty; thresholds open |
| N-03 | Bound memory use and overload behavior | Proposed queue caps in [protocol](protocol.md); saturate queues in tests |
| N-04 | Make failures visible independently of successful latency samples | Report timeouts, invalid inputs, drops, stale/conflicting results and tracking failures |
| N-05 | Reproduce experiments | Record commits, hardware, software, network topology, trial parameters, warmup and workload |
| N-06 | Keep observation overhead measurable | Buffered logging and GPIO comparison with/without instrumentation |
| N-07 | Keep the interface understandable across component owners | Versioned shared contracts and cross-repository review |
| N-08 | Use English for maintained documentation, diagrams, examples, and new comments | Documentation review; C/C++ comments use `//` |
| N-09 | Respect device power, current, and safe inactive outputs | Review chosen driver/wiring before actuator tests; hardware limits remain open |

## Provisional timing targets

The initial discussion mentioned 200 Hz controller processing, a 5 ms physics tick, 25 ms from IMU boundary to physics receipt, and 15 ms from decision to electrical feedback. These are **provisional design targets**, not benchmarks or promises for the skeleton-dependent application round trip. See [timing](timing.md) for exact proposed event definitions, uncertainty, included stages and unresolved limits.

In particular, 200 Hz processing does not establish a feasible rate of 200 full transactions per second per player. Four such streams would require 800 transactions per second, each with a ball query/response and proposed commit acknowledgement. Measure capacity and agree sampling/admission policy before treating a rate as supported.

## Acceptance gates

1. **Documentation:** links and examples pass checks; component responsibilities and status labels agree.
2. **Contract:** choose and version transport, skeleton provider, hardware, field limits, deadlines, freshness/uncertainty thresholds and actuator limits.
3. **Component:** implement and test validation, deterministic calculations, session fencing, queues, timing hooks and explicit faults.
4. **Integration:** demonstrate the complete mandatory transaction and single committed state owner with one controller.
5. **Measurement:** run the full [matrix](testing.md) with one to four controllers; report distributions and all failures. Passing documentation checks alone satisfies only the first gate.
