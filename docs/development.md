# Development setup and integrated startup

[Documentation home](../README.md) · [Master plan](master-plan.md) · [Architecture](architecture.md) · [Testing](testing.md)

## Current state and reference profile

**Implemented:** repository documentation, a documentation checker, shared specification artifacts and the small offline trace checker in `debug-units`. There is no controller firmware, capture/inference pipeline, physics service, game state server, renderer, live collector or integrated startup executable. A complete game cannot yet be built or started.

**Confirmed constraints:** four wireless battery-powered controllers, an available Raspberry Pi 3 Model B, and a Windows laptop with a user-reported RTX 5080. **Proposed reference design:** webcam-first `plane_2_5d` gameplay, ESP32-S3/BMI270 handhelds, native C++ Pi fusion/physics, GPU pose estimation and separate state/UI services on the laptop. The [master plan](master-plan.md), [reference profile](../spec/reference-profile.json) and [protocol](protocol.md) define one compatible implementation target. Proposed component choices and budgets are not hardware inventory or measured capabilities.

## Obtain all six repositories

Git and repository access are required. These SSH URLs come from inspected `origin` remotes; configure authentication locally and never include keys or tokens in documentation. All six inspected local branches and remote HEAD references are `main`.

From a new parent directory:

```sh
git clone git@github.com:motion-tennis/documentation.git
git clone git@github.com:motion-tennis/motion-tennis-camera-tracking.git
git clone git@github.com:motion-tennis/motion-tennis-game-engine.git
git clone git@github.com:motion-tennis/motion-tennis-physics-engine.git
git clone git@github.com:motion-tennis/motion-tennis-controller.git
git clone git@github.com:motion-tennis/debug-units.git
```

For existing checkouts, inspect each repository's `git status --short`, current instructions and branch configuration. Preserve uncommitted work; setup does not require reset or cleanup. The sibling layout is convenient for local cross-repository checking, not a runtime deployment requirement.

## Checks available now

The documentation checker uses Python 3.9+ and the standard library. From `documentation`:

```sh
python3 scripts/check_docs.py
git diff --check
```

With `debug-units` cloned beside this repository, the synthetic offline trace can be checked from the same directory:

```sh
python3 ../debug-units/scripts/check_trace.py ../debug-units/examples/synthetic-trace.jsonl
```

The fixture is synthetic. Passing it verifies the supported offline checks, not camera inference, radio performance or runtime interoperability. See the [debug environment](debugging.md) and [debug repository](https://github.com/motion-tennis/debug-units) for the tool's exact coverage.

The documentation checker finds sibling repositories automatically; an alternate checkout parent can be supplied explicitly:

```sh
python3 scripts/check_docs.py --workspace /path/to/MotionTennis
```

The path above is a placeholder directory argument. Missing checkouts are reported as skipped. Local validation maps known GitHub project links to worktrees; it does not publish pages or establish remote access. Mermaid structure and JSON syntax checks are not full rendering or runtime schema tests. Inspect new untracked files for whitespace separately because `git diff --check` omits them.

## Reference development prerequisites

The following are **proposed implementation choices and verification tasks**, not installed packages or runnable component commands. Pin actual versions and hashes only after a verified setup; add real build and launch entry points with the first implementation.

| Area | Reference stack | First evidence required |
| --- | --- | --- |
| Controller | ESP32-S3-DevKitC-1-N8R8 candidate, BMI270 over SPI, ESP-IDF C/C++, protected battery supply and bounded output driver | Exact board revision, usable pins, safe power/wiring, IMU configuration, 200 Hz interrupt trace, battery-powered radio and measured output transitions |
| Tracking | Windows webcam capture adapter using Media Foundation; Python RTMO-m/rtmlib worker with verified ONNX Runtime GPU | Exact webcam/driver/mode, RTX GPU/provider support, four-person identity/quality, timestamp meaning and calibrated 2.5D geometry |
| Physics | Existing Pi 3 Model B, headless 64-bit Linux, C++20/CMake, bounded buffers and nonblocking I/O | Kernel/runtime manifest, scheduler trace, wired query/commit performance and deterministic batch/fusion fixtures |
| Game | Windows C++20 state service; separate C++/SDL3 renderer | State handling independent of frames/inference, atomic versioned batch commit and traceable display events |
| Network | Dedicated 2.4 GHz AP; Pi and laptop wired to LAN; UDP Protocol Buffers data and TCP control | Recorded endpoints/profile, all encoded datagrams within 1,200 bytes, session binding, retry/expiry and packet capture |
| Debug | Python offline tooling now; collector/viewer/replay/fault injection to implement | Common run manifest, profile/schema hashes, clock-aware traces, complete transaction ledger and log-loss counters |

Read [hardware](hardware.md), [tracking stack](tracking-stack.md) and [networking](networking.md) before selecting installations or wiring. Schema artifacts do not imply generated serializers or compatible handlers already exist. Do not run guessed firmware, Python model, game or service commands merely because a framework appears in the plan.

## Proposed implementation and startup order

This checklist becomes executable only after the named components have working implementations.

1. **Freeze the run profile.** Record the revisions of all six repositories, schema/profile hashes, actual devices, OS/kernel/driver/model versions, camera mode, AP/channel, input rate and instrumentation. Check power, battery, motor limits and camera placement.
2. **Prove the two feasibility gates independently.** On the laptop, verify four-person capture/inference and 2.5D calibration with recorded timestamps. On the Pi, run synthetic 800-transaction/s input against a mock or real independent Windows state service; verify the 5 ms release/4 ms p99 service target and bounded overload before connecting gameplay.
3. **Prepare nonblocking diagnostics.** Start the planned collector, packet captures and run manifest. Verify local trace buffers and dropped-record counters. Losing a debug consumer must not prevent services from responding.
4. **Start the game state service.** Create a fresh game session and initial committed snapshot. Negotiate protocol/profile identity and one physics writer epoch. Start rendering separately so frame work cannot block snapshot/commit replies.
5. **Start continuous webcam tracking.** Keep capture queue length one; count discarded frames. Validate frame/person identities, quality, calibration, GPU provider and capture-time semantics. Tracking does not wait for controller requests.
6. **Start Pi physics/fusion.** Bind control/data/pose endpoints, allocate bounded histories and admission queues, and connect to the state service. Keep gameplay paused until the session, mappings, associations and calibration are usable.
7. **Start and pair one wireless controller.** Establish a fresh controller boot/session and validate the chosen playing hand and lane/person association. Every 200 Hz interrupt retains its own transaction ID, even when the Pi batches requests. Verify error patterns and safe output limits.
8. **Validate clocks and freshness.** As each component starts, establish its clock mapping and uncertainty. Confirm one ESP32 clock for `t0`, `tr` and `t1`. Do not enable gameplay when capture age or mapping uncertainty cannot satisfy the reference limits.
9. **Trace a full batch.** Verify controller input, historical IMU/pose selection, per-transaction query entries, required snapshot response, ordered decisions, one atomic update, commit acceptance, matching feedback and eligible electrical cue. Confirm a receipt ACK alone cannot finish the transaction.
10. **Enable periodic play and scale to four controllers.** Verify movement without controller events, add players deliberately, then run three 10-minute baseline trials at each controller count and the fault matrix. Export buffered evidence outside the measured path.

## Proposed minimal smoke test

Capture a semantic hit, completed missed swing, tracking-loss input, disconnected-service input and a non-cue-eligible measurement. For every transaction, verify a response or counted local terminal outcome. Verify that successful batch events share the accepted version and preserve distinct transaction/event indices. Errors must not create ordinary misses; non-eligible samples must not invent `t1`.

Send duplicate queries/updates/feedback, inject one stale snapshot and lose a commit reply. Confirm bounded retries, atomic all-or-nothing batch commit, no second event application, writer pause on unresolved commit, and suppression of expired output. Repeat with two simultaneous players and a batch containing two inputs from one controller. This runtime smoke test is not yet implemented or executed.

## Proposed shutdown and recovery

Stop admitting gameplay work, drain or explicitly reject bounded pending transactions, turn motors off, save buffered evidence, then stop services. After restart, change the appropriate session, invalidate old work and associations, and re-establish readiness. A surviving physics process may resume its writer epoch only under the protocol's explicit ownership checks.

A lost commit reply remains uncertain until the retained original update result resolves it. Fetching only the current ball snapshot cannot prove whether an event committed. Pause or reset the session if the original outcome is unavailable; never repeat it under a new ID or replay its haptic cue. See [physics](physics.md) and [troubleshooting](troubleshooting.md).

## Contributing

Follow [AGENTS.md](../AGENTS.md): all project edits, code and comments remain in English. Keep shared definitions central and each component's local setup accurate. Preserve **Implemented**, **Agreed design**, **Proposed** and **Open** distinctions, licenses, attribution and uncommitted work. Update examples, profile, schemas and diagrams together when interfaces change. Do not push, publish or change repository settings without authorization.
