# ADR 0003: Application timing and evidence boundaries

[Decision index](README.md)

**Status:** Agreed measurement definitions from the brief; instrumentation is proposed. Recorded 2026-10-24. **Implementation and measurement:** absent.

## Context and decision

The experiment measures a complete application transaction, not a network ping. Capture `t0` at the defined IMU interrupt/measurement boundary, `tr` at receipt of the matching application response, and `t1` at electrical feedback actuation, all on the same ESP32 clock. Report `tr - t0` and `t1 - t0` independently. The proposed precise receipt boundary captures complete framed-message availability and retains it only after validation, as specified in [timing](../timing.md).

These differences require no device-to-device clock synchronization. Cross-device stage duration and sensor alignment do require explicit clock mappings with uncertainty. Preserve original sensor times and distinguish capture, arrival, computation and simulation time.

## Consequences and proposed instrumentation

Include queueing, pose waiting, ball query/response, computation, and any chosen commit-acceptance wait. Exclude unobserved sensor latency before `t0`; pre-existing camera processing is not automatically included. Electrical motor activation is not vibration onset and render processing is not display photons.

Use buffered logs and GPIO markers, then compare software timing to logic-analyzer traces. Optional photodiodes, vibration sensors and an independent calibrated movement reference extend the experiment to physical onset boundaries. Document instrumentation and clock uncertainty.

Report median, tails, observed maximum, deadline misses, timeouts, tracking failures and dropped/discarded records. Do not report only successful events or claim an observed maximum proves a worst-case bound. A network ping, average-only metric or half-RTT one-way estimate cannot substitute for this measurement.

## Validation needed

Declare exact boundaries and provisional/open targets before a run; characterize overhead and resolution versus accuracy. Exercise all [test matrix](../testing.md) cases. The 200 Hz, 5 ms, 25 ms and 15 ms discussion targets are not verified guarantees.
