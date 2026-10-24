# Communication and message contracts

[Documentation home](../README.md) · [Architecture](architecture.md) · [Physics consistency](physics.md) · [Timing](timing.md)

**Implemented:** no transport, wire format, serializers, or protocol tests exist. **Agreed design:** controller input and feedback, continuous skeleton input, explicit physics-to-game ball-state request and response, and physics-to-game state/event output. **Proposed:** the entire contract below, including TCP, field names, version `0.1-proposed`, queue caps and commit acknowledgement. **Open:** approval of this contract, numerical deadlines, deployment endpoints and security profile.

This page is the shared source of truth for message names and semantics. Examples are synthetic contract illustrations, not captured traffic or executable fixtures. Rejecting a proposal is permitted, but all component documentation must change together.

## Transport and connection setup

Propose persistent TCP connections on a controlled laboratory LAN: controllers connect to physics over Wi-Fi; physics connects to the game state service and tracking service; the game may also subscribe to tracking for display. Listeners use operator-configured addresses/ports. No port, address, hostname, configuration file or discovery service is currently assigned.

Frame each message as a four-byte unsigned big-endian payload length followed by that many UTF-8 JSON bytes. Proposed payload range: 1 through 65,536 bytes. Read partial headers/bodies incrementally; do not equate TCP packets or individual reads with application messages. Reject oversize frames before allocating the payload. Apply a bounded assembly deadline to incomplete messages. Disable or enable buffering options only as a measured implementation choice, not a promised latency fix.

TCP preserves byte order on one connection, but retransmissions and head-of-line blocking still affect latency. Reconnects, application retries and independently queued streams still require application deduplication and freshness checks. Network packet loss/reordering tests measure transport effects; application duplicate/out-of-order tests require a deliberate message-level harness.

Use a `hello`/`hello_result` exchange before gameplay: negotiate exact protocol version, role (`controller`, `physics`, `tracking`, `game`), sender and boot/session identity, clock descriptors, supported capabilities, and finite limits. The receiver binds that connection to the role and identity; payload IDs cannot change the sender arbitrarily. The game issues `game_session_id` and a single active `writer_epoch` to an authorized physics session. A replacement writer fences the old epoch before accepting writes.

The initial proposal requires an exact version match; unsupported versions fail setup explicitly. Future additive optional fields need documented compatibility rules; incompatible semantics require a new version. Stable endpoint discovery, credential provisioning, authenticated identity, encryption, heartbeat cadence and reconnect backoff remain open. Do not embed Wi-Fi credentials in examples or treat sender IDs as authentication.

## Envelope and scalar types

Every message has these required envelope fields:

| Field | Type and meaning |
| --- | --- |
| `protocol_version` | String, initially `0.1-proposed` |
| `type` | One of the message types in this page |
| `message_id` | Nonempty string unique within the sending session; retransmission keeps the original identity and payload |
| `sender_id` | Provisioned component/controller identity, bound during setup |
| `session_id` | Fresh sender boot/process-session ID; must not be reused after restart |
| `clock_id` | Session-scoped monotonic clock descriptor for `sent_time_us` |
| `sent_time_us` | Nonnegative integer microseconds encoded as a decimal string |
| `payload` | Object defined for the message type |

IDs are opaque strings. Construct `event_id` from the generating physics session and a session-local unique ID (for example `physics-session-a:event-42`); consumers retain it unchanged. Nonnegative counters (`request_seq`, `frame_id`, `state_version`, `simulation_tick`, `writer_epoch`, `association_version`) and microsecond timestamps use canonical decimal strings, with no signs or leading zeros except `"0"`, in the unsigned 64-bit range. This avoids precision loss in JSON consumers with floating-point numbers. Start a new session before counter wrap; normalize sensor counters explicitly. JSON physical values are finite numbers; NaN and infinity are invalid. Boolean flags are booleans, not strings. Optional unavailable values use explicit `null` where specified, not zero as an unknown sentinel.

Proposed string length limit: 128 UTF-8 bytes for identifiers and 256 for human-readable error reasons. Required fields must be present. Reject duplicate object keys, wrong types, unsupported enum values, nonfinite vectors and out-of-range values. The exact joint set and per-field physical limits remain open and must be negotiated/configured before trials. Ignore no field that changes units, identity, timing or validation behavior.

An illustrative complete request envelope:

```json
{
  "protocol_version": "0.1-proposed",
  "type": "ball_state_request",
  "message_id": "query-42",
  "sender_id": "physics-1",
  "session_id": "physics-session-a",
  "clock_id": "pi-monotonic-a",
  "sent_time_us": "8800000",
  "payload": {
    "query_id": "query-42",
    "game_session_id": "game-session-a",
    "writer_epoch": "3",
    "transaction": {"controller_id": "controller-1", "session_id": "controller-session-a", "request_seq": "42"}
  }
}
```

Envelope sender `session_id` and nested controller `transaction.session_id` identify different components; never substitute one for the other. A receiver appends its own arrival timestamp to its log; it does not rewrite the sender's capture or send time.

## Shared records and correlation

| Record | Required fields / semantics |
| --- | --- |
| `transaction` | `controller_id`, controller `session_id`, `request_seq`; unique key for a measurement from `t0` through its terminal outcome |
| Capture observation | `capture_time_us`, `clock_id`, `capture_boundary`; original source timestamp and its meaning. Timestamp can be `null` when unknown, but unknown age cannot pass a bounded-freshness gate |
| Association | Controller transaction identity bound to `tracking_session_id`, `person_id`, `association_version`, `calibration_id`, `playing_hand`, player slot |
| Ball snapshot | `game_session_id`, `state_version`, `simulation_tick`, `tick_duration_us`, `coordinate_frame`, `calibration_id`, `position_m`, `velocity_m_s`, `radius_m` |
| Selected input provenance | `imu_sample_ids`; `tracking_session_id`, `skeleton_frame_ids`, `person_id`, `association_version`, `calibration_id`; unchanged source capture records; `clock_mapping_ids`; computed ages/alignment and uncertainty in microseconds |
| Feedback profile | `led_pattern`, `intensity` in `[0,1]`, nonnegative integer `duration_ms`; negotiated hardware-safe maximum and pattern vocabulary |

A `person_id` is meaningful only in its tracking session. A state version is meaningful only in its game session. Reassociation or calibration changes invalidate queued work using the previous mapping. Physics owns the association table; an initial manual/operator-controlled pairing exchange is proposed, but its UI/control transport remains open. Gameplay must wait for a confirmed mapping rather than guessing from connection order.

For provenance, record `imu_age_us`, `skeleton_age_us`, `alignment_error_us`, and `uncertainty_us` as nonnegative decimal strings with `clock_mapping_ids`; log signed residuals separately when useful. For more than one pose, retain all source frame IDs/capture records and the interpolation weights. Source clocks and uncertainty must be available, not inferred from fresh arrival alone. See [time mapping](coordinates-and-time.md#proposed-clock-mapping).

## Units and coordinate semantics

Use metres, seconds for physics calculations, metres/second, metres/second squared, radians, and radians/second. Wire timestamps use integer microseconds, motor durations use integer milliseconds, and tick duration uses integer microseconds. Vectors are `[x,y,z]` in the named frame. The proposed world frame is right-handed: court center origin, +X court-right viewed from the near baseline, +Y up, +Z toward the near baseline. See [calibration](coordinates-and-time.md).

Quaternions are normalized `[x,y,z,w]`, active rotations from the named source frame to target frame; `q` and `-q` are equivalent. Controller acceleration remains in the calibrated IMU frame until transformed, with gravity/specific-force semantics explicitly declared. Do not invent a world position by integrating uncalibrated raw acceleration.

The outgoing `velocity_m_s` vector is authoritative in a snapshot. For display, derive speed as its norm, elevation as `atan2(vy, sqrt(vx*vx + vz*vz))`, and azimuth as `atan2(vx, vz)` measured from +Z toward +X. Angles are undefined when their reference magnitude is zero; show unavailable rather than contradictory redundant angle fields. Spin and richer ball parameters require an agreed extension.

## Message catalog

All payloads include the following fields in addition to the envelope. Fields identified as nullable must still be present in that message's payload.

| Type and direction | Payload and validation |
| --- | --- |
| `hello` / `hello_result`, connection initiator ↔ listener | Role, identity, session, versions, clock descriptors, capabilities and limits; result accepts or gives an explicit reason. Exact bootstrap schema is open until implementations select dependencies |
| `controller_input`, controller → physics | `transaction`, `start_time_us` (= `t0` in the controller envelope clock), `association_version`, `calibration_id`, `imu_samples` array; each sample has `sample_id`, capture observation, `sensor_frame`, `acceleration_m_s2`, `angular_velocity_rad_s`, declared acceleration semantics, nullable orientation plus source/target frames. Proposed one sample per request initially; batching needs an explicit admission rule |
| `skeleton_frame`, tracking → physics (and optionally game) | `tracking_session_id` (= sender session), `frame_id`, capture observation, `processing_complete_time_us` and `processing_clock_id`, `coordinate_frame`, `calibration_id`, `people` array. Each person: `person_id`, `tracking_state`, named joints with `position_m` or null, `tracking_state`, nullable backend confidence and its scale |
| `ball_state_request`, physics → game | `query_id`, `game_session_id`, `writer_epoch`, `transaction` (null for periodic work). Must request a current atomic snapshot; an earlier push does not replace this exchange |
| `ball_state_response`, game → physics | Echo `query_id` and `transaction`; `status` (`ok` or `error`), nullable `reason`; snapshot object for `ok`, null for error. Snapshot includes version and tick |
| `state_update`, physics → game | `update_id`, `writer_epoch`, `game_session_id`, `base_state_version`, `target_simulation_tick`, `transaction` (null for periodic), candidate `ball`, `event` (null for periodic), `provenance` (null for periodic). Candidate ball includes position, velocity, radius, world frame and calibration; it does not assign the committed version |
| `state_commit_result`, game → physics | Echo `update_id`, `transaction`, game session and writer epoch; `status` (`accepted`, `conflict`, `invalid`, `wrong_session`, `wrong_writer`); `state_version`, `simulation_tick`, nullable `reason`. For acceptance these identify the original commit; for rejection current state is diagnostic only and requires a fresh query |
| `feedback_result`, physics → controller | `transaction`, `outcome`, nullable `reason`, nullable `event_id`, nullable `game_session_id`, nullable `state_version`, nullable `simulation_tick`, nullable `provenance`, and `feedback`. Hit/miss requires a successfully committed event and complete provenance; failures may lack unavailable snapshot/input fields |

`event` contains `event_id`, `kind` (`hit` or `miss`), and the controller `transaction`. A hit and a miss both produce an event; no error is encoded as a miss. Tracking states are `tracked`, `inferred`, `unavailable`; adapters must document how backend quality maps into these and which states are eligible for collision. An empty `people` list is an explicit no-body frame; failure to receive frames is a separate stream timeout. Missing required joints are unavailable, never zero-position defaults.

## Example query, update, and feedback payloads

These are **payload-only** examples for the corresponding envelopes. Their values are synthetic. A real sender must include the envelope, calibrated input provenance and validated negotiated settings. They illustrate one hit based on version 17 at tick 240; the hit changes version to 18 without advancing the tick. The velocity change is illustrative and does not specify a collision model.

`ball_state_response` payload:

```json
{
  "query_id": "query-42",
  "transaction": {"controller_id": "controller-1", "session_id": "controller-session-a", "request_seq": "42"},
  "status": "ok",
  "reason": null,
  "snapshot": {"game_session_id": "game-session-a", "state_version": "17", "simulation_tick": "240", "tick_duration_us": "5000", "coordinate_frame": "world", "calibration_id": "cal-a", "position_m": [0.1, 1.0, 2.0], "velocity_m_s": [0.0, -1.0, 3.0], "radius_m": 0.033}
}
```

`state_update` payload; the source times belong to different clocks, so the illustrative ages below require the cited mapping records, which are not shown:

```json
{
  "update_id": "update-42",
  "writer_epoch": "3",
  "game_session_id": "game-session-a",
  "base_state_version": "17",
  "target_simulation_tick": "240",
  "transaction": {"controller_id": "controller-1", "session_id": "controller-session-a", "request_seq": "42"},
  "ball": {"coordinate_frame": "world", "calibration_id": "cal-a", "position_m": [0.1, 1.0, 2.0], "velocity_m_s": [1.0, 2.0, -5.0], "radius_m": 0.033},
  "event": {"event_id": "physics-session-a:event-42", "kind": "hit", "transaction": {"controller_id": "controller-1", "session_id": "controller-session-a", "request_seq": "42"}},
  "provenance": {
    "imu_sample_ids": ["1042"], "tracking_session_id": "tracking-session-a", "skeleton_frame_ids": ["300"], "person_id": "body-2", "association_version": "1", "calibration_id": "cal-a",
    "imu_captures": [{"capture_time_us": "1000000", "clock_id": "controller-monotonic-a", "capture_boundary": "sample-ready estimate"}],
    "skeleton_captures": [{"capture_time_us": "7000000", "clock_id": "camera-a", "capture_boundary": "backend frame boundary"}],
    "clock_mapping_ids": ["map-controller-a", "map-camera-a"], "imu_age_us": "12000", "skeleton_age_us": "15000", "alignment_error_us": "3000", "uncertainty_us": "1000"
  }
}
```

`state_commit_result` payload:

```json
{
  "update_id": "update-42", "writer_epoch": "3", "game_session_id": "game-session-a",
  "transaction": {"controller_id": "controller-1", "session_id": "controller-session-a", "request_seq": "42"},
  "status": "accepted", "state_version": "18", "simulation_tick": "240", "reason": null
}
```

An invalid-tracking `feedback_result` from a different transaction needs no fabricated state or event:

```json
{
  "transaction": {"controller_id": "controller-1", "session_id": "controller-session-a", "request_seq": "43"},
  "outcome": "tracking_unavailable", "reason": "Required playing-hand joint is unavailable",
  "event_id": null, "game_session_id": null, "state_version": null, "simulation_tick": null, "provenance": null,
  "feedback": {"led_pattern": "tracking_fault", "intensity": 0.0, "duration_ms": 0}
}
```

Zero motor duration here means no motor activation; a separately configured LED fault pattern is requested. No motor strength, pin, frequency, or LED color is fixed by these examples.

## Matching, bounds, and expiry

Match controller results by the complete `transaction`, queries by `query_id` plus expected session, updates by `update_id` plus game session/writer epoch, and display effects by `(game_session_id, event_id)`. The session-qualified event ID prevents collisions across physics restarts. A matching receipt acknowledgement, if later added, cannot terminate an input transaction. Only a valid `feedback_result` does so; a local deadline can instead terminate it as a recorded failure.

Proposed initial resource caps, to be measured and revised together:

| Resource | Initial proposal | On exhaustion |
| --- | --- | --- |
| Controller pending table | 8 transactions per controller | Assign/record the attempt; reject locally as `overloaded` |
| Physics input queue | 8 entries per controller; at most four active controllers | Return correlated `overloaded`; never silently evict an admitted request |
| Skeleton history | 4 frames per tracked person | Discard oldest, count discard, then apply normal freshness tests |
| Physics state operations | 1 outstanding query or update operation | Serialize; bounded input queues expose backlog |
| Wire payload | 65,536 bytes | Reject/close malformed connection; record framing failure |

All of these are proposed caps, not implementation defaults. Finite timeout, capture-age, alignment, mapping uncertainty, reconnect, deduplication retention, log-buffer, output-queue and maximum-actuation limits remain **open run parameters**. Setup must fail rather than silently use an unspecified bound. Do not derive a full application deadline by adding 25 ms and 15 ms: intermediate acquisition waiting, ball query and scheduling may exceed either provisional sub-budget.

Record a controller-local request deadline and component-local operation deadlines. Remote stages use their own duration budgets; raw controller deadlines cannot be compared with Pi time without a validated mapping. Any accepted budget transfer must account for clock uncertainty. Suspend application work after an expired query, stale pose, invalid mapping, or lost session rather than reusing a cached state as if fresh.

## Error and lifecycle behavior

Terminal outcomes are `hit`, `miss`, `invalid_input`, `tracking_unavailable`, `stale_input`, `state_conflict`, `timeout`, `overloaded`, and `internal_error`. A local connection loss is also recorded as a failure reason, never a miss. Tracking failures, invalid calibration, clock uncertainty and outdated input are distinct diagnostic reasons even when sharing an outcome category.

- For every parsed measurement with valid correlation, send one terminal correlated result, including validation failures and misses. Retain a cached result for bounded duplicate replay. Pending duplicates attach to the existing operation, not a second calculation.
- A malformed envelope without recoverable identity cannot receive a fabricated correlation key. Count it at the receiver; the originating controller's pending record expires, preserving end-to-end accounting.
- Each generated controller transaction must end in a response or a counted local terminal failure. Network failure can prevent response delivery; never claim guaranteed delivery or omit these requests from latency reporting.
- A late response is counted, linked to the expired record, and discarded for actuation. A duplicate result cannot trigger a second pulse. Unmatched responses are counted with reason.
- Missing or delayed frames invalidate hit eligibility according to declared tracking/age limits. Out-of-order skeleton frames may enter retained history only if still useful; never roll back the latest displayed frame silently.
- Reconnect negotiates sessions again. Preserving a process session can permit replay of the same still-live transaction, but only while deduplication retention is known valid. For physics, resume the existing writer epoch only when the game confirms the same process session still owns it and no replacement writer was admitted; resume also invalidates the previous transport connection. A new process or replacement writer receives a new epoch. Boot/process restart always changes session. No retry silently creates a new request identity for the same uncertain event. If epoch resumption fails while a commit is uncertain, pause and recover/reset the session rather than reissue the candidate as new work.
- A game/physics restart or ambiguous commit follows [state recovery](physics.md#conflicts-and-ambiguous-commits). Positive hit/miss feedback waits for commit acceptance. The controller may time out while a commit is still being resolved; outcome accounting must retain both facts.
- Controller/person reassociation and calibration changes invalidate old work explicitly. Tracking identity loss requires revalidation, not automatic reassignment to the nearest body.

The [controller feedback policy](controller.md#proposed-feedback-semantics) defines patterns and safe output scheduling. `intensity` is a requested normalized drive level, not a measured vibration strength. Clamp to negotiated hardware limits and log the applied values. No error should silently reuse a hit/miss pattern.

## Implementation gates

Before coding against this proposal, resolve the bootstrap schema, hardware-safe feedback profiles, exact sample/joint limits and ranges, timing/memory limits, pairing control path, endpoint/security profile, and log schema. Then implement shared schema fixtures and cross-component tests, including malformed/oversize payloads, duplicate keys, counter precision, stale sessions, duplicate commits and complete failure accounting. The current checker validates JSON syntax only; it is not a wire schema validator.
