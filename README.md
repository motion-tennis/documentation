# Motion Tennis documentation

Motion Tennis is a multiplayer tennis demonstrator for up to four players. The main objective is to make distributed processing, latency, synchronization, data freshness, and measurable timing behavior visible. Sophisticated graphics are secondary.

**Current status:** all five repositories contain documentation and MIT licenses. At the inspection on 2026-10-24, none contained application source, dependencies, build configuration, workflows, or tests. The architecture below is an agreed design; the protocol and consistency mechanisms are proposals awaiting implementation and review. No hardware or latency results are claimed.

## Start here

1. Read the [overview and terminology](docs/overview.md) and [requirements](docs/requirements.md).
2. Follow the [architecture and complete transaction](docs/architecture.md), including the mandatory physics-to-game ball-state request and response.
3. Use [development setup](docs/development.md) to obtain the repositories and distinguish today's documentation checks from the proposed integrated startup.
4. Before implementing interfaces, review the [protocol](docs/protocol.md), [ball-state consistency](docs/physics.md), and [timing and measurement](docs/timing.md).
5. Choose work from the [milestones and open decisions](docs/roadmap.md); validate against the [integration test matrix](docs/testing.md).

## Repositories and roles

These links derive from the inspected Git remotes. All local checkouts track `origin/main`, whose remote HEAD is `main`.

| Repository | Agreed software role | Target physical device |
| --- | --- | --- |
| [documentation](https://github.com/motion-tennis/documentation) | Shared specifications, decisions, setup, and validation guidance | Development workstation |
| [motion-tennis-controller](https://github.com/motion-tennis/motion-tennis-controller) | IMU measurements, transaction timing, LED and haptic feedback | ESP32 handheld, one per player |
| [motion-tennis-camera-tracking](https://github.com/motion-tennis/motion-tennis-camera-tracking) | Continuous skeleton acquisition and tracking quality | Kinect v2 attached to a suitable host PC |
| [motion-tennis-physics-engine](https://github.com/motion-tennis/motion-tennis-physics-engine) | Sensor combination, hit decisions, ball-state calculations | Raspberry Pi |
| [motion-tennis-game-engine](https://github.com/motion-tennis/motion-tennis-game-engine) | Committed ball-state storage, state queries, UI, visualization | PC, intended Linux environment |

Tracking and visualization may share one PC but remain separate software components and repositories. Linux skeleton tracking is an unresolved dependency; see [tracking integration](docs/tracking.md).

## Documentation map

| Area | Reference |
| --- | --- |
| Scope, evidence, language | [Overview](docs/overview.md), [requirements](docs/requirements.md) |
| Devices and data flow | [Architecture and deployment](docs/architecture.md), [hardware](docs/hardware.md) |
| Component design | [Controller](docs/controller.md), [tracking](docs/tracking.md), [physics](docs/physics.md), [game engine](docs/game-engine.md) |
| Shared contracts | [Protocol](docs/protocol.md), [coordinate systems, calibration, and clocks](docs/coordinates-and-time.md) |
| Measurements | [Timing requirements and methodology](docs/timing.md) |
| Development and validation | [Setup](docs/development.md), [testing](docs/testing.md), [troubleshooting](docs/troubleshooting.md), [documentation validation record](docs/validation.md) |
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
