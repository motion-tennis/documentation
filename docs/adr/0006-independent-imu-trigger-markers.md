# ADR 0006: Independent IMU threshold markers

- Date: 2026-10-25
- Status: **Agreed design** for the unchanged continuous stream and additional traceable hardware marker; **Proposed** correlation details and sensor/runtime choices
- Related: [ADR 0003](0003-application-timing-and-evidence.md), [ADR 0005](0005-webcam-wireless-pi3-masterplan.md), [marker contract](../imu-trigger-markers.md), [IMU selection](../imu-selection.md)

## Context

The user requested a configurable acceleration-threshold IRQ to mark likely swing activity and inspect its complete processing path while preserving the existing continuous data stream. The user also expressed a preference for Zephyr support. A 200 Hz sample rate has a 5 ms period; a sensor's event detector can have a different cadence and filter/duration delay. The previous BMI270/ESP-IDF reference is an unvalidated baseline, not a selected purchase or implementation.

## Decision

Keep the 200 Hz per-controller gameplay stream, wire schema, individual transaction IDs, processing order, priorities, batching and expiry unchanged. Add a diagnostic threshold marker with its own `t_trigger` and session-scoped identity. Export it asynchronously through debug instrumentation and link it explicitly to existing transaction/sample identities; reconstruct the complete query/response/commit/feedback path using those identities. No extra gameplay transaction or priority path is introduced.

The proposed primary endpoint is the response to the first regular sample captured at or after `t_trigger`, with an explicit proven link and the same association. Preserve hardware causative-sample provenance separately. Uncertain links stay unresolved. Existing per-sample `t0`, `tr`, `t1` metrics continue unchanged; trigger-to-response and trigger-to-semantic-cue measurements have separate populations and declared endpoints. A threshold event is a swing candidate, not a confirmed hit.

Evaluate IMUs for appropriate threshold semantics, detector latency, exact 200 Hz acquisition, concurrent interrupt routing and Zephyr driver coverage. Zephyr is a preferred compatibility criterion; firmware framework, exact device, threshold settings and board wiring remain open. Sensor research does not itself activate a different profile or change the frozen gameplay schema.

## Consequences and alternatives

The debug emitter, correlation audit and viewer need new diagnostic records and tests. Missing records, false triggers, marker overhead and uncertain sensor timing remain visible. Existing gameplay messages need no added marker fields. A wire-visible marker would change that contract and requires a separately reviewed protocol revision.

Trigger-gated sending and priority treatment of marked inputs would change the load being measured and contradict the requested continuous stream. A host-only software threshold would not supply the requested independent hardware IRQ reference. Neither is selected by this decision.

## Validation needed

Prove unchanged sampling/traffic behavior, detector and IRQ timing, deterministic correlation, the complete required ball query/response/commit chain, failure accounting and optional cue linkage. Verify driver callbacks against actual interrupt edges and characterize detection delay before claiming physical-motion latency. No hardware, firmware or runtime evidence is established by this ADR.
