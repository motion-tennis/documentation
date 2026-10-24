# Motion Tennis documentation

Motion Tennis is a multiplayer tennis demonstrator for up to four players. The main objective is to make distributed processing, latency, synchronization, data freshness, and measurable timing behavior visible. Sophisticated graphics are secondary.

**Current status:** six repositories contain coordinated documentation. `debug-units` also provides an offline trace checker and synthetic integrity tests; the controller, tracking, physics and game runtimes are not implemented. The current reference uses the available Raspberry Pi 3 Model B, a Windows laptop with an RTX 5080, four wireless battery controllers, and webcam-first 2.5D gameplay. Detailed stacks and budgets are proposed, unverified implementation targets.

## Start here

1. Start with the [master plan](docs/master-plan.md), [machine-readable reference profile](spec/reference-profile.json), [overview](docs/overview.md) and [requirements](docs/requirements.md).
2. Follow the [architecture and complete transaction](docs/architecture.md), including the mandatory physics-to-game ball-state request and response.
3. Use [development setup](docs/development.md) to obtain the repositories and distinguish today's documentation checks from the proposed integrated startup.
4. Before implementing interfaces, review the [protocol](docs/protocol.md), [ball-state consistency](docs/physics.md), and [timing and measurement](docs/timing.md).
5. Choose work from the [milestones and open decisions](docs/roadmap.md); validate against the [integration test matrix](docs/testing.md).

## Repositories and roles

These links derive from the inspected Git remotes. All local checkouts track `origin/main`, whose remote HEAD is `main`.

| Repository | Agreed software role | Target physical device |
| --- | --- | --- |
| [documentation](https://github.com/motion-tennis/documentation) | Shared specifications, decisions, setup, and validation guidance | Development workstation |
| [motion-tennis-controller](https://github.com/motion-tennis/motion-tennis-controller) | IMU measurements, transaction timing, LED and haptic feedback | Four wireless battery ESP32 handhelds; S3 reference proposed |
| [motion-tennis-camera-tracking](https://github.com/motion-tennis/motion-tennis-camera-tracking) | Continuous webcam pose estimation and identity tracking | Windows RTX 5080 laptop; RTMO-m reference proposed |
| [motion-tennis-physics-engine](https://github.com/motion-tennis/motion-tennis-physics-engine) | Temporal fusion, hit decisions, sole ball-state calculations | Available Raspberry Pi 3 Model B |
| [motion-tennis-game-engine](https://github.com/motion-tennis/motion-tennis-game-engine) | Committed ball-state service and separate visualization | Windows laptop; native C++/SDL3 reference proposed |
| [debug-units](https://github.com/motion-tennis/debug-units) | Offline trace audit now; live collection, viewer and fault harness planned | Windows analysis host; bounded emitters on all devices |

Tracking, state service, visualization and debug collection share the laptop as separate software components. Webcam-first 2.5D and Windows deployment supersede the earlier Kinect/Linux assumptions. Kinect/depth/stereo remains a later true-3D option, not a prerequisite. See [tracking integration](docs/tracking.md).

## Documentation map

| Area | Reference |
| --- | --- |
| Scope, evidence, language | [Overview](docs/overview.md), [requirements](docs/requirements.md) |
| Devices and data flow | [Master plan](docs/master-plan.md), [architecture](docs/architecture.md), [hardware](docs/hardware.md), [networking](docs/networking.md) |
| Component design | [Controller](docs/controller.md), [tracking](docs/tracking.md), [physics](docs/physics.md), [game engine](docs/game-engine.md) |
| Shared contracts | [Protocol](docs/protocol.md), [Protobuf schema](spec/motion.proto), [reference profile](spec/reference-profile.json), [coordinate systems, calibration, and clocks](docs/coordinates-and-time.md) |
| Measurements | [Timing requirements and methodology](docs/timing.md) |
| Development and validation | [Setup](docs/development.md), [tracking stack](docs/tracking-stack.md), [debug environment](docs/debugging.md), [testing](docs/testing.md), [troubleshooting](docs/troubleshooting.md), [validation record](docs/validation.md) |
| Future work and decisions | [Roadmap and open decisions](docs/roadmap.md), [architecture decision records](docs/adr/README.md) |

## Status vocabulary

- **Implemented:** verified in repository source or existing artifacts. Documentation existence does not establish working runtime behavior.
- **Agreed design:** requirements established by the project brief, not evidence of implementation.
- **Proposed:** a concrete, compatible suggestion awaiting agreement and implementation.
- **Open:** information or a decision still needed. Open numerical limits must be resolved before acceptance trials.

## Check and contribute

Python 3.9 or later is the only dependency for the documentation checker. From this repository:

```sh
python3 scripts/check_docs.py
```

See [development](docs/development.md) for checking sibling repositories and [testing](docs/testing.md) for the checker's limits. No application build or run command exists yet.

Follow [AGENTS.md](AGENTS.md) for project context and repository editing rules. All project edits must be in English, including documentation, code, identifiers, comments, docstrings, examples, and diagram labels. Update shared contracts here and component usage in the corresponding README together. Separate implementation evidence from design status; attach validation evidence to changes. Preserve attribution and avoid committing credentials. New C/C++ comments must use `//`. Submit changes through the team's review process; no branch protection or review policy is assumed.

This repository is licensed under the [MIT License](LICENSE), copyright 2026 Motion Tennis Group. Component repositories retain their own existing MIT notices.
