# Windows state service and game visualization

[Documentation home](../README.md) · [Master plan](master-plan.md) · [Protocol](protocol.md) · [Physics](physics.md)

**User-confirmed host:** Windows laptop with RTX 5080. **Proposed stack:** C++20/CMake native state service and a separate simple C++/SDL3 renderer. [SDL3](https://wiki.libsdl.org/SDL3/FrontPage) supports native C++ use and Windows; no game framework or application is installed/implemented by this documentation change. Linux portability can be pursued later; it is not the primary deployment for this profile.

## Separate state service from rendering

Keep the state service in a separate process from GPU inference and rendering. Its nonblocking socket loop responds independently of graphics-frame timing. It owns a single immutable current snapshot and a bounded query/commit deduplication cache. No textures, neural inference, disk logging or UI event loop executes on that state path. This isolation reduces avoidable coupling; Windows scheduling still prevents a hard end-to-end timing guarantee.

Accept the physics writer through control setup with matching profile/schema hashes and a fresh epoch. For each required `ball_state_request`, return one atomic snapshot and exactly echo every transaction/query entry. A duplicate query within retention returns its original snapshot, not an unmarked newer response. A new query gets the current state. Track query send/receive times independently from render timestamps.

For `state_update`, validate sender/epoch/game session, exact base version, target tick, calibration, complete bounded event list and finite ball state. Commit all events and final state atomically or reject all. Increment state version once per batch. Return `state_commit_result` only after that operation. The renderer may never independently advance the authoritative ball.

Cache outcomes for 2 s, up to 512 batches; if retention cannot be honored, apply explicit backpressure/pause. Duplicate identical updates return the cached original result. A changed payload with the same update key is invalid. `commit_status` on the control connection resolves an uncertain update or returns unknown; a current snapshot cannot substitute for that answer. Fence old epochs after writer replacement and new game sessions after service restart.

## Renderer and operator UI

The renderer consumes bounded `state_publication` messages on a local subscription and may interpolate committed snapshots for a 60 Hz presentation target. It uses ordered event IDs `(game_session_id, writer_epoch, batch_id, event_index)` to avoid duplicate effects. It does not extrapolate a visual guess back into game authority. Keep recent events in the state-service history so skipped visual snapshots do not erase measurement provenance.

Display a simple court, four lane/player assignments, 2.5D racket/ball motion, hit/miss effects and explicit faults. Subscribe to tracking separately for smooth avatar display; old/ambiguous joints are marked stale and excluded from collision eligibility. The model's normalized image coordinates are converted using the same calibration profile; no guessed 3D depth is displayed as measured geometry.

The UI must show connection/battery state, person/controller/hand association, pose age and prediction horizon, clock uncertainty, current game version/tick, simulation lag, queue occupancy, transaction/event IDs, response and electrical timing populations, timeouts and tracking failures. UI error indicators may use trace/status subscriptions; missing diagnostic updates are shown as stale rather than fabricated healthy status. Collecting these diagnostics cannot block the state service.

UI pairing, pause, resume, serve and reset use the versioned control plane. Physics performs authoritative motion changes; reset may instead create a fresh game session, invalidating pending work. The pairing UI requires deliberate confirmation and cannot silently attach a controller to whichever person is nearest.

## Presentation and integration evidence

Trace application update receipt, commit completion, render submission and, when available, actual presentation separately. Photodiode/display-patch experiments are needed to measure photons; neither snapshot commit nor a render call proves visible output. A game commit can be displayed after the controller timed out; keep that discrepancy visible instead of rewriting the controller outcome.

Implementation starts with headless synthetic query/commit tests and maximum-size schema fixtures, then adds the minimal renderer. Benchmark four-player batched state traffic while RTMO inference and rendering compete on the laptop. Require batch-service capacity and correct rejection/recovery before optimizing visuals. Real build/run commands and dependency locks must accompany source implementation; none exist yet.
