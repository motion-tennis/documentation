# Pi 3 sensor fusion, scheduling and ball consistency

[Documentation home](../README.md) · [Master plan](master-plan.md) · [Protocol](protocol.md) · [Profile](../spec/reference-profile.json)

**User-confirmed hardware:** Raspberry Pi 3 Model B. **Proposed implementation:** C++20/CMake, 64-bit Raspberry Pi OS Lite, bounded native data structures and nonblocking sockets. No runtime implementation or performance test exists. Do not run camera inference or rendering on this Pi.

## Process and thread responsibilities

Use one physics process with separate I/O, simulation and trace-export tasks. Start with a normal scheduler to establish a baseline; evaluate a verified PREEMPT_RT kernel and fixed-priority scheduling only after bounded execution and starvation controls are tested. Reserve one CPU for the simulation task when measurement justifies it; do not blindly pin USB/Ethernet IRQ work onto the same overloaded core. No allocation, synchronous logging, DNS, model inference, file I/O or blocking network read belongs in the simulation tick.

The I/O task timestamps receipt, validates bounded messages and writes controller queues/pose history. The simulation task owns all mutable fusion, swing and candidate-ball state. It polls completion records from I/O and advances a nonblocking batch state machine. Trace export drains a bounded buffer; full buffers increment loss counters, never block physics. Pin and profile real thread priorities/affinities in the run manifest; they are not guarantees from documentation alone.

## Temporal and spatial fusion

Maintain 256 time-ordered IMU samples per controller (1.28 s at 200 Hz) and eight poses per person. This history remains after transaction completion because delayed camera observations need historical alignment. Preserve original timestamps, source clock IDs and association/calibration versions.

1. Calibrate sensor axes, bias, neutral grip and controller-to-racket offset. Integrate gyroscope orientation with a normalized quaternion; use gravity-direction correction only when acceleration magnitude/dynamics permit it. Do not subtract gravity in an unknown frame or infer absolute yaw from six-axis data.
2. Map a new camera capture into the common experiment timeline. Find bracketing historical IMU samples and interpolate orientation at that capture time. Their alignment error plus propagated uncertainty must fit the 25 ms limit; log both sample IDs. Never pretend the latest IMU sample was captured simultaneously with an old image.
3. Convert the selected wrist ray into the calibrated player interaction plane. Apply a bounded constant-velocity alpha-beta position update in that plane; start with proposed alpha 0.7 and beta 0.1, then tune against recorded trajectories. Use actual mapped time deltas, not assumed camera cadence. Reject ambiguous identities and invalid geometry.
4. Replay buffered angular rates from the observation time to the transaction evaluation time. Predict plane position by velocity for at most 50 ms, including uncertainty. Do not double-integrate accelerometer data into long-term racket position. Do not apply magnetic heading correction unless a future sensor/profile explicitly adds it.
5. Check pose age at most 80 ms, current IMU age at most 30 ms, valid mapping/calibration and position-prediction limit. A candidate initially valid can expire during the ball query: recheck after the response and immediately before submission. Inputs that fail become explicit errors, not misses.

The fused racket center is the plane wrist position plus the calibrated grip-to-racket offset rotated by IMU orientation. The result is a constrained `plane_2_5d` estimate. A wrist ray/plane intersection does not establish true wrist depth. Neutral-pose heading is reset deliberately, with proposed yaw-drift validation at each run and re-pairing; a numerical acceptable yaw/position error must be established in calibration trials before collision acceptance.

## Ball simulation and collision reference

Use world SI units and fixed 5 ms logical integration steps. Initial model: gravity 9.81 m/s², no aerodynamic spin or drag, swept sphere versus calibrated racket disk/plane, court/net geometry from a versioned configuration. Ball radius 0.033 m and racket-disk radius 0.15 m are proposed demonstrator parameters, not measured equipment. Use semi-implicit Euler for gravity, with swept contact evaluation to avoid endpoint-only tunneling. Ground restitution starts at 0.75; racket normal restitution at 0.8; cap outgoing speed at a configured 20 m/s for the first demo. All parameters belong in the run's gameplay configuration and deterministic test fixtures.

A contact latch prevents the same continuing overlap from generating a new hit every 5 ms. Rearm only after separation greater than the ball radius plus a configured clearance (initial 0.02 m). Swing detection and haptic cue rules are in [controller behavior](controller.md). If tracking becomes invalid within an unresolved swing, terminate it as a tracking failure, never emit a normal missed-swing cue.

A simple initial scene uses four calibrated player lanes whose positions/interaction planes are independent of team assignment. Multiplayer serve/scoring and lane layout are configured demo rules, not real tennis rules inferred from the camera. True spatial 3D collision requires the later depth/stereo profile.

## Ownership and invariants

The Windows game state service stores the single committed snapshot. Physics is the sole writer/calculator and receives a fenced `writer_epoch`. A snapshot is `(game_session_id, state_version)`; `simulation_tick` is separate logical time. Only the game increments committed version. Rendering interpolation cannot change it.

An accepted batch changes version once even if it contains eight controller decisions. Events are identified by `(game_session_id, writer_epoch, batch_id, event_index)`. Candidate states between decisions in a batch are derived states, not separately committed revisions. Old sessions/epochs cannot write after restart or replacement.

## Four-controller batching and arbitration

The offered load is 4 × 200 = 800 transactions/s. Per 5 ms release, admit up to two pending inputs per controller, eight total, from bounded queues of four/controller. Among eligible controller queues, rotate the starting controller slot each release, then order selected entries by recorded Pi arrival sequence with controller/session/request IDs as tie-breakers. Record the final order; never use unsynchronized source timestamps to claim physical arrival order. Reject overflow explicitly and retain all generated keys in accounting.

Each input gets its own `QueryEntry`; one required `ball_state_request` carries all selected entries and one `ball_state_response` echoes them with a shared atomic snapshot. Normal load is four entries; eight allows recovery from a short burst. No samples are silently combined into a different measurement boundary.

From the returned snapshot, integrate required fixed steps once, then evaluate events in the recorded order at the chosen target tick. The second event sees the first candidate result, and so on. Prepare one final ball state and ordered decisions, then submit `state_update` against the exact base version. All accepted decisions share the resulting committed version and retain event indices. A valid miss is recorded even when no haptic cue is eligible.

If an earlier entry becomes invalid before submission, return its explicit failure and rebuild subsequent candidate calculations without its effects. Do not remove it from the list while keeping a ball trajectory it changed. If the game rejects the batch version/session, apply none of it and return state-conflict/errors for every affected input; bounded future requests can query anew.

Stage all ball-dependent contact latches, swing-hit/completion flags and cue decisions alongside the candidate ball state. Install them only after accepted commit; rejection restores the pre-batch gameplay state. Rebuilding a batch starts from that same pre-batch state, not partially mutated latches. Continuous sensor histories and observation filters may advance independently, but each decision uses an immutable estimator snapshot. An uncommitted hit cannot become a confirmed gameplay/estimator fact. Retain staged side-state during commit ambiguity until its outcome is resolved or the session is reset.

## Scheduler and periodic motion

Only one batch is in flight. The state machine is `Idle -> QueryPending -> Compute -> CommitPending -> Complete`; errors enter `Recovering/Paused`. A release while busy counts as a skipped release, rather than creating another writer. When ready, choose the next bounded batch and at most four catch-up integration steps. Periodic-only batches use the same query/commit path with no controller entries, so the ball continues moving while no one swings.

The capacity gate is batch-service p99 at most 4 ms under the declared workload. That leaves nominal scheduling margin within 5 ms, but does not prove a worst-case bound. Track average/percentiles, skipped releases, effective commit rate and simulation lag. If required catch-up or lag exceeds 20 ms, pause and expose degraded state; resume only after state, queues and clock mappings are revalidated. Do not integrate an unbounded jump to hide missed work.

At `run_start` or resume, record an anchor `(Pi monotonic time, committed simulation_tick)`. Desired tick is that anchored tick plus elapsed **active** Pi time divided by 5 ms; simulation lag is the corresponding tick difference times 5 ms. On pause, stop active-time advancement. After recovery, fetch the committed tick and rebase the anchor so time spent paused is not integrated as catch-up. Log every anchor/rebase; do not hide lag accrued before pausing. This metric uses one Pi clock and logical ticks, not a subtraction between Windows and Pi timestamps.

## Conflicts and ambiguous commits

| Situation | Required proposed behavior |
| --- | --- |
| Stale base version | Game rejects the complete update; no partial state or event application |
| Duplicate update | Return the cached outcome for the same game/epoch/batch and identical bytes; changed payload is invalid |
| Lost query reply | Same query retry at 2 ms, expiry at 5 ms; expired replies cannot feed a calculation |
| Lost commit reply | Identical resends at 2/4 ms; after 8 ms pause new writes and use control-plane `commit_status` |
| Unknown outcome after retention | Recover/reset the game session; a snapshot alone does not prove a specific event happened |
| Controller already expired at 50 ms | Preserve later discovered game commit in history; controller suppresses late haptics and retains timeout in measurement accounting |
| Same-process reconnect | Resume its epoch only if the game confirms no replacement writer; invalidate old connection |
| Physics restart | New epoch; old writes fenced; reconcile or reset unresolved prior work before resuming |
| Game restart | New game session and initial state; invalidate snapshots, queries and old writers |

Retain query/commit results for 2 s, capped at 512 batches without evicting still-required records. On pressure, pause/reject rather than silently weaken deduplication. UI reset/serve requests are physics commands or a new game session; UI must not independently advance the authoritative ball.

## Implementation gates

First prove deterministic fusion/integration with replay and validate maximum-size schema messages. Then benchmark Pi-only compute, wired query/commit with Windows state service, and four-controller radio load. Record thermal/throttling state, CPU/IRQ load, memory, per-stage timing, uncertainty and all losses. Upgrade to a faster Pi only if measured Pi compute/scheduling is the bottleneck; it cannot fix camera depth, wireless contention or a GPU-blocked Windows state service.
