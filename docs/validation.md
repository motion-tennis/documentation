# Masterplan validation record

[Documentation home](../README.md) · [Inspection evidence](overview.md#repository-inspection-evidence) · [Runtime acceptance plan](testing.md)

Initial record date: 2026-10-24. Scope: coordinated masterplan changes across six accessible repositories, plus a small offline trace-audit implementation in `debug-units`. Later dated sections record subsequent decisions and checks; earlier status statements describe their revision at that time. This record concerns static documentation and synthetic tool validation, not hardware acceptance.

The documentation checkout started this revision clean at `98e43f5`; four component READMEs already contained uncommitted work from the preceding documentation phase and were preserved/updated. `debug-units` started at `4ec9ed1` with README/license only. No commits, pushes, repository-settings changes, procurement or deployments were performed in this revision. Existing licenses remain unchanged.

## Reviewed changes

| Repository | Result |
| --- | --- |
| documentation | English master plan, reference hardware, explicit budgets and fusion, coordinated UDP/Protobuf design/schema/profile, six-repository debug/integration plan, updated instructions and superseding ADR |
| camera tracking | Windows webcam/RTMO reference, rectification ownership, four-person identity, 2.5D geometry and true 3D migration, exact hardware/runtime feasibility gates |
| controller | Proposed battery ESP32-S3/BMI270 stack, 200 Hz transactions, bounded pending/outputs, semantic cues and local timing |
| physics | Confirmed Pi 3 B target, native delayed-pose fusion, ordered atomic batches with logical queries, staged gameplay state, pause/recovery |
| game engine | Windows native state-service/SDL3 renderer separation, versioned ownership, batch query/commit and independent visual timing |
| debug-units | Runnable offline trace auditor, normalized trace-v1, synthetic four-controller fixture, integrity tests, future collector/viewer/replay/fault plan |

Earlier Kinect/Linux and TCP/JSON assumptions are preserved only in explicitly historical/superseded ADR context. User-confirmed webcam-first 2.5D, wireless battery operation, Pi 3 B and Windows host take precedence. The required game-state query and response remain in architecture and timing diagrams and per-input query records.

Independent review prompted: post-network freshness checks; atomic staging/rollback of contact/swing/cue state; association installation acknowledgement and retirement of old cues; simulation-time anchors rebased after pause; writer-epoch matching on ball responses; and bounded uint64 wire values to keep varint sizes controlled. Exact generated-code maximum-size checks remain a runtime contract gate.

## Checks executed

| Command/check | Result and scope |
| --- | --- |
| `python3 scripts/check_docs.py` in documentation | Passed across six repositories: local/mapped links, anchors, navigation, JSON/fences, Mermaid block structure, reference-profile capacity/deadline checks and schema presence |
| `python3 scripts/check_docs.py --workspace /tmp` | Passed standalone-documentation mode, with explicit missing-sibling skips |
| `python3 scripts/check_trace.py examples/synthetic-trace.jsonl` in debug-units | Passed trace integrity: 5 starts, 3 responses, 1 timeout, 1 local drop; intentionally includes a response over the 30 ms target |
| `python3 -m unittest discover -s tests -v` in debug-units | Nine tests passed for accounting, mixed clocks, duplicate actuation, missing terminal records, expired responses, sequence gaps, duplicate JSON keys, empty input and unmatched old responses |
| `git diff --check` in each repository | Passed tracked whitespace checks |
| `git diff --exit-code -- LICENSE` in each repository | Passed; existing license contents unchanged |
| UTF-8/final-newline/trailing-whitespace and Python AST inspection | Passed, including new untracked files |
| Invalid-profile experiments | Too-small pending table, oversized payload, per-controller batch exceeding queue and nonfinite JSON were rejected |

The synthetic fixture's timing values are fabricated known-answer inputs. Its 32 ms response intentionally fails the 30 ms target while preserving trace integrity. A zero exit from the trace audit means the trace is internally valid, not that a real game met a performance acceptance gate. Read the report's target/failure fields separately.

## Limits and checks not performed

- No Mermaid renderer/parser is installed; diagrams received structural and manual checks only. Full rendering remains an explicit publishing check.
- No `protoc`, `grpc_tools` or generated protobuf codecs are available here. Schema syntax/fields and bounded wire-size reasoning were reviewed, but compilation, inter-language round trips and maximum-size encoding must run with actual implementation dependencies before interoperability claims.
- No Windows laptop, RTX inference, Pi 3, ESP32, battery, webcam, AP, logic analyzer or physical reference was connected/tested by these changes. No hardware/network/timing benchmark is claimed.
- The live debug collector, packet decoder, viewer, simulator/replay/fault harness and production emitters are designed but not implemented. The offline checker does not prove complete batch correctness or discover an entirely absent expected source without a future source registry.
- Primary-source facts were researched and linked in hardware, networking and tracking-stack pages. External URL reachability, private repository access and remote anchors were not comprehensively tested; local links do not imply unpublished files already exist remotely.
- Python checks ran with the available Python 3.14 interpreter; the declared 3.9 minimum was not separately exercised. Existing gameplay test suites do not exist.

## Remaining gates

Resolve exact procurement/power parts, webcam generation/focus/FOV and lighting, model/GPU compatibility and license manifest, calibration/confidence settings, clock uncertainty, actual Pi/Windows batch capacity and radio tails. Then implement/pin components and the complete runtime debug environment in the [delivery order](roadmap.md). These are observable implementation gates, not hidden assumptions in a claimed perfect real-time system.

## Independent IMU marker planning revision: 2026-10-25

The user approved an additional configurable hardware acceleration-threshold IRQ marker while preserving the continuous 200 Hz gameplay stream, requested an IMU comparison, preferred Zephyr support and suggested MPU-6050 because of availability. This revision adds the [marker contract](imu-trigger-markers.md), [ADR 0006](adr/0006-independent-imu-trigger-markers.md) and [IMU selection study](imu-selection.md), and updates component READMEs, timing/protocol guidance, hardware selection, roadmap, acceptance tests and the debug trace plan.

The marker is asynchronous diagnostic evidence linked to existing transactions; it does not modify wire payloads, priorities, sample cadence, batching or expiry. `spec/motion.proto` and `spec/reference-profile.json` are byte-for-byte unchanged against HEAD. BMI270 remains the frozen profile's unvalidated candidate while sensor selection is explicitly reopened in planning. LSM6DSV16X is a conditional full-marker candidate; MPU-6050 is a practical acquisition prototype candidate with shared-IRQ, detector and Zephyr-extension gates. No purchase or firmware migration was performed.

Checks performed for this revision:

- The central documentation checker passed across all six repositories, covering 38 Markdown files, local/mapped links, JSON/profile checks and nine Mermaid blocks structurally.
- `git diff --check` passed in all six repositories; existing licenses, gameplay schema/profile, debug implementation, tests and synthetic fixture were left unchanged.
- The existing nine debug unit tests passed. The existing synthetic trace audit passed integrity with five starts, three responses, one timeout and one local drop; its deliberate response-target exceedance remains present.
- Independent design review checked marker/sample separation, full query/response/commit correlation and honest implementation status. Review clarified shared-IRQ ambiguity and retention of known failed sample links.

Primary manufacturer documents and upstream Zephyr sources were reviewed for sensor capabilities and driver limitations; no installed Zephyr/board combination was compiled or tested. MPU-6050 availability is user-reported, and TDK's current obsolete status is recorded separately. Source URLs/`main` branches can change and must be pinned with implementation. No `mmdc` renderer is available; diagrams received structural/manual checks, not rendered validation. Hardware detection delay, IRQ timestamp accuracy, marker tracing and new event-latency metrics remain unimplemented and unmeasured. Passing the existing auditor/tests does not validate the new marker extension.

## WLAN topology comparison planning revision: 2026-10-25

The user chose to retain Wi-Fi and add an external-access-point versus Pi-hotspot comparison. [ADR 0007](adr/0007-wifi-topology-comparison.md) and the [network experiment plan](networking.md#external-ap-versus-pi-hotspot-comparison) record A as the initial external-AP baseline and B as a Pi-hosted hotspot candidate, with the laptop wired in both. Master plan, roadmap, testing/development guidance, component references and the debug experiment plan now agree on the two variants. Earlier unconditional restrictions against a Pi-hosted AP are scoped to baseline A.

The planned comparison preserves gameplay traffic/protocol, 200 Hz sampling, deadlines and independent markers. It requires verified topology-specific endpoints and Windows collector reachability, matched baseline/load/fault trials, separate sample/marker distributions and Pi resource/recovery evidence. ESP-NOW remains deferred. No live networking, routes, hotspot configuration or service implementation was changed.

The documentation checker passed across 39 Markdown files in six repositories; whitespace checks passed in the changed repositories. Gameplay schema/profile and existing runtime tools/tests are unchanged. The previous synthetic trace tests were not repeated for this documentation-only follow-up. No WLAN performance or hotspot feasibility test has run; the comparison remains planned.

## MPU-6050 with Zephyr prototype decision: 2026-10-25

The user selected **MPU-6050 over I²C with Zephyr for the first prototype**. [ADR 0008](adr/0008-mpu6050-zephyr-prototype.md), the master plan, hardware/wiring reference, controller documentation, roadmap and IMU assessment now distinguish this agreed selection from unimplemented firmware and unverified marker behavior. BMI270/ESP-IDF remain historical recommendations; later alternatives do not reopen the first-prototype choice automatically.

`spec/reference-profile.json` advances to `webcam-pi3-wireless-v2` with the selected IMU, firmware and selection-status metadata. A comparison against HEAD confirmed that only the profile ID and those hardware/firmware fields changed; all other hardware fields, status, protocol version, player count, rates, limits, timing targets, ports and acceptance values are unchanged. `spec/motion.proto` remains byte-for-byte identical. The revised profile needs a new deployment hash; it does not change the gameplay data stream.

Checks performed for this revision:

- The documentation checker passed across 40 Markdown files in all six repositories, including local/mapped links, JSON/profile checks and nine Mermaid blocks structurally.
- Whitespace checks passed in all six repositories; new untracked Markdown files were checked separately for UTF-8, trailing whitespace and final newlines.
- Independent consistency review identified and corrected remaining SPI-path wording and ESP-IDF-specific power-save instructions in current guidance. Historical decisions remain readable as history.

No sensor, firmware, driver extension, board configuration or build/flash setup was implemented or tested. The existing offline debug tests were not repeated for this planning/profile-metadata change. Required gates remain pinned Zephyr/board/HAL versions, explicit DLPF/divider readback and measured 200 Hz cadence, single shared-INT attribution, motion-detector semantics, early timestamps and complete marker trace integration. The numerical timing allocations are still unmeasured; Mermaid diagrams received structural/manual checks only.

## Pi-reference synchronization and debug uncertainty: 2026-10-25

The user approved the Pi monotonic clock as the shared experiment reference, source offset/drift correction and visible timing uncertainty in the debug tool. [ADR 0009](adr/0009-pi-reference-clock-mapping.md), the [clock contract](coordinates-and-time.md#pi-reference-clock-mapping), protocol guidance, master plan, roadmap, acceptance matrix, component READMEs and debug plan now record that design. The planned Pi coordinator owns immutable mappings; runtime decisions and debug reconstruction use explicit versioned evidence while original source timestamps remain unchanged.

The debug specification adds numeric uncertainty intervals, a per-source offset/drift/age/status panel and explicit local-clock presentation when shared-time evidence is unavailable. It preserves valid history across later expiry/restarts, distinguishes source/reference epochs, and supports separate mapping-use references for multiple source times in one processing stage. Shared laptop fits retain separate producer/session bindings. Same-clock RTT and marker intervals remain independent of cross-device mappings. Estimator parameters and measured accuracy are still implementation gates.

The documentation checker passed across 41 Markdown files in all six repositories, including local/mapped links, profile/JSON checks and nine Mermaid blocks structurally. Whitespace checks passed in all six repositories, with new untracked documents separately checked for UTF-8, final newline and trailing whitespace. Independent review checked four-timestamp offset signs, affine drift mapping, conservative error propagation, historical validity and shared/multiple-source bindings.

SHA-256 comparison against the start of this revision confirmed unchanged `spec/motion.proto`, the already-selected v2 reference profile and the offline trace-auditor implementation. No gameplay payload, sampling rate, port, deadline or numeric profile value changed. No runtime clock code, UI, hardware synchronization test or accuracy result was produced. The existing synthetic auditor tests were not repeated for this documentation-only change; they do not validate the new mapping contract. Full Mermaid rendering remains unperformed.

## Doubles gameplay and controller assignment: 2026-10-25

The user selected 2v2 doubles inspired by Wii Tennis interaction, automatic avatar movement without physical running, a controller-lift toss followed by an overhead stroke, normal tennis scoring and net/out rules, explicit team assignment and two elevated rear team views. [Gameplay](gameplay.md), [player assignment](player-assignment.md) and [ADR 0010](adr/0010-doubles-auto-movement-gameplay.md) record the decision. Master plan, physics/fusion, tracking/calibration, display, controller behavior, protocol planning, roadmap, acceptance/debug plans and component READMEs now use body-relative human gestures around Pi-controlled avatar roots.

The existing guided controller/person confirmation and Association installation ACK/resume barrier is retained. Proposed stable encoding is `1=A1`, `2=A2`, `3=B1`, `4=B2`, with exactly one human/controller/avatar per slot. Court ends and front/back roles do not change identity. Best-of-three sets and a horizontal Team-A-above/Team-B-below screen arrangement are proposed defaults rather than newly asserted user choices. Normal matches need four ready players; smaller integration workloads are not labeled full doubles.

Rules were checked against the linked ITF 2026 rules and official tennis-association guides, including deuce/advantage, service/receiver rotation, first/second fault, service let, abandoned toss, line contact and second bounce. Official Nintendo material supports the interaction reference; no game assets or runtime were added. The documents preserve the distinction between technical failures, per-sample misses and sporting point decisions.

The current ball-only schema cannot carry full roster, avatar, serve/rally and score state. The [contract extension](protocol.md#doubles-match-contract-extension) is therefore an explicit prerequisite for implementation, with atomic complete-state updates and encoded-size/resource/recovery checks. SHA-256 comparison confirmed that `motion.proto`, the v2 reference profile and existing offline auditor are unchanged by this planning revision; continuous 200 Hz IMU traffic and existing targets remain intact.

The documentation checker passed across 44 Markdown files in six repositories, including local/mapped links, JSON/profile checks and nine Mermaid blocks structurally. Whitespace checks passed across all six repositories, including separate encoding/newline checks for untracked documents. Independent consistency review covered identity versus court position, body-relative sensing, Pi/PC state ownership, schema gaps and gesture-only normal serves; remaining generic UI-serve wording was restricted to diagnostic/test commands. No runtime, scoring, avatar movement, gesture recognition, split-screen rendering or hardware tests were implemented or run. Existing synthetic auditor tests were not repeated for this documentation-only change.

## Staged contributions across six repositories: 2026-10-25

The user requested repository-specific orientation and a common staged implementation process for multiple people working with AI agents. Each repository now has `AGENTS.md`, `docs/orientation.md` and `docs/workflow.md` reachable from its README. The [shared S0–S7 plan](project-stages.md) defines scope and evidence gates; the [central ledger](project-status.md) is the sole active-stage record; the [contribution workflow](contribution-workflow.md) supplies bounded task briefs, contract-change coordination and review/handoff templates.

The plan separates contract baseline, isolated slices, device/transport feasibility, one-controller integration, playable doubles, matched measurement/hardening and reproducible delivery. True 3D and alternatives remain separately scoped. Local success does not automatically advance the shared stage. Explicit human authorization for a bounded later-stage slice is recorded as an exception, while routine work inside authorized scope needs no repeated permission. Old roadmap labels are mapped to the new sequence, and master/setup/tracking/debug instructions point to the same gates.

The active stage is S0, incomplete: the existing ball-only schema still needs its versioned doubles extension, contract/resource checks and cross-component review. This documentation task neither accepts that gate nor implements the planned runtimes.

Checks performed:

- The documentation checker passed across 64 Markdown files in all six repositories, including local/mapped links, JSON/profile checks and nine Mermaid blocks structurally.
- `git diff --check` passed in all six repositories. Changed/new Markdown was separately checked for UTF-8, trailing whitespace and final newlines. All six repositories have the required three entry documents and all S0–S7 rows in their local workflows.
- Independent reviews checked central/local scope consistency, contract-first ordering, real versus synthetic clock evidence, handoff authority and permanent Pi/PC ownership boundaries. Wording was corrected where deferred work could imply future PC rule calculation or forbid small S0 contract-validation tools.
- The existing debug synthetic audit and nine unit tests passed. Their established coverage does not validate planned clock/marker semantics or runtime stage gates.
- All tracked non-Markdown files were compared with HEAD and remain unchanged, including schema, reference profile, runtime-adjacent tools, tests, fixture and licenses.

No firmware, service, renderer, live collector, hardware trial or performance experiment was added or executed. Stage discipline is documentation and review guidance, not a newly implemented CI enforcement mechanism. No Protobuf compilation, Mermaid rendering or remote link validation was performed by these checks.

## README project-progress dashboard: 2026-10-25

The README now embeds a repository-local SVG stage dashboard plus a text summary and the next unchecked gate item. Both are generated by `scripts/render_progress.py` from the canonical status ledger and shared stage names. The view distinguishes accepted core stages S0–S6 from the active gate checklist and separately scoped S7 extensions. It reports counts rather than an unsupported overall completion percentage.

The generator uses Python's standard library, preserves README content outside its marked block and has a read-only `--check` mode. The existing documentation checker now also rejects stale generated views or inconsistent status sources. The [status maintenance instructions](project-status.md#updating-the-readme-dashboard) document regeneration and the expected ledger vocabulary. No scheduled refresh, remote badge service or new stage acceptance is implied.

Validation covered read-only freshness checks, changed-checklist detection, deterministic regeneration, a simulated S0-to-S1 transition, conflicting active stages, unknown state values, missing README markers, SVG XML parsing and preservation of unrelated README content. Counterexamples ran in temporary copies and did not alter the real stage ledger. The SVG was rendered locally with `rsvg-convert` and visually inspected for layout and legibility. The central documentation checker passed across 64 Markdown files and both generated progress views; whitespace checks also passed. No gameplay schema, reference profile or component runtime changed.
