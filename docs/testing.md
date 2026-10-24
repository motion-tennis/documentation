# Testing and acceptance

[Documentation home](../README.md) · [Development setup](development.md) · [Timing](timing.md) · [Protocol](protocol.md)

## Status and evidence

**Implemented:** documentation validation is available in [`scripts/check_docs.py`](../scripts/check_docs.py). There are no component test suites, executable services, hardware tests, packet captures or latency measurements in the inspected repositories. All runtime checks below are **Proposed acceptance tests**. Their results must be recorded when implementations and equipment exist; this plan is not a claim that the system passes them.

**Agreed design:** the evaluation emphasizes distributed communication, synchronization, data freshness and measurable timing under one through four active controllers. Tracking failures and communication failures must not silently count as misses. Every measurement transaction must have a correlatable terminal outcome, including local timeouts when the network cannot deliver a result.

## Documentation checks available now

Run from `documentation`:

```sh
python3 scripts/check_docs.py
git diff --check
```

Also run `git diff --check` from every changed component repository. The Python checker validates local links/anchors, available sibling-repository links, Markdown fences, JSON syntax and basic Mermaid block structure. It checks the presence of the core architecture, protocol and timing pages and their required transaction/timestamp terms. It does not test a runtime schema or perform full Markdown/Mermaid parsing. A successful exit is evidence of these bounded static checks only.

Manual review must confirm English language, correct hardware roles, consistent status labels and wire names, SI units and coordinate conventions, preserved sensor timestamps, version ownership and measurement definitions. Check that diagrams visibly include both the physics-to-game ball query and the return of the snapshot, that failure arrows do not look like successful gameplay decisions, and that no placeholder commands are presented as runnable software. Render all Mermaid diagrams before accepting a publishing format; record whether a renderer was actually available.

## Test layers to implement

| Layer | Minimum evidence | Acceptance rule |
| --- | --- | --- |
| Message validation | Valid/invalid version, identifier, timestamp, numeric, quaternion and payload fixtures | Invalid input is rejected explicitly; finite values and units obey the contract; the correlation key is preserved when recoverable |
| Controller | Interrupt/sample logs, response matching, actuator markers and output limits | One terminal accounting record per transaction; duplicates do not repeat feedback; errors have explicit behavior; outputs turn off after the bounded duration |
| Tracking | Recorded frame sequences with quality transitions, two-person crossing and loss/reacquisition | Frame IDs and original capture times survive processing; no silent controller/person reassociation; unsuitable data never becomes a normal miss |
| Physics | Deterministic input/state fixtures and concurrent requests | One state writer; query/response preserved; outdated versions cannot overwrite committed state; outcomes reference the actual inputs and versions |
| Game integration | Snapshot service, accepted/rejected update traces and rendered-event records | Atomic version validation and commit; duplicate events do not apply twice; render processing is distinguished from display timing |
| Timing instrumentation | Software log versus logic-analyzer traces | Timestamp boundary and uncertainty are documented; missing samples/log overflow are counted; buffered logging overhead is characterized |

## Proposed integration matrix

Run the baseline for each of **one, two, three and four active controllers** before fault injection. Repeat the relevant fault cases at one and four controllers at minimum, then fill all controller counts when studying load scaling. Do not invent numerical load or fault rates: record the chosen values and repeat count in each run's configuration, and increase them deliberately until the system's admission or timing limits are visible.

| Case | Stimulus and controlled variation | Required observations and acceptance criteria |
| --- | --- | --- |
| Baseline gameplay | Separate known hits and misses; periodic ball motion between swings | Correct outcomes, full query/response trace, consistent state versions, one matching feedback per transaction; missed targets are reported |
| Invalid tracking | Untracked hand, low-confidence pose, occlusion, player leaving view, camera unplug | Explicit `tracking_unavailable` or another applicable failure; no normal miss derived from absent pose; recovery requires valid association/calibration |
| Simultaneous events | Multiple controllers submit around the same scheduling boundary | Recorded deterministic arbitration order; only accepted versions commit; no overwritten hit and no duplicate state/event application |
| CPU load | Load the Pi and PC separately, then together; record utilization and queue occupancy | Queue bounds and timeout/overload behavior hold; latency tails, admission drops and timing-target misses remain visible |
| Rendering load | Vary scene/render load while preserving the same input replay | Snapshot/commit service delays and display delays are reported separately; rendering cannot create a second physics authority |
| Wi-Fi delay and jitter | Inject known delay distributions independently in each direction | Response time includes all waiting; late responses are counted and do not actuate obsolete feedback; one-way delay is not inferred as RTT/2 |
| Packet loss and missing messages | Apply link loss, then separately omit input, query, snapshot, update, commit result and feedback in an application-level harness | Transport retransmission delays and application omissions are distinguished; each missing step yields a counted timeout/error or successful deduplication/reconciliation; no unbounded backlog |
| Duplicates | Replay each message category, including an accepted update and a feedback result | Idempotent updates and bounded event deduplication; no repeated haptic actuation; duplicate counts are retained |
| Reordering | Reorder requests, snapshots, frames, updates and responses | Correlation keys and versions prevent wrong matches; stale data is rejected and counted; outcome order is explainable |
| Stale ball state | Delay a snapshot until a newer state has committed; inject an outdated update | Compare-and-swap rejects the obsolete base version; reconciliation is bounded and logged; no successful feedback for an unaccepted result |
| Stale skeleton data | Freeze capture, delay delivery, deliver out-of-order frames and vary mapping uncertainty | Capture age and alignment checks distinguish old data from recent arrival; explicit stale/invalid outcome with no invented pose |
| Clock faults | Offset/drift change, mapping expiration, controller reboot, counter wrap behavior | Local monotonic intervals remain valid within the session; cross-device comparisons fail closed when uncertainty exceeds policy; no mixed-session subtraction |
| Controller reconnect | Drop Wi-Fi, reboot a controller, then deliver delayed old responses | New session invalidates old responses; person pairing is revalidated; pending transactions and discarded responses are accounted for |
| Tracking restart | Restart acquisition and reuse a numerical person ID in a new tracking session | Old association and frame identity cannot match the new person by accident; readiness is re-established explicitly |
| Physics/game restart | Interrupt each service before/after a commit and before feedback | New service/game session invalidates old work; unknown commit outcomes are reconciled; the ball does not fork into competing histories |
| Queue overload | Submit above admitted capacity, including a non-reading consumer | Bounded memory and queue residence; explicit overload or counted local drop; periodic processing is not allowed to accumulate an unlimited catch-up queue |
| Long idle and no inputs | Leave controllers idle while ball simulation runs; then resume | Periodic physics keeps the ball moving through committed updates; freshness checks still apply after idle; game interpolation never becomes an independent authoritative trajectory |

The proposed TCP transport delivers an ordered byte stream within one connection. Link-level packet duplication or reordering primarily tests transport recovery and head-of-line delay; it does not normally expose duplicated or reordered application messages. Use a future application-level harness to test logical duplication/reordering, and delayed messages across reconnections, separately from Wi-Fi impairments. TCP reliability does not establish that a remote application processed or committed a message.

Where faults are injected by software, record the tool, exact configuration and affected link once a transport and test host are selected. No `netem`, proxy, firmware fault switch or test harness is currently supplied by these repositories.

## Run record and accounting

**Proposed:** retain a manifest for every experiment with run ID, all code revisions, hardware/OS/firmware identifiers, network topology, protocol version, clock mapping parameters and uncertainty, calibration/association versions, test case, controller count, duration, warm-up policy, input rate and all queue/deadline/retry limits. Retain the seed and replay data for reproducible workloads when possible. Warm-up samples may be reported separately, but never silently removed.

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

The 200 Hz controller rate, 5 ms physics tick, 25 ms IMU-to-physics budget and 15 ms decision-to-electrical-feedback budget are **provisional design targets**. Passing a component budget does not establish a complete skeleton-dependent transaction deadline. The full transaction target and target miss-rate limits remain **Open** until agreed. No observed maximum is a proven worst-case bound.

## Acceptance gates

1. Documentation checks pass, diagrams are reviewed, and proposed interfaces have a recorded team decision before interoperable implementations are claimed.
2. Component tests establish correlation, bounds, timestamp preservation and safe feedback behavior using known fixtures.
3. The one-controller smoke test demonstrates both required ball-state arrows and rejects tracking/communication failures explicitly.
4. The full controller-count and fault matrix demonstrates consistent state ownership, bounded recovery and complete accounting.
5. Timing measurements include uncertainty and all failure populations; unresolved targets remain reported as unresolved. A performance acceptance claim requires agreed numerical limits, defined workload and recorded evidence.

The current repositories satisfy neither the runtime nor hardware gates; this document specifies the evidence to collect.
