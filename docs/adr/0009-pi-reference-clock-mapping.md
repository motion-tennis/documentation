# ADR 0009: Pi-reference clock mapping with drift correction and visible uncertainty

- Date: 2026-10-25
- Status: **Agreed design**; estimator, runtime exchange, debug viewer and measured accuracy are not implemented
- Refines: clock-mapping guidance in [ADR 0003](0003-application-timing-and-evidence.md) and [ADR 0005](0005-webcam-wireless-pi3-masterplan.md)
- Related: [clock contract](../coordinates-and-time.md#pi-reference-clock-mapping), [protocol](../protocol.md), [debug environment](../debugging.md), [implementation gates](../roadmap.md)

## Context and decision

The user approved the Pi as the common time reference, correction for clock drift, and visible timing uncertainty in the debug tool. Four ESP32 clocks and the laptop's declared monotonic clock domains must be comparable for temporal fusion and trace inspection without replacing their original timestamps. Transaction/session/marker IDs establish causal relationships; clock mapping supplies qualified positions and durations on the shared timeline.

Use the Pi monotonic clock and reference session as the experiment time base. Fit `T_pi = a * t_source + b` per declared source clock, correcting both offset and rate drift. Keep native counters running without trace-driven steps. The Pi owns versioned runtime mappings and exports those same immutable versions to debug consumers. Each mapping identifies its source and Pi reference sessions/clocks, fit window, coefficients/anchor, validity interval and uncertainty model. Keep raw exchange evidence and the mapping version used for each temporal decision.

Use four-timestamp `ClockExchange` observations over the existing TCP control connections. The proposed implementation has the Pi initiate exchanges so the mapping owner records the fourth receipt timestamp itself. Timestamp placement, asymmetric WLAN delays, TCP buffering/retries and scheduling require measurement; an RTT/2 assumption does not establish one-way delay or accuracy. Fit/filter/window parameters and the validated error-growth model remain implementation gates.

## Lifecycle and uncertainty

Retain the existing proposed 1 s refresh, 5 s maximum age without a valid update, and 2 ms/source mapping-uncertainty gate. These values are acceptance targets rather than measured capabilities. Account for drift and growing uncertainty between observations; validity ends sooner when bounds become unknown or exceed policy. A source restart invalidates its future mapping. A Pi reference-session restart starts a new reference epoch and requires all participants to establish new mappings. Historical events retain the applicable earlier versions and validity intervals.

Combine different-source mapping and capture uncertainties conservatively. Two ±2 ms source bounds can yield ±4 ms relative mapping uncertainty before additional capture errors. A drift fit or a small residual alone does not validate an uncertainty bound. Same-clock ESP32 sample/marker intervals and Pi query/commit RTT remain available without cross-device mapping; their own timer scale and event-placement errors still require characterization.

## Debug behavior and acceptance

Display uncertainty intervals and numeric bounds on the timeline, with per-source offset at the declared anchor, drift, mapping age/ID, reference epoch and validity status. Do not rely on color alone. Unknown/invalid mappings appear in separate local-time lanes; retain causal ID links, but omit unsupported cross-device durations. Overlapping intervals must not imply a proven total time order. Collector arrival time and file order cannot replace source timestamps. Historical validity is evaluated at the event time, not solely by the mapping's current live status.

Validate known-offset and drift fixtures, jitter/asymmetry, timestamp-boundary delay, outliers, missing records, stale maps, source/Pi restarts and near-simultaneous events. Compare mapped results with independent GPIO/optical references. Require runtime/debug agreement on mapping versions and explicit evidence gaps. Camera exposure-to-timestamp calibration remains separate from laptop-clock mapping. The current offline auditor does not enforce these planned mapping or viewer rules.

## Scope and consequences

The continuous 200 Hz stream, marker-only diagnostic role, gameplay fields, query/response/commit path, timing targets, ports and profile values remain unchanged. No schema/profile revision is needed to record this design; `ClockExchange` already exists. The mapping registry and trace references are a planned diagnostic contract, not a working implementation. Invalid clock evidence must fail freshness-dependent gameplay gates while preserving sampling, local timing and explicit failure accounting.

A design using only an initial offset would miss drift; a timeline ordered only by collector arrival would include export delays. This decision requires original source evidence and qualified conversion. A later estimator or hardware timestamp implementation may improve accuracy without changing these principles, but needs its own measured evidence.
