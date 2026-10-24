# Testing and acceptance

[Documentation home](../README.md) · [Master plan](master-plan.md) · [Development setup](development.md) · [Timing](timing.md) · [Protocol](protocol.md)

## Status and evidence

**Implemented:** documentation validation is available in [`scripts/check_docs.py`](../scripts/check_docs.py), and `debug-units` provides an offline trace checker with synthetic data. There are no running firmware, pose, physics or game services, hardware tests, packet captures or measured latency results. All runtime checks below are **Proposed acceptance tests** for [the shared reference profile](../spec/reference-profile.json). Their results must be recorded when implementations and equipment exist; this plan is not a claim that the system passes them.

**Agreed design:** the evaluation emphasizes distributed communication, synchronization, data freshness and measurable timing under one through four active controllers. Tracking failures and communication failures must not silently count as misses. Every measurement transaction must have a correlatable terminal outcome, including local timeouts when the network cannot deliver a result.

## Documentation checks available now

Run from `documentation`:

```sh
python3 scripts/check_docs.py
git diff --check
python3 ../debug-units/scripts/check_trace.py ../debug-units/examples/synthetic-trace.jsonl
```

The trace command assumes the six repositories are checked out side by side. Its input is explicitly synthetic and cannot establish performance. Review its supported event and timing checks in [debugging](debugging.md); future adapters must also prove that logged events correspond to actual application boundaries.

Also run `git diff --check` from every changed repository. The documentation checker validates local links/anchors, available sibling-repository links, Markdown fences, JSON syntax and basic Mermaid block structure. It checks the presence of core architecture, protocol and timing definitions. It does not execute generated Protocol Buffers handlers or perform full Markdown/Mermaid parsing. A successful exit is evidence of these bounded static checks only.

Manual review must confirm English language, correct hardware roles, consistent status labels and wire names, SI units and coordinate conventions, preserved sensor timestamps, version ownership and measurement definitions. Check that diagrams visibly include both the physics-to-game ball query and the return of the snapshot, that failure arrows do not look like successful gameplay decisions, and that no placeholder commands are presented as runnable software. Render all Mermaid diagrams before accepting a publishing format; record whether a renderer was actually available.

## Test layers to implement

| Layer | Minimum evidence | Acceptance rule |
| --- | --- | --- |
| Message validation | Valid/invalid version, profile hash, identifier, timestamp, numeric, quaternion and payload fixtures; shared Protocol Buffers examples in every implementation language | Reject incompatible versions, nonfinite values, excessive arrays, missing correlation and datagrams above 1,200 bytes before state changes; verify generated encoders agree on actual bytes and field semantics |
| Controller | Interrupt/sample logs, response matching, actuator markers and output limits | One terminal accounting record per transaction; duplicates do not repeat feedback; errors have explicit behavior; outputs turn off after the bounded duration |
| Tracking | Four-person webcam recordings with quality transitions, crossings, depth-plane departures and loss/reacquisition | Frame IDs and original timing semantics survive processing; no silent person reassociation; 2.5D projections are never presented as measured 3D; unsuitable data never becomes a normal miss |
| Physics | Deterministic historical IMU/pose fixtures, concurrent requests and variable batch occupancy | One state writer; every admitted transaction retains a query/response entry; old versions cannot overwrite committed state; atomic batches preserve deterministic order and per-input outcomes |
| Game integration | Snapshot service, accepted/rejected update traces and rendered-event records | Atomic version validation and commit; duplicate events do not apply twice; render processing is distinguished from display timing |
| Timing instrumentation | Software ledger versus packet/GPIO/optical traces, plus malformed/missing-event fixtures for the offline checker | Timestamp boundaries and uncertainty are documented; missing samples/log overflow are counted; buffered logging overhead is characterized; a synthetic trace pass is not a physical timing result |

## Proposed integration matrix

Run **three 10-minute baseline trials at each of one, two, three and four active controllers**, with separately recorded warmup. At 200 Hz per controller, a four-player trial nominally starts 480,000 measurement transactions. Retain every started transaction, including failures. Repeat relevant fault cases at one and four controllers at minimum, then fill intermediate counts when studying scaling. Record injected load, delay/loss distributions, seeds and affected links; increase them deliberately until admission and timing limits are visible.

Proposed clean-baseline gates: application-response p99 at most 30 ms, eligible electrical-feedback p99 at most 40 ms, at most 1% late-or-failed attempts, zero wrong-player associations, zero duplicate commits, no gameplay output after local 50 ms expiry, and zero log loss for acceptance. Report target misses with their full denominators. Do not count a timely tracking-error response as a successful gameplay decision; it remains a failure outcome. Fault-injection trials evaluate bounded failure/recovery and do not inherit the clean-baseline success-ratio requirement.

| Case | Stimulus and controlled variation | Required observations and acceptance criteria |
| --- | --- | --- |
| Baseline gameplay | Separate known hits and misses; periodic ball motion between swings | Correct outcomes, full query/response trace, consistent state versions, one matching feedback per transaction; missed targets are reported |
| Invalid tracking | Untracked hand, low-confidence pose, occlusion, player leaving view, camera unplug | Explicit `tracking_unavailable` or another applicable failure; no normal miss derived from absent pose; recovery requires valid association/calibration |
| Simultaneous events | Multiple controllers submit around the same scheduling boundary | Recorded deterministic arbitration order; only accepted versions commit; no overwritten hit and no duplicate state/event application |
| Batch occupancy and fairness | Batches of 0, 1, 4 and 8 inputs; two inputs per controller; attempt a third from one controller and overflow the four-entry queue | Preserve each transaction/query key; obey eight-total/two-per-controller caps, fair selection and deterministic event order; overflow is explicit, never silent coalescing |
| Atomic batch failure | Drop or invalidate one query entry; duplicate a complete batch; alter a duplicate payload; inject an invalid event in an update | Matched query entries are required before calculation; a state update either commits once in its entirety or not at all; no partial commit or positive feedback for an unaccepted member |
| Lost commit result | Lose the first reply, then all replies; deliver a retained acceptance after controller expiry | Identical update retries at 2 and 4 ms; ambiguity pauses at 8 ms; no concurrent next batch or fresh-ID replay; the controller's 50 ms expiry still suppresses late cues |
| CPU load | Load the Pi and PC separately, then together; record utilization and queue occupancy | Queue bounds and timeout/overload behavior hold; latency tails, admission drops and timing-target misses remain visible |
| Rendering load | Vary scene/render load while preserving the same input replay | Snapshot/commit service delays and display delays are reported separately; rendering cannot create a second physics authority |
| GPU inference contention | Run the four-person model with rendering, model warmup, device/provider failure and a deliberately slow inference path | Record actual GPU provider, processing time and dropped capture frames; no silent CPU fallback or frame backlog; snapshot replies remain independent of inference completion |
| Wi-Fi delay and jitter | Inject known delay distributions independently in each direction | Response time includes all waiting; late responses are counted and do not actuate obsolete feedback; one-way delay is not inferred as RTT/2 |
| Packet loss and missing messages | Apply link loss, then separately omit input, query, snapshot, update, commit result and feedback in an application-level harness | Distinguish Wi-Fi retries from application retries; inputs are not retransmitted, query retries once and expires at 5 ms, commit ambiguity is bounded; every missing stage yields an explicit failure or counted local timeout |
| Duplicates | Replay each message category, including an accepted update and a feedback result | Idempotent updates and bounded event deduplication; no repeated haptic actuation; duplicate counts are retained |
| Reordering | Reorder requests, snapshots, frames, updates and responses | Correlation keys and versions prevent wrong matches; stale data is rejected and counted; outcome order is explainable |
| Stale ball state | Delay a snapshot until a newer state has committed; inject an outdated update | Compare-and-swap rejects the obsolete base version; reconciliation is bounded and logged; no successful feedback for an unaccepted result |
| Stale skeleton data | Freeze capture, delay delivery, deliver out-of-order frames and vary mapping uncertainty | Capture age and alignment checks distinguish old data from recent arrival; explicit stale/invalid outcome with no invented pose |
| Historical fusion alignment | Delay a usable pose while supplying current and historical IMU samples; exceed prediction or age limits independently | Align the pose to historical samples, replay orientation and retain selected IDs; apply IMU 30 ms, pose 80 ms, prediction 50 ms and alignment 25 ms limits including uncertainty; a recent arrival cannot refresh capture time |
| Plane calibration | Known hand positions in and out of the declared interaction plane, mirrored image, camera movement and player lane changes | Validate projected-plane error against fixtures; do not apply a floor homography to raised hands; invalidate moved calibration; declare unsupported depth motion instead of inventing metric 3D |
| Clock faults | Offset/drift change, mapping expiration, controller reboot, counter wrap behavior | Local monotonic intervals remain valid within the session; cross-device comparisons fail closed when uncertainty exceeds policy; no mixed-session subtraction |
| Controller reconnect | Drop Wi-Fi, reboot a controller, then deliver delayed old responses | New session invalidates old responses; person pairing is revalidated; pending transactions and discarded responses are accounted for |
| Tracking restart | Restart acquisition and reuse a numerical person ID in a new tracking session | Old association and frame identity cannot match the new person by accident; readiness is re-established explicitly |
| Physics/game restart | Interrupt each service before/after a commit and before feedback | New service/game session invalidates old work; unknown commit outcomes are reconciled; the ball does not fork into competing histories |
| Queue overload | Submit above admitted capacity, including a non-reading consumer | Bounded memory and queue residence; explicit overload or counted local drop; periodic processing is not allowed to accumulate an unlimited catch-up queue |
| Pi power and thermal load | Use the actual Pi 3 B with sustained CPU/network load; record power/thermal/throttling indications | No hidden reduction in service capacity; count delayed releases and pause beyond 20 ms lag; no inference or synchronous disk logging moves onto the physics path |
| Debug consumer failure | Stop collector/viewer, saturate trace buffers, drop telemetry packets and lose packet-capture records | Gameplay remains independent; every observer loss is counted; an incomplete trace cannot pass complete-accounting acceptance |
| Long idle and no inputs | Leave controllers idle while ball simulation runs; then resume | Periodic physics keeps the ball moving through committed updates; freshness checks still apply after idle; game interpolation never becomes an independent authoritative trajectory |

The reference gameplay/pose transport is UDP: loss, duplication and reordering are application concerns. Link-layer Wi-Fi retries do not establish application processing or commit. Control-plane TCP remains an ordered stream; test its framing and reconnect behavior separately, and do not treat a control receipt as completion of a gameplay transaction. Use the planned application-level harness for reproducible message faults alongside actual wireless impairments.

Where faults are injected by software, record the tool, exact configuration and affected link. The offline checker is implemented; a live fault proxy, firmware fault switch, simulation/replay stack and collector are still planned in `debug-units`. See [debug environment](debugging.md) for those boundaries.

## Run record and accounting

**Proposed:** retain a manifest for every experiment with run ID, all six repository revisions, profile/schema hashes, hardware/OS/kernel/firmware and GPU/provider/model identifiers, camera configuration, network topology/channel, protocol version, clock mappings and uncertainty, calibration/association versions, test case, controller count, duration, warm-up policy, input rate and queue/deadline/retry limits. Retain seeds, replay data and byte-level packet evidence where possible. Warm-up samples may be reported separately, but never silently removed.

Join logs by `(controller_id, session_id, request_seq)` and record the selected IMU sample IDs, skeleton session/frame/person, ball base and committed version/tick, feedback/event ID and outcome. Preserve capture time, arrival time, processing completion, simulation time, `t0`, `tr` and `t1` as distinct fields with explicit clock domains. Mark unavailable fields as unavailable rather than synthesizing timestamps.

Account for each started measurement as one of:

- A matching application response with a gameplay outcome (`hit` or `miss`).
- A matching explicit failure response, such as invalid input, tracking failure, stale input, state conflict, overload or internal error.
- A local terminal failure/timeout because no matching result was received by the configured deadline, including an input discarded before transmission or admission.
- Still outstanding at the reporting cutoff, with its age and a reason it has not yet reached its deadline.

Track dropped inputs, malformed messages, duplicate requests/responses, stale frames, rejected state updates, discarded late responses, retry attempts, reconnections and log overflow as separate counters. Avoid counting a late response as a second completed transaction: it is an additional diagnostic event for a transaction already timed out. If a malformed input has no recoverable correlation key, retain its receiver counter and diagnostic reason; the originating controller's pending transaction must still terminate locally.

## Required reporting

Report sample count, median, p95, p99 and **observed maximum** for application response time `tr - t0` and time to electrical feedback `t1 - t0`, separately by controller count, test condition and outcome. State the percentile method and include the count supporting each tail statistic; a small sample does not justify a reliable tail estimate. Include explicit failure responses in overall application-response statistics, and publish successful hit/miss distributions separately so filtering is visible.

For every target report deadline misses as both counts and fractions, with a declared denominator. Also report input drops, timeouts, tracking failures, state conflicts, late/discarded responses and missing instrumentation. A timeout is a censored observation: its actual response latency is unknown beyond the wait limit, not a zero, a fabricated deadline-valued completion, or a sample to silently omit. Include censored counts beside completion percentiles and count them against transaction-level service objectives where applicable. If electrical actuation does not occur for an error policy, mark `t1` not applicable and report that count separately.

Report selected skeleton age and IMU/skeleton alignment error together with mapping uncertainty, queue residence, computation duration and game-service request/response duration where measured in valid clock domains. Report the effective periodic tick interval and missed ticks under load. Do not subtract clocks from different devices without a validated mapping.

The [reference profile](../spec/reference-profile.json) defines proposed 200 Hz controller and 5 ms physics rates, 30 ms response/40 ms electrical p99 targets, 50 ms local expiry and the 1% late-or-failed baseline limit. The earlier 25 ms input budget is historical; the 15 ms decision-to-electrical target remains a provisional diagnostic sub-path target. Passing a component budget or adding stage percentiles does not establish an end-to-end guarantee. No observed maximum is a proven worst-case bound.

## Acceptance gates

1. Documentation checks pass, diagrams are reviewed, and proposed interfaces have a recorded team decision before interoperable implementations are claimed.
2. Component tests establish correlation, bounds, timestamp preservation and safe feedback behavior using known fixtures.
3. The one-controller smoke test demonstrates both required ball-state arrows and rejects tracking/communication failures explicitly.
4. The full controller-count and fault matrix demonstrates consistent state ownership, atomic batches, bounded recovery, correct 2.5D calibration and complete accounting.
5. Three 10-minute trials per controller count meet the declared reference targets with uncertainty and all failure populations reported. Any revised slower profile is named and versioned rather than silently changing rates or dropping inputs. Unresolved physical-onset accuracy remains explicitly unverified.

The current repositories satisfy neither the runtime nor hardware gates; this document specifies the evidence to collect.
