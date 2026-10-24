# Physics processing and ball-state consistency

[Documentation home](../README.md) · [Architecture](architecture.md) · [Protocol](protocol.md)

**Agreed design:** physics runs on a Raspberry Pi, combines controller and skeleton measurements, queries PC ball state, calculates hits and outgoing ball motion, and returns controller feedback plus game updates. **Implemented:** no source or runtime exists. **Everything below is a proposed consistency model**, not a claim about current software.

## Ownership and invariants

| Concern | Proposed authority and invariant |
| --- | --- |
| Committed ball snapshot | Game engine stores exactly one current snapshot per `game_session_id` |
| Calculating state changes | One active physics writer, fenced by a game-issued `writer_epoch` |
| Snapshot identity | `(game_session_id, state_version)`; version increments once for each accepted update |
| Simulation time | `simulation_tick` counts fixed integration steps within a session; several events may commit at the same tick |
| State precondition | Game accepts only updates whose `base_state_version` equals its current version |
| Event identity | `event_id` embeds the generating physics session plus a session-local unique ID, so it cannot collide after a writer restart; `update_id` is unique within its fenced writer session |
| Rendering | Reads committed snapshots; visual interpolation never changes committed state |

State version is not a timestamp and not interchangeable with simulation tick. A same-tick hit or miss may increment the version without advancing simulation time. A periodic step advances tick and version. Restarting the game changes `game_session_id`, even if counters reset; old snapshots cannot match the new session.

## Serialized execution

1. Validate and enqueue controller input with the full transaction key. Give arrivals a monotonic Pi-local arrival sequence; break any batched ties by controller ID, session ID, and request sequence. Never order independent devices by unmapped raw timestamps.
2. Maintain one total order shared by controller jobs and periodic movement jobs. Insert periodic jobs on the configured cadence. Do not reorder an older controller job behind newer controller jobs; use bounded queues and reject excess work explicitly.
3. A controller job resolves the current association and calibration, chooses a skeleton frame, and checks input ages/alignment against declared limits. Preserve all selected IDs and original capture times. A failed check returns an explicit error rather than a miss.
4. Send `ball_state_request`; match `ball_state_response` to the query ID, game session, and transaction. A response received after query expiry cannot be used. Allow one outstanding state operation at a time.
5. After the ball response, recheck input age, alignment uncertainty, association/calibration and transaction expiry. From the returned snapshot, integrate any required elapsed steps and evaluate the racket/ball interaction. Use a swept collision test as a candidate to avoid tunneling between samples; geometry, masses, drag, restitution and swing filtering are open algorithm choices.
6. Recheck those validity conditions immediately before submission; if they no longer hold, return an explicit failure without committing the candidate. Submit `state_update` with the exact base version, target tick, candidate state, selected input provenance, and gameplay event. Wait for `state_commit_result` before starting another state operation. Log freshness at the decision/submission boundaries, not only at admission.
7. On acceptance, return `feedback_result` with the committed version and event ID. A valid miss is also a terminal decision and commits an event (and any time advancement), so the UI and controller can refer to the same result.

For two simultaneous controller events, the first admitted job reads version V and commits V+1; the next explicitly queries V+1. This ordering is deterministic from the recorded arrival order, not a fairness guarantee or proof of physical event order. Record cross-controller latency and starvation statistics before accepting the scheduling policy.

## Between controller events

Periodic physics jobs use the same query, integration, version-check, and commit path. They keep the ball moving while no player swings. An initial candidate step is 5 ms; the chosen `tick_duration_us` is session metadata, not inferred from the version counter.

Use one simulation scheduler. At job execution, integrate from the returned `simulation_tick` to the next required target tick; subsequent queued tick jobs already covered by that advancement become accounted-for scheduling skips, not repeated integration. Apply a controller event at the selected current target tick, logging the difference from mapped sensor capture time. No rewind or rollback is included in this initial proposal. Late input outside the agreed age/alignment limit is rejected as `stale_input`; tolerated short pose prediction must be explicitly bounded and logged.

If network or CPU work falls behind, bounded catch-up can calculate several fixed steps in one candidate update. The maximum catch-up steps and acceptable simulation lag are open parameters. Beyond them, pause the simulation and show an explicit degraded state; do not take an unbounded leap or pretend that missed deadlines were met. Render interpolation may improve appearance but does not conceal the lag metric or advance authority.

One outstanding query/update path over a LAN is unlikely to behave like a purely local periodic loop under all loads. Separate scheduler wakeup lateness, computation duration, network waiting, commit latency and simulation lag in measurements. Whether 200 Hz processing and a 5 ms physics target are feasible is unresolved.

## Conflicts and ambiguous commits

| Condition | Proposed behavior |
| --- | --- |
| Base version is stale | Game rejects without mutation, returns current version; physics records `state_conflict` for this input |
| Input result was computed from an old snapshot | Never overwrite current state or relabel it as based on the new snapshot |
| Retry after an ordinary version rejection | Initial model ends the input with `state_conflict`; later transactions query anew. Recalculation retries require a separate bounded policy decision |
| Update accepted, response lost | Pause writer; retransmit exactly the same `update_id` and payload while its epoch and deduplication record remain valid; game returns the original acceptance. A reconnect of the same physics process can resume that epoch only if no replacement writer was admitted |
| Deduplication retention expired or writer replaced while commit is uncertain | Resynchronize or reset the session; never blindly resubmit the event under a new ID. A new writer must resolve or invalidate old outstanding work before resuming play |
| Controller deadline expires before commit resolves | Count timeout; suppress late electrical gameplay feedback. If commit later proves accepted, retain it in game history and record delivery failure separately |
| Duplicate update with changed payload | Reject as protocol violation; it must not become a different commit |
| Duplicate controller transaction | Replay cached terminal result or attach to pending work; do not recompute and actuate twice |
| Game restart | Invalidate outstanding queries, versions and writer epoch; pause, establish a new session and calibrated initial state |
| Physics restart | Acquire a new fenced writer epoch; reject packets from the old writer; reset pending work with explicit controller outcomes where possible |

The game maintains commit deduplication independently of controller feedback caching. Retention must cover the negotiated operation deadline plus retry/reconnect window. Its numeric size/time limit is open and must be finite. Session reset is the safe recovery when the system cannot know whether an old operation committed. This is at-most-once commit within a retained session, not guaranteed exactly-once delivery across crashes.

## Ball initialization, resets, and diagnostics

The game creates an initial snapshot at session start, using agreed court/ball parameters. Those parameters are open. After initialization, start, serve, reset, and pause actions from the UI are commands to the physics writer; the game cannot independently move the ball. A reset either commits through the writer or starts a new game session that invalidates in-flight work.

Trace each decision with transaction identity, association/calibration, selected IMU samples, tracking session/frame, mapped ages and uncertainty, query ID, base version/tick, result version/tick, event/update IDs, queue/processing durations, and commit status. Store outgoing velocity as a vector in the world frame; derive speed and angles with the [protocol convention](protocol.md#units-and-coordinate-semantics), avoiding redundant contradictory values.

Implementation tests should first establish deterministic integration, version-precondition behavior, duplicate handling and restart fencing with synthetic inputs, then run the [integration matrix](testing.md). No physics tests or hardware runs are currently available.
