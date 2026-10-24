# Motion Tennis documentation instructions

## Scope and mandatory language policy

These instructions apply to this repository and all its subdirectories. This repository records shared Motion Tennis documentation policy; this file does not automatically apply to sibling repositories, whose applicable instructions must also be read when editing them.

**Motion Tennis may only be edited in English. All new or modified documentation, code, and comments must be written in English.** This is a project-wide content requirement, not an optional style preference.

- Write README content, specifications, diagrams and their labels, examples, scripts, tests, configuration descriptions, UI text, error messages, and log messages in English.
- Use English names for project-defined variables, functions, classes, and other identifiers. Preserve required programming-language syntax, external API identifiers, protocol compatibility, and proper names.
- Write every new or modified comment and docstring in English. In C and C++, use `//` comments rather than block comments.
- Do not add non-English translations or parallel language versions. If a request arrives in another language, keep repository changes in English.
- Preserve existing license text and attribution. Do not rewrite third-party names or legal notices as part of language cleanup.

## Project context

Motion Tennis is a multiplayer tennis demonstrator for up to four players. Its focus is observable distributed processing, communication latency, synchronization, data freshness, and measurable timing behavior. Sophisticated graphics are secondary. Keep the project description neutral and technical; do not add affiliations or assumed team size.

| Repository | Role and agreed hardware |
| --- | --- |
| `documentation` | Central architecture, requirements, interfaces, measurement methods, development guidance and decisions |
| `motion-tennis-controller` | Four wireless battery ESP32 handhelds; S3/BMI270 reference proposed; captures samples and operates LED/haptic feedback |
| `motion-tennis-camera-tracking` | Continuous webcam pose estimation on the Windows RTX 5080 laptop; active 2.5D body/joint input, later true 3D |
| `motion-tennis-physics-engine` | Available Raspberry Pi 3 Model B; temporal fusion, ordered physics batches and sole ball-state calculations |
| `motion-tennis-game-engine` | Windows committed-state service and separate renderer/UI; C++/SDL3 reference proposed |
| `debug-units` | Offline trace checker implemented; runtime collection, viewer, simulator/replay and fault injection planned |

Tracking and visualization may share one physical PC while remaining separate software components and repositories. Handheld controllers are ESP32 devices, not Raspberry Pis. Do not assume specific boards, sensors, motor drivers, pins, runtimes or rendering frameworks without repository evidence.

The current [master plan](docs/master-plan.md) supersedes Kinect-only and Linux-first PC assumptions. The user selected webcam-first 2.5D play, later true 3D, the available Pi 3 B and wireless battery operation. RTMO-m and controller hardware/software details remain proposed until verified. A single RGB camera does not provide unambiguous metric wrist depth. Preserve active pose/IMU fusion and continuous camera acquisition independent of transactions. Kinect/depth/stereo are later alternatives; `libfreenect2` alone is not a skeleton tracker.

## Inspect evidence and label status

Before editing, inspect applicable instructions, Git status, remotes and branches, relevant source/configuration/build files, and existing documentation. Preserve uncommitted work and repository conventions. Derive repository URLs and branch links from actual Git configuration; do not invent owners, default branches or deployment URLs.

At the initial inspection on 2026-10-24, the original five repositories contained only placeholder READMEs and MIT licenses. The six-repository masterplan revision adds shared specifications and real offline trace tools/tests in `debug-units`, not gameplay runtimes. Reinspect current files before implementation claims; update historical status statements when code arrives.

Use these labels consistently:

- **Implemented:** supported by current source or actual artifacts; documentation alone does not establish runtime functionality.
- **Agreed design:** an established project requirement, even if not implemented.
- **Proposed:** a concrete suggestion awaiting agreement and implementation.
- **Open:** a decision or missing information that has not been resolved.

Do not present proposed transports, schemas, consistency mechanisms, numerical limits or examples as implemented defaults. Do not invent commands, dependencies, configuration files, executable names, screenshots, badges, benchmarks or test results. If a component is empty, describe its role, development prerequisites and planned entry points honestly.

## Preserve the required processing transaction

Keep the complete transaction explicit in relevant descriptions and diagrams:

1. An IMU interrupt or defined measurement boundary occurs on an ESP32.
2. The controller records `t0` and assigns a unique transaction identity.
3. The controller sends movement data to the Raspberry Pi.
4. Physics resolves the controller/person association and selects suitable continuously acquired skeleton data.
5. Physics sends `ball_state_request` to the PC game engine.
6. The game returns `ball_state_response` with the snapshot's state version or simulation tick.
7. Physics combines the inputs and calculates hit/miss, outgoing motion and resulting ball state.
8. Physics sends updated state/gameplay events to the game and the corresponding feedback to the controller.
9. The controller matches the response, records `tr`, and actuates the configured outputs at their electrical boundaries, recording `t1`.
10. The game applies the result and displays the scene.

**Never remove or replace the required ball-state request and response during cleanup.** The additional proposed commit acknowledgement does not replace either arrow. Invalid input or unavailable tracking may terminate early with a correlated error; do not fabricate a physics decision.

The current proposed protocol batches up to eight logical queries (at most two per controller) per 5 ms release, with one explicit query key per input and one common versioned snapshot. Each IMU interrupt remains a distinct transaction. Atomic ordered batch commit preserves per-input results; periodic-only batches keep the ball moving. Do not silently decimate samples or turn a shared datagram into an uncorrelated transaction. Use [reference-profile.json](spec/reference-profile.json) and [motion.proto](spec/motion.proto) as canonical proposed values/types; UDP/Protobuf live traffic supersedes the earlier TCP/JSON proposal.

The game stores committed ball state; physics calculates changes. Keep the [proposed consistency model](docs/physics.md) explicit: one serialized physics writer for periodic and controller work, version-checked commits, session/epoch fencing, duplicate handling, and hit/miss feedback after commit acceptance. This mechanism remains proposed until implemented. Avoid two components independently advancing conflicting authoritative states; rendering interpolation is not a physics commit.

Preserve transaction/session/sample/frame/event identities and original timestamps. Explain ordering, stale snapshots, conflicting updates, ambiguous commits, reconnection and periodic movement between controller events. Recheck freshness, association, calibration and expiry after network waiting and before submission. Tracking failures, invalid inputs, overload and communication errors must never silently become ordinary misses. A receipt acknowledgement is not a completed gameplay result.

## Timing and measurement rules

Follow [timing requirements](docs/timing.md) and [coordinate and clock conventions](docs/coordinates-and-time.md):

- `t0` is the specified controller-side IMU interrupt/measurement boundary.
- `tr` is complete framed-message reception on that controller, retained only after validating a matching, timely application result; post-receipt validation has its own boundary.
- `t1` is electrical feedback activation, not merely an output-enqueue call. Record separate LED/motor timestamps when necessary and declare which defines the metric.
- Application response time is `tr - t0`; time to electrical feedback is `t1 - t0`. These same-ESP32 differences do not require cross-device clock synchronization.
- Include queueing, processing, pose waiting, the required ball query/response and any proposed commit wait in the measured transaction. Distinguish sensor latency before `t0`, earlier skeleton acquisition, electrical activation, physical vibration onset and display photons.
- Preserve capture, arrival, processing-completion and simulation times separately. Cross-device comparisons require explicit clock mapping with uncertainty; never infer one-way delay as half the RTT.
- Current provisional targets are 200 Hz measurements per controller, a 5 ms tick, batch service p99 at most 4 ms, application response p99 at most 30 ms, eligible electrical cue p99 at most 40 ms, and local controller expiry at 50 ms. The earlier 25 ms uplink value is historical; the 15 ms decision-to-electrical sub-path target remains provisional. None is a hard guarantee. This Windows/GPU/Wi-Fi profile does not prove hard end-to-end real-time behavior.
- All transactions receive outcome accounting, but haptic cues occur only for semantic hits/completed missed swings. Noneligible samples have no fabricated `t1`. Keep original source timestamps and historical IMU/pose alignment; arrival freshness is not capture freshness.
- Account for every started measurement, including misses, invalid inputs, drops, rejected/late responses, timeouts and pending observations. Report sample counts, median, tail percentiles, observed maximum, deadline misses and failures. Timeouts are censored observations, not fabricated completion latencies.
- Timer resolution is not measurement accuracy. An observed maximum is not a proven worst-case bound. Never claim hardware, networking, tracking or timing validation without actual evidence.

## Documentation organization and editing

Use [README.md](README.md) as the navigation hub. Keep detailed shared specifications in `docs/`; component READMEs explain local responsibilities, prerequisites, actual commands, available tests, limitations and links to the hub. Update affected component references when shared contracts change within the authorized task scope.

- Keep the [architecture](docs/architecture.md), [protocol](docs/protocol.md), [physics model](docs/physics.md), examples and diagrams consistent. Link to canonical definitions rather than introducing competing schemas or timing definitions.
- Use relative links within this repository and verified Git-remote-derived links across repositories. Keep heading anchors and navigation working.
- Label physical devices, software components and repositories distinctly in Mermaid diagrams. Maintain deployment, communication, complete-transaction and timing-boundary diagrams.
- Keep contracts explicit about transport/versioning, units, coordinate frames, quaternion conventions, validation, correlation, state versions, bounded queues/timeouts, stale data and lifecycle errors. Mark unresolved values as open.
- Record significant choices and changes in [ADRs](docs/adr/README.md); keep [open decisions](docs/roadmap.md) current. Do not silently promote a proposal to an agreed or implemented feature.
- Prefer substantive, concise Markdown and small supporting validation tools. Do not introduce a publishing platform or implement whole runtime subsystems to make documentation appear complete.
- Preserve licenses and attribution, and never include credentials, private keys or other secrets.
- Make routine editorial decisions independently; identify genuine blockers while continuing unaffected work. Do not push, publish or modify repository settings without separate authorization.

## Validation and completion

From this repository, run:

```sh
python3 scripts/check_docs.py
git diff --check
```

The checker requires Python 3.9+ and the standard library. It checks available sibling repositories automatically. Missing siblings are skips, not verified remote links. Run `git diff --check` in other repositories changed by the task as well. Check new untracked files for whitespace and final newlines because Git's diff check does not include them.

Manually review English-only content, status claims, commands, links, units, message names, ownership and timing boundaries. The checker validates JSON syntax and basic Mermaid structure; it does not enforce English, validate a runtime schema, fetch every external URL or fully parse/render diagrams. Use a Mermaid renderer when available and record its absence when relevant. Do not claim stronger verification than was performed.

Follow the [test matrix](docs/testing.md) when documenting future runtime acceptance, including one through four controllers, hits/misses/invalid tracking, concurrent inputs, CPU/render load, network faults, stale inputs/state and restarts. Report changed files, checks performed, limitations and remaining decisions accurately. Preserve other work and keep the requested change focused.
