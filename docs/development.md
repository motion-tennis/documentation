# Development setup and startup

[Documentation home](../README.md) · [Architecture](architecture.md) · [Testing](testing.md)

## Current state

**Implemented:** the inspected repositories contained only their README and MIT license before this documentation work. There is no firmware, tracking service, physics service, game executable, dependency manifest, build system, configuration template, or existing CI workflow. The documentation checker described below is available; a complete game cannot yet be built or started.

**Agreed design:** ESP32 handheld controllers communicate over Wi-Fi with a Raspberry Pi running physics. Kinect v2 skeleton tracking and the game engine are separate services, potentially sharing the PC. Linux is the intended PC environment; the skeleton-tracking dependency and its operating-system requirements remain **Open**.

## Obtain the repositories

Git and repository access are the only requirements for obtaining the files. These SSH URLs come from the inspected `origin` remotes. SSH authentication must already be configured; do not place private keys or access tokens in the documentation. The observed local branch and `origin/HEAD` are `main` in all five repositories.

From a new parent directory, run:

```sh
git clone git@github.com:motion-tennis/documentation.git
git clone git@github.com:motion-tennis/motion-tennis-camera-tracking.git
git clone git@github.com:motion-tennis/motion-tennis-game-engine.git
git clone git@github.com:motion-tennis/motion-tennis-physics-engine.git
git clone git@github.com:motion-tennis/motion-tennis-controller.git
```

For existing checkouts, inspect each checkout's `git status --short` and `git branch -avv` before editing. Preserve other people's changes; these instructions do not require resetting or cleaning a working tree. The side-by-side layout is convenient for cross-repository documentation validation, but it is not a runtime deployment requirement.

## Validate the documentation now

The checker uses the Python standard library and requires Python 3.9 or later. From the `documentation` checkout:

```sh
python3 scripts/check_docs.py
git diff --check
```

The script checks Markdown links and heading anchors, maps known project GitHub links to available local checkouts, parses JSON examples, checks fence balance and basic Mermaid structure, and checks that the central transaction and timing documentation are present. By default it looks for sibling component repositories beside `documentation`. To use a different parent directory:

```sh
python3 scripts/check_docs.py --workspace /path/to/MotionTennis
```

The placeholder path above is a directory argument, not a repository file to create. Missing sibling checkouts are reported as skipped; the central documentation still gets checked. The script does not fetch URLs, validate arbitrary remote anchors, prove a Mermaid diagram parses, validate wire contracts against runtime code, or check natural language accuracy. Review the diagrams in a Mermaid-capable Markdown viewer and perform the review described in [Testing](testing.md). Cross-repository GitHub links to new pages will become usable remotely only when the corresponding changes are published through the team's normal review process.

## Development prerequisites to decide

The following are **Proposed preparation steps**, not installed dependencies or working commands:

| Area | Required before implementation can start | Current decision |
| --- | --- | --- |
| Controller | Identify ESP32 board, IMU, electrical interfaces, motor driver, power supply, firmware framework, flashing and serial tools | Open; record selections in [hardware](hardware.md) and an ADR |
| Camera | Verify Kinect v2 adapter, host connectivity, acquisition driver, skeleton SDK/library, licensing and supported OS | Open; prove continuous joint tracking using the chosen route before building integration |
| Physics | Choose Raspberry Pi model, OS, implementation language, runtime, transport library and deployment method | Open; preserve the required ball-state request/response |
| Game | Choose PC requirements, language, renderer and build tooling | Open; retain Linux as the intended environment pending tracking compatibility |
| Network | Provision a Wi-Fi network, addresses/service discovery, endpoint configuration, queue limits and reconnect policy | Open; credentials stay outside Git |
| Measurement | Identify timer behavior, GPIO access, logging storage and available measurement equipment | Open; see [timing](timing.md) |

Each component must add its real dependency manifest, build instructions, configuration reference and executable entry point alongside its first implementation. Do not treat the proposed message examples as a generated SDK or a compatibility guarantee.

## Proposed integrated startup order

This is the intended operational checklist once the component implementations exist. It is not a set of commands that works today.

1. Record the run identifier, revisions of all repositories, device and OS versions, network conditions, protocol version and selected timing/queue limits. Check power, motor-driver safety, and camera placement using [hardware](hardware.md).
2. Prepare the measurement reference and mapping configuration. As each device/service starts, establish its clock mapping and uncertainty, or mark cross-device age measurements unavailable. Do not enable skeleton-dependent gameplay until the required freshness/alignment bounds can be established. Verify that controller-local `t0`, `tr`, and `t1` use one monotonic clock.
3. Start the PC game engine with a new game session and a known initial committed ball state. Check that its ball-state query service returns both a version and a simulation tick. Resetting a session must invalidate older results.
4. Start continuous camera acquisition and skeleton processing. Check frame progression, preserved capture timestamps, confidence states and calibration. Acquisition remains independent of controller transactions.
5. Start physics on the Raspberry Pi. Connect to the game service and the skeleton stream, initialize bounded buffers, and verify that only physics computes ball advances. Keep gameplay paused until state, calibration and tracking dependencies are valid.
6. Start one ESP32 controller, establish its fresh boot/session identifier, and associate it with a tracked person through the agreed pairing process. Confirm that the controller can report communication and tracking failures distinctly from misses.
7. Perform a single valid transaction and inspect its full trace: `controller_input`, selected `skeleton_frame`, `ball_state_request`, `ball_state_response`, calculation, `state_update`, proposed `state_commit_result`, `feedback_result`, electrical actuation and scene processing. A receipt acknowledgement is not transaction completion.
8. Check that the ball continues to advance through the physics scheduler while no controller is active. Check that the game displays committed state without independently producing competing physics updates.
9. Add controllers two through four, verify separate person associations, and run the [integration matrix](testing.md). Enable buffered collection before measuring; export logs outside the measured path.

## Proposed minimal smoke test

For each run, capture one valid hit, one valid miss, one tracking-loss input and one disconnected-service input. Match each admitted input to its terminal outcome or a counted local timeout using the controller ID, session ID and request sequence. For a hit or miss, verify the selected IMU/skeleton identities, base and committed ball versions, controller feedback and visible game event. For failure cases, verify an explicit failure state, no invented miss, no duplicate haptic actuation and no unaccepted state mutation. This smoke test is **not implemented or executed** yet.

## Proposed shutdown and recovery

Stop admitting new controller inputs, drain or explicitly cancel bounded outstanding work, turn the motors off, persist logs, and then stop services. After an unexpected restart, use new session identifiers, reject delayed messages from old sessions, clear invalid associations, fetch committed state and re-establish readiness. A lost commit response is an unknown outcome until the same update's retained deduplication result resolves it; a current ball snapshot alone does not prove whether that event committed. If the original outcome cannot be established, follow the session recovery/reset policy rather than blindly repeat feedback or the ball update. See [physics](physics.md) and [troubleshooting](troubleshooting.md).

## Contributing

Keep shared architecture, contract and measurement definitions here; keep local commands in the appropriate component README. Describe each change as Implemented, Agreed design, Proposed or Open as appropriate. Update examples and diagrams together when an interface changes, run the checker and whitespace check, and record remaining limitations honestly. Preserve the existing MIT licenses and attribution. The repositories currently define no additional contribution workflow or publishing system.
