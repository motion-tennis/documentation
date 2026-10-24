# Game-engine integration and visualization

[Documentation home](../README.md) · [Architecture](architecture.md) · [Physics consistency](physics.md)

**Agreed design:** the game runs on a PC, intended Linux; stores and returns ball state; applies physics results; and displays players, ball motion, and hit/miss effects. **Implemented:** no renderer, language, framework, executable or tests are present. Selecting Unity, Godot, Unreal, a custom renderer, or another framework remains **open**.

## Proposed state service

Keep state handling independent of rendering work so a slow frame does not intentionally block ball-state responses. This does not guarantee isolation from shared CPU/GPU/OS load; measure it.

- Answer every valid `ball_state_request` with one atomic snapshot in `ball_state_response`, preserving the query identity and returning game session, state version, simulation tick and tick duration.
- Accept `state_update` only from the current writer epoch, for the current game session and exact base version. Validate schema, units, finite values, calibration and monotonic tick before committing.
- Store the candidate snapshot and event atomically; then return `state_commit_result`. A transport receipt does not imply the update committed.
- Return the recorded outcome for duplicate update IDs and reject changed duplicate payloads. A same-process reconnect may resume its current writer epoch; a restarted or replacement physics session fences the old writer before accepting writes.
- Publish the committed version to the renderer. Rendering must not independently integrate authoritative physics.

These are proposed interface boundaries, not source modules that already exist. [Protocol](protocol.md) owns the shared field definitions; [physics](physics.md) owns the proposed ordering and recovery model.

## Proposed display behavior

Start with a simple court, player skeleton/racket poses, and ball path. A continuous tracking display subscription is proposed so body motion is visible between transactions. Label invalid/inferred joints and hide or freeze stale avatars with a visible tracking warning. Never show an unqualified active player when its controller/person association is invalid.

Show hit and miss effects only for committed gameplay events and deduplicate by `(game_session_id, event_id)`; event IDs embed their generating physics session to prevent collisions after a writer restart. Show rejected/stale/invalid/timeout outcomes as diagnostic failures, not misses. Controller feedback arrival and scene presentation are separate observations; a committed event may be displayed even when the controller timed out, and the UI should expose that discrepancy.

An initial diagnostics overlay should include:

- Controller connection and session, player association, tracking quality and frame age.
- Latest committed game session, state version, simulation tick and simulation lag.
- Transaction/event ID, hit/miss/error, selected skeleton frame and IMU samples.
- Queue depth, dropped inputs, timeouts, stale frames, conflicts and clock uncertainty.
- Application response distributions reported by controllers, with sample counts and failure counts.

Displaying `tr - t0` from a controller report is valid; calculating that value by subtracting PC time from ESP32 time is not. PC update-received, commit, render-submit, and presentation timestamps have their own clock domain. A displayed latency overlay is not a measurement of photons leaving the display.

## Proposed lifecycle and startup

Create a fresh game session and initial ball snapshot before accepting physics writes. Negotiate a single physics writer, then wait for ready controllers, association/calibration, and usable skeletons before enabling play. Keep diagnostic UI available when gameplay is paused. UI resets/serves go through the physics writer or create a new fenced session; they do not create a second state integrator.

See [development](development.md) for the proposed integrated sequence. There is no runnable game command, asset pipeline, build dependency or screen capture yet. Future tests must exercise snapshot atomicity, CAS rejection, duplicate events, restart fencing, headless state handling where feasible, and CPU/render-load effects on the complete transaction.
