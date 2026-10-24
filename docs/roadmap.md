# Milestones and open decisions

[Documentation home](../README.md) · [Requirements](requirements.md) · [Decision records](adr/README.md)

**Implemented:** documentation scaffolding and local documentation checks. **Agreed design:** project scope, devices, active skeleton fusion, and required controller transaction. **Proposed:** the milestones below; no dates, team assignments or completed runtime milestones are implied.

## Milestones and evidence

| Milestone | Deliverable | Exit evidence |
| --- | --- | --- |
| M0: shared specification | Readmes, architecture, status labels, proposed contracts, timing definitions | Documentation checks and team review of proposals |
| M1: feasibility and hardware | Selected ESP32/IMU/driver, Pi, Kinect host/backend and safe wiring | Repeatable sensor/actuator checks; skeletons for one to four people; timestamp semantics and dependency licenses recorded |
| M2: interface baseline | Agreed versioned contract and finite limits; simulators/fixtures implemented by component teams | Round-trip correlation, input validation, duplicate/error/timeout tests without requiring a full game |
| M3: consistency and temporal fusion | Query/response, single physics writer, versioned commits, pose association/calibration/clock mapping | Deterministic conflict/restart tests and bounded freshness checks |
| M4: one-player integration | Complete controller transaction plus periodic motion and simple UI | Correlated trace and electrical timing measurements, including misses and invalid tracking |
| M5: four-player evaluation | Full [test matrix](testing.md) and reporting pipeline | Distributions, failure accounting, overhead/uncertainty analysis and reproducible run metadata |
| M6: demonstrator handover | Verified startup, troubleshooting and presentation material | A new contributor reproduces a documented run; claims match evidence |

Suggested work areas are controller hardware/firmware, tracking/fusion, physics/state consistency, visualization/state service, and shared measurement/integration. Assign contributors and reviewers according to these responsibilities.

## Open decision register

All entries remain open until documented evidence or team agreement closes them. Proposed values do not silently become requirements.

| ID | Decision | What resolves it | Initial responsible area |
| --- | --- | --- | --- |
| O-01 | Kinect v2 skeleton backend and compatible host OS | Working metric 3D joints, stable identities, one-to-four person tests, timing semantics, resource and license review | Tracking |
| O-02 | ESP32 variant, IMU, framework, power, motor/driver, LED, pins | Available parts, driver support, electrical schematic and safe bench validation | Controller |
| O-03 | Pi model/OS, PC resources and LAN topology | Hardware inventory and reproducible OS/network configuration | Integration |
| O-04 | Game/physics/tracking implementation languages and frameworks | Supported target environments, state-service needs and build reproducibility | Component teams |
| O-05 | Transport/bootstrap/schema agreement and endpoint discovery/security | Review [protocol](protocol.md), choose schemas, addresses/ports and lab security boundary | All interface owners |
| O-06 | Ball model, court geometry, racket transform, fusion, collision and serve rules | Calibrated fixtures and deterministic physics cases | Physics and tracking |
| O-07 | Pairing UI/control path, playing-hand choice and tracking recovery | Guided association tests including crossings and loss | Tracking and game |
| O-08 | Coordinate calibration residual limits and clock mapping method/uncertainty | Physical reference measurements and mapping residuals | Measurement and tracking |
| O-09 | IMU/pose age, alignment and uncertainty limits; interpolation/prediction horizon | Sensor-rate measurements and gameplay correctness tests | Physics and measurement |
| O-10 | Full transaction deadline and feasibility of provisional timing targets | End-to-end load tests with all included stages | Measurement |
| O-11 | Final queue limits, retries, deduplication retention, operation deadlines, catch-up/lag cap | Overload/restart tests with bounded memory and explicit failures | Physics and integration |
| O-12 | Input admission rate versus 200 Hz processing; physical feedback scheduling | Four-player load and haptic scheduling experiments; complete outcome accounting | Controller and physics |
| O-13 | LED/haptic patterns, maximum drive/duration, perceived onset | Characterized chosen hardware, safety limits and observable error legend | Controller |
| O-14 | Log schema, storage, run duration/sample count and statistical method | Reproducible reporting with overhead and loss counters | Measurement |
| O-15 | Pause policy on tracking loss and commit ambiguity | Explicit gameplay/recovery behavior reviewed against consistency and feedback guarantees | Game and physics |

## How to close a decision

Record the alternatives, evidence and resulting choice in an [ADR](adr/README.md), then update the shared specification and affected component README together. A decision's acceptance establishes design intent; mark runtime behavior implemented only when source and tests exist. Attach the exact commit/configuration and measurement limits to performance claims. Do not label an observed maximum as a proven worst-case bound.

Next executable project work is feasibility and contract approval followed by real subsystem implementation. This documentation task intentionally does not create firmware, pose-estimation, simulation, or rendering code to make setup instructions look complete.
