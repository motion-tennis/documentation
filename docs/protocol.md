# Motion protocol 0.2: live data and control contracts

[Documentation home](../README.md) · [Master plan](master-plan.md) · [Schema](../spec/motion.proto) · [Reference profile](../spec/reference-profile.json)

**Proposed reference design, not implemented runtime behavior.** `0.2-proposed` supersedes the earlier proposed TCP/JSON live protocol. The [Protocol Buffers schema](../spec/motion.proto) defines field numbers and types; this page defines required presence, bounds and behavior that proto3 alone does not enforce. All six repositories must agree on the schema/profile SHA-256 before integration.

**Agreed clock design:** [ADR 0009](adr/0009-pi-reference-clock-mapping.md) selects Pi-reference affine clock mappings with drift correction and visible uncertainty. The existing `ClockExchange` supports the planned exchanges; no schema, port or numeric profile setting changes. Runtime estimation, readiness integration and mapping-aware debug validation remain unimplemented.

## Transport and connection setup

Use one serialized `motion.v02.Envelope` per UDP datagram for live data, at most **1,200 bytes including the envelope**. Reject oversized packets before processing. Do not split one atomic commit into independently applied fragments. A skeleton packet contains one person, not all four people; a separate frame-status packet lists visible IDs. An encoder that cannot fit eight decisions in one update must fail the schema acceptance test or lower the configured batch capacity and re-evaluate capacity; it must not truncate fields or silently split commits.

TCP control messages use the same envelope with a four-byte big-endian byte length, maximum 65,536 bytes and a 1 s assembly deadline. Control handles hello, association, clock exchange, readiness, pause/reset, calibration/configuration transfer, and uncertain-commit lookup. Live data does not wait for log collection or a UI frame. The [network page](networking.md) defines topology and retry timing.

| Proposed listener | Device | Port | Data |
| --- | --- | --- | --- |
| Controller input | Pi | UDP 41000 | `controller_input`; reply to the controller's negotiated endpoint |
| Ball-state service | Windows | UDP 41010 | Required `ball_state_request`, `state_update`; responses to physics |
| Pose input | Pi | UDP 41020 | `skeleton_frame`, `frame_status` |
| Trace collector | Windows | UDP 41030 | Separate trace batches, not gameplay messages; collector remains planned |
| Physics control | Pi | TCP 41040 | Controller registration, association, calibration, run commands |
| Game control | Windows | TCP 41041 | Writer setup, commit lookup, reset and renderer subscription |
| Tracking control | Windows | TCP 41042 | Capture/model configuration, calibration, pairing diagnostics |
| Debug control | Windows | TCP 41043 | Run start/stop, manifest, future viewer control |

These are reserved reference ports, not currently running services. Addresses are run-manifest values, not invented deployment hosts. Use the selected WLAN variant's AP with a controller-compatible authenticated mode and isolated test network: external AP baseline A or planned Pi hotspot B. The [topology comparison](networking.md#external-ap-versus-pi-hotspot-comparison) changes deployment addresses/interfaces only; message fields, ports and transaction semantics stay identical. Bind sender role, ID, session and UDP source endpoint during setup; repeat registration after topology changes and reject unknown senders. This is not cryptographic message authentication. Public/untrusted network use requires a separately reviewed authenticated/encrypted profile; keep credentials outside Git.

## Envelope, versioning and scalar validation

Set `major=0`, `minor=2`. Require exact supported profile/schema hashes during `hello`; unknown versions, fields with incompatible semantics, unbound sessions or invalid message roles fail setup. `sender_id` is a provisioned numeric node ID, never a person identity. `sender_session_id` and `run_id` are exactly 16-byte unique IDs. `message_seq` increases within the sender session; identical retries reuse identity and payload. `sent_time_us` belongs to that sender session's `clock_id`.

Counters and timestamps use protobuf `uint64`, with a mandatory wire-value maximum of **2^56 - 1 = 72057594037927935** so every varint fits in eight bytes. Validate this semantic limit in every codec; change the applicable session before reaching it. Full-width uint64 extremes are not legal profile values: eight maximum-width decisions could otherwise exceed the datagram cap. JSON trace exports use decimal strings to avoid floating-point precision loss. Never reuse a session after process restart or wrap counters into an outstanding key. Hashes are 32 bytes. Physical values must be finite. Proto3 default/absent values are not automatically valid: required nested messages, nonzero IDs, correct UUID lengths, enums other than UNSPECIFIED, vector completeness and bounds must be checked by handlers. An unavailable timestamp has `timing_valid=false`, not a fabricated capture at zero.

Limits: four active controllers/player slots; up to eight query/decision entries, at most two per controller; exactly 17 unique COCO joint indices per tracked-person message; reasons at most 128 UTF-8 bytes. Indices 0–16 are nose, left/right eye, left/right ear, left/right shoulder, left/right elbow, left/right wrist, left/right hip, left/right knee, left/right ankle. Missing joints use `UNAVAILABLE`; zero coordinates are not a missing-data sentinel. Keypoint score and normalized image coordinates are in [0,1]; out-of-frame joints are marked unavailable, not clipped into apparently valid positions. Decoder collection lengths and memory must be bounded before allocation.

## Units and coordinate semantics

Use SI: metres, seconds for physics, m/s, m/s², rad/s. Wire time is integer microseconds; haptic duration is integer milliseconds. Controller `specific_force_m_s2` includes gravity as measured in the calibrated sensor frame; physics owns gravity handling. No quaternion is required from the controller. Internal quaternion convention remains normalized `[x,y,z,w]`, active local-to-world rotation; q and -q are equivalent.

World is right-handed, origin court center, +X court-right from near baseline, +Y up, +Z toward near baseline. `Ball` always uses that world frame and the named calibration. Webcam joints are normalized coordinates of the original undistorted image after reversing model resize/letterbox transforms. They are not metric 3D coordinates. Physics applies the versioned `plane_2_5d` calibration. The outgoing velocity vector defines speed and angles; derive elevation `atan2(vy,sqrt(vx²+vz²))` and azimuth `atan2(vx,vz)`. Undefined zero-vector angles remain unavailable.

## Message contracts and correlation

| Message | Required semantics |
| --- | --- |
| `controller_input` | One transaction per regular IMU sampling boundary: `(controller_id, session_id, request_seq)`, `t0_us`, current `sample_id`, capture metadata/raw sensor ticks, association/calibration, specific force, angular rate, saturation, battery voltage. Envelope session must match transaction session. No silent sample decimation. |
| `skeleton_frame` | One person per datagram: common capture `frame_id`, tracker-session-scoped `person_id`, original capture/time kind/uncertainty, processing completion and clock, image dimensions, calibration and 17 joints. Capture may be unknown; bounded-freshness gameplay must then remain unavailable. |
| `frame_status` | Same tracker session/frame ID, observed person IDs, readiness and cumulative skipped-frame count; empty IDs explicitly means no person. Missing status/pose packets also expire through freshness limits. |
| `ball_state_request` | `game_session_id`, writer epoch, batch ID, ordered query entries containing a unique query ID and the full controller transaction key. Every valid selected input has its own logical query. Empty entries mean periodic-only work. |
| `ball_state_response` | Echo exactly writer epoch, batch and query entries; return one atomic snapshot with game session, version, tick, tick duration and ball, or explicit rejection. Match game session/epoch/batch/entries, including periodic-only empty-query batches, so a delayed pre-restart response cannot match a new writer. No cached push replaces this required response. A retry of the same query within its lifetime returns the same retained response. |
| `state_update` | Same game session, writer epoch and batch ID; exact base version, target tick, final ball state, tracking session and ordered decisions. Commit entries may contain only `HIT` or `MISS`; invalid/stale/error inputs receive direct failed feedback and cannot be committed as normal decisions. Each decision retains its transaction, current sample, selected frame/person, association, source capture times, outcome, swing/cue and event index. Full source clocks, historical sample references and uncertainty are preserved in the trace. |
| `state_commit_result` | Echo game/session/epoch/batch; acceptance returns original committed version/tick, rejection reports reason. Acceptance is atomic for the full candidate state and ordered event list. |
| `feedback_result` | Exact originating transaction, outcome and cue; `committed=true` plus game/epoch/batch/event-index/version/tick for hit/miss. Errors have `committed=false`; commit identity fields are unavailable and must not be interpreted as version zero. |
| `state_publication` | Committed snapshot and ordered event list for the local renderer/debug consumers. Must not make the renderer an authoritative writer. Delivery uses a bounded local TCP subscription; delayed frames may be skipped while event IDs remain deduplicated. |

Outcome enum names in the schema are uppercase; human trace names use their lowercase spelling: `hit`, `miss`, `invalid_input`, `tracking_unavailable`, `stale_input`, `state_conflict`, `timeout`, `overloaded`, `internal_error`. A valid no-collision sample is a miss even if it is not eligible for a physical miss cue. A sensor/communication failure is never a miss.

The durable gameplay event key is `(game_session_id, writer_epoch, batch_id, event_index)`. The update key is `(game_session_id, writer_epoch, batch_id)`. A physics restart receives a new epoch; these keys cannot collide just because a sequence resets. `swing_id` and `cue_id` are scoped to the physics writer epoch and controller association. Input/feedback deduplication always uses the controller transaction key, not event proximity in time.

## Diagnostic threshold markers

The [independent threshold marker](imu-trigger-markers.md) adds only diagnostic trace records. `motion.proto`, gameplay payloads, per-sample transaction semantics, rates and expiry stay unchanged. An asynchronous marker-to-transaction link lets the debug tools join the existing query, batch, commit and feedback identities. The marker is not carried in a new gameplay message, is not a new transaction, and cannot alter admission or priority. Packet capture needs the separate trace evidence to identify marked samples.

## Batched query and atomic commit example

This is an illustrative logical transcript, not serialized JSON or a captured run:

```text
batch 81, writer epoch 3
  query 901 -> controller A / boot A7 / request 120
  query 902 -> controller B / boot B4 / request 225
ball_state_response(batch 81, queries [901,902], version 17, tick 240)
  event 0 evaluates A against version 17 -> candidate A
  event 1 evaluates B against candidate A -> candidate B
state_update(batch 81, base 17, target tick 241, final candidate B, events [0,1])
state_commit_result(batch 81, accepted, committed version 18, tick 241)
feedback A/request120 -> committed18/event0
feedback B/request225 -> committed18/event1
```

Intermediate candidates are not separately committed versions. Both decisions record common base 17 and their event order. All admitted query entries must appear in the decisions or be explicitly rejected before submission; no controller ID may disappear from accounting. If validation changes during computation, rebuild the candidate deterministically without invalid entries and return their explicit errors; never keep later calculations based on a removed earlier hit. Unknown partial acceptance is forbidden.

## Matching, bounds, and expiry

The [profile](../spec/reference-profile.json) is authoritative for proposed numeric settings. Controller pending capacity is 16 (80 ms at 200 Hz, greater than the 50 ms expiry); Pi admission is four per controller; batch maximum eight with at most two per controller; one state batch in flight; retained IMU history 256/controller and poses eight/person. These queues serve different purposes and must not be conflated.

Controller inputs are sent once, with no live application retransmission. Missing data becomes a timeout or a gap; UDP checksum success or Wi-Fi MAC acknowledgement is not an application result. The Pi caches terminal results for duplicate requests while retained. The controller never actuates a duplicate or expired feedback result.

Ball query retries once after 2 ms, expires after 5 ms. Commit resends the exact original payload after 2 and 4 ms; after 8 ms without resolution, pause the writer and use control-plane status recovery. Do not start a new state batch while the commit is uncertain. Every stage retains the same local deadlines; retries never extend the controller's 50 ms expiry. Query expiry/ambiguity timers are local durations, not unsynchronized remote deadlines.

Retain query/commit deduplication records for 2 s and up to 512 batches; at 200 batches/s this covers 400 batches plus headroom. If full before time retention expires, reject/pause new state work rather than evict an outcome needed for recovery. A status lookup after expiry returns UNKNOWN_BATCH; it does not prove the update was never committed. Recover/reset the game session before resuming if the outcome cannot be established. A current ball snapshot alone cannot answer whether a particular event committed.

## Control operations and lifecycle

`hello` announces role (`controller`, `physics`, `tracking`, `game`, `debug`, `renderer`), profile/schema hashes and receive endpoint; `hello_result` accepts explicitly. Every new process session repeats readiness and clock setup. A reconnect of the same physics session may resume its epoch only if the game confirms it has not admitted a replacement writer; the old transport is invalidated. New physics sessions fence old epochs.

`Association` binds one controller session to one tracker-session/person, playing hand, slot and calibration; its transaction's sequence is zero because this control record identifies a controller, not a measurement. Increment association version on every change. Physics first suspends the old binding and explicitly rejects old queued work. Send an installation with `command_id`; the controller installs it while suspended and returns the same association/command with `response=true` and `accepted=true`, or an explicit rejection. Only after matching acceptance and valid clocks/calibration does physics send a correlated `resume` command. Until that barrier completes, no normal gameplay input is eligible. Retry installation idempotently by command ID; TCP delivery alone is not installation acceptance. Tracking restart, player ambiguity or re-pairing repeats this barrier. No automatic reassignment to a nearby person is permitted.

During that barrier, the controller retires all pending records and cancels queued cues tied to the old association/calibration, retaining their failure reasons. Every pending entry stores the association/calibration used at transmission; a matching late transaction is still ineligible if that binding has changed. Physics resolves or explicitly invalidates old in-flight batches before resuming the new mapping. Feedback without a live pending entry cannot actuate, even if its controller boot session has not changed.

Allowed `ControlCommand.operation` values are `configure`, `ready`, `pause`, `resume`, `reset_session`, `commit_status`, `subscribe_state`, `run_start`, `run_stop`. Every command has a unique command ID and matching result. Configuration is a versioned UTF-8 JSON object containing profile hash, endpoint map, calibration transform/rules and limit overrides; validate against the published profile and calibration requirements before accepting. `commit_status` identifies game/epoch/batch and returns its cached `state_commit_result`, or UNKNOWN_BATCH. `pause` admits no new gameplay work; `reset_session` invalidates old snapshots and pending batches; neither directly creates competing physics updates.

## Pi-reference clock exchange and mapping ownership

The Pi owns runtime mapping and clock-dependent readiness. It maps each source monotonic domain with `T_pi = a * t_source + b`, retaining both offset and rate correction. Native timestamps remain unchanged. Mapping versions are immutable and scoped to source ID/session/clock plus Pi reference session/clock. Tracking/game/renderer may share a verified host-clock fit and evidence, but each producer session receives its own bound mapping record/ID; distinct clock domains and an independent camera clock need separate conversion evidence. See [clock definitions, estimator requirements and uncertainty](coordinates-and-time.md#pi-reference-clock-mapping).

The proposed implementation default is to initiate exchanges from the Pi over each existing bidirectional control connection. An ESP32 can establish its registration connection to the Pi and still answer a Pi-originated exchange on that same socket; no new listener is needed. The Pi uses existing game/tracking control connections for the relevant laptop domains. Each exchange is correlated with its initiator session and `exchange_id`, and the response must come from the expected registered peer session.

| Boundary | Clock | Existing field or evidence |
| --- | --- | --- |
| `A`: request send | Pi reference | `ClockExchange.source_send_us`; retained locally and echoed in the response |
| `B`: complete request receipt | Peer source | `receiver_receive_us` in the response |
| `C`: response send | Peer source | `receiver_send_us` in the response |
| `D`: complete response receipt | Pi reference | Recorded locally by the Pi; retained with `A`, `B` and `C` in exchange evidence |

The request has `response=false`; its receiver times are not yet available. The matched reply has `response=true` and echoes the request identity/time with the peer's two times. Envelope sender identity/session/clock still describes the actual sender; `source_send_us` describes the exchange initiator even when the peer sends the reply. Capture send timestamps close to the framed-message I/O boundary and receipt timestamps at complete-frame reception, keeping later validation/handling boundaries separate. Timestamp placement, buffering and TCP retransmission affect the observation and must appear in uncertainty and rejection evidence.

Preserve all four raw times and both clock/session identities. Source-initiated diagnostic exchanges are also possible with the same message, but their fourth timestamp is local to that initiator and must be retained/exported before claiming a complete observation. No three-timestamp transcript may be treated as a full exchange. With Pi initiation and equal-rate approximation, the peer-minus-Pi offset is `((B-A) + (C-D))/2`, so conversion to Pi time subtracts that estimate; the maintained model additionally fits drift. [RFC 5905, section 8](https://www.rfc-editor.org/rfc/rfc5905.html#section-8) describes the four-timestamp offset/delay formulation. Neither that estimate nor a low-delay exchange proves symmetric paths, and one-way delay must never be reported as RTT/2.

Filter high-queue/outlier observations and fit offset/drift robustly over recorded observations. Concrete fit windows, counts and weighting remain implementation choices, not additional fixed profile values. Export the Pi's immutable mapping versions and raw exchange evidence asynchronously through the debug path, including anchors, offset/rate and drift ppm, fit window, validity interval, last refresh/age, state/reason and time-dependent uncertainty bounds. The manifest's `clock_maps` registry resolves `details.clock_mapping_id` for a single-source conversion. Pi-issued mapping-use evidence or multi-source `details.clock_mapping_refs` entries bind each original event/sample/time to the version used by the runtime; missing versions or assignments remain unresolved. Raw ESP/laptop emitters never wait for a map or overwrite native timestamps. Signed/fractional fit parameters remain metadata, separate from unsigned raw timestamps. Debug consumes those exact versions; neither the collector nor viewer participates synchronously in clock readiness or gameplay. The [trace contract](https://github.com/motion-tennis/debug-units/blob/main/docs/trace-format.md) defines the evidence destination; its mapping validation remains planned.

The existing candidate settings remain 1 s refresh, 5 s maximum age and at most 2 ms network mapping uncertainty per source. The accuracy gate requires a justified error bound; an offset estimate, fit residual or unknown bound is insufficient. Rate uncertainty grows the bound with age; expiry or excessive uncertainty invalidates readiness even if the control connection is alive. Different-source comparisons conservatively include both mapping bounds plus event/capture error, so two sources at 2 ms each permit 4 ms mapping uncertainty before those additional terms. Same-clock/session elapsed times need no mapping.

The asynchronous mapping export also includes authoritative source-time selection intervals for trace-only events not converted during runtime processing. The viewer can use them for explicitly labeled display conversions; they never replace missing expected runtime-use evidence. Keep selection history, full source/reference bindings and validity boundaries. This allows diagnostic marker/render timestamps to be displayed without adding a synchronous debug-to-physics round trip; see the [clock contract](coordinates-and-time.md#pi-reference-clock-mapping).

A Pi restart/reference discontinuity starts a new reference epoch and prevents future reuse of live mappings to the old reference. Source reboot/session change prevents future reuse of that source's mapping. Evaluate validity at the event's source-time interval and epoch; later expiry/reboot does not invalidate earlier history that used a valid mapping. Retain historical versions without silently refitting old events. Events without a mapping valid for their time retain causal IDs and separate local-clock debug lanes, with no cross-source duration claim. Required gameplay freshness/alignment gates fail closed, while the continuous 200 Hz stream, per-sample identities, local deadlines and explicit outcome accounting remain unchanged.

## Doubles match contract extension

**Agreed gameplay, planned schema work:** [doubles with automatic avatar movement](gameplay.md) expands the state beyond the ball-only messages currently defined in `motion.proto`. The current `Snapshot`, `StateUpdate` and `StatePublication` do not encode a complete roster, avatar state, serve/rally phase or score. They cannot be advertised as a working doubles protocol. Prepare and validate a versioned schema/profile revision before implementing or claiming interoperability for this feature; this planning change does not silently modify the current wire schema.

The extension must specify the following together:

| Contract area | Required design |
| --- | --- |
| Match configuration and roster | Immutable/revisioned match rules, four controller/person/avatar bindings, team membership, handedness, serving/receiving order and physical-station calibration; enforce [assignment uniqueness and activation](player-assignment.md) |
| Player-slot convention | Proposed stable encoding `1=A1`, `2=A2`, `3=B1`, `4=B2`; `Association.player_slot` already exists, but a slot is neither a changing front/back role nor a court end. Document this convention in the new match profile and negotiate its identity |
| Complete snapshot | Ball state, all avatar roots and necessary movement/coverage state, active roster revision, court ends, server/receiver, service side/attempt, toss/rally phase, bounce/point state and point/game/set/match score |
| Query and atomic update | Retain required `ball_state_request`/`ball_state_response` and per-sample logical query identities. The Pi calculates one candidate match state; the PC accepts/rejects ball, avatars, rules and score together against one version |
| Rule events | Stable identities for toss, serve attempt, legal contact, fault, let, point/game/set/match transitions and technical pause; duplicates/retries cannot advance score, attempts or avatars twice |
| Publication and display | Both team viewports consume one committed match snapshot and ordered event stream. Serve/score/side changes and contact discontinuities have explicit events; camera transforms create no second simulation |

Keep ordinary per-sample `feedback_result` outcomes separate from tennis-rule events. A sample `MISS` does not automatically lose a point; a completed swing without contact, second bounce, serve fault and technical tracking failure have different semantics. Periodic-only updates may move avatars/ball or finish a point without inventing a controller transaction. UI reset/team commands enter the control plane; normal serves come from the assigned player's pose/IMU lift-and-stroke sequence. Any operator-triggered serve is restricted to explicitly labeled diagnostic/test operation. The Pi remains the sole calculator and the PC remains the committed-state owner.

The four continuous 200 Hz IMU streams, their measurement identities, additional diagnostic markers and proposed timing targets remain intact. Carry roster/team configuration through the versioned setup contract rather than adding team labels to every IMU sample. Specify complete serializers/validation and test the extended snapshot/update against the 1,200-byte datagram ceiling and maximum batch size; do not truncate decisions, silently fragment an atomic commit or raise the limit without a reviewed profile decision. Include extended-state deduplication, restart recovery, bounded resource/capacity tests and fixture updates in the revision. See [ADR 0010](adr/0010-doubles-auto-movement-gameplay.md).

## Error and lifecycle behavior

Return one correlated terminal result for every parseable admitted measurement, including misses and invalid inputs. For a malformed request without recoverable identity, count the receiver failure; the controller's own pending key expires locally. Log every input not admitted, dropped log record, expired query, late/duplicate/unmatched response and suppressed cue. Retain the original local terminal outcome even when a later commit is discovered; do not fabricate a second completion.

`Cue.electrical_eligible=false` and `CUE_NONE` mean no per-transaction actuation is expected. Continuous status LED state is not an electrical pulse for every sample. Eligible cues are bounded semantic hits or completed missed swings; fault behavior is distinct. Normalize requested intensity to [0,1], cap it by characterized driver limits, and measure actual drive onset separately. See [controller](controller.md) and the [debug trace contract](debugging.md).

This schema is reviewable design source. Generated codecs, nanopb bounds/options, wire-size fixtures, exact configuration JSON schema, authentication extensions and runtime validation remain implementation work. Do not advertise interoperability until codec round-trip and maximum-size tests run across ESP32, Pi and Windows.
