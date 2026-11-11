# S1 tracking consumer compatibility

[Project status](project-status.md) · [Shared S1 review](s1-review.md) · [Tracking contract](tracking.md) · [Clock contract](coordinates-and-time.md#pi-reference-clock-mapping) · [Contribution workflow](contribution-workflow.md)

## Task and baseline

The project user authorized a bounded S1 typed tracking input bridge, trace-v1 exporter, validation fixes and reproducible consumer compatibility checks on 2026-11-11. This task uses controlled observations and externally declared clock-map evidence. It does not release S2 or authorize camera acquisition, a Pi clock fitter, live networking, a collector/viewer, complete fusion or a full tennis rule engine.

Work was prepared on `task/s1-tracking-consumer-compatibility`. The starting revisions are:

| Repository | Baseline |
| --- | --- |
| documentation | `683cd45352e38ac66738fdee3bd5dba1614a9ab0` |
| motion-tennis-camera-tracking | `0509fbd8cc15dd7b5a1a640814b66e890aef1ca3` |
| motion-tennis-physics-engine | `51f153593d83bf4872302f7ab286ce458389cd5f` |
| debug-units | `84c3c2a0289011764980de44575bdb14c7d83376` |

The accepted `motion.v03` / `0.3-proposed` / `webcam-pi3-doubles-v3` contract is unchanged. Its canonical LF schema SHA-256 is `b6728e240316e957f5c5addb973f12f9a57fffbcdacc4331f3db5e06895f360b`; profile SHA-256 is `a3533462fdebfd4c7c2f87eaa3bd579d3056170e3dcfc6a6c68ed34474c1d969`.

Component implementations remain in their owning repositories. This central handoff records the compatible source/evidence set and remaining boundaries. On 2026-11-11, the project user explicitly authorized committing, merging and pushing all three changed repositories to remote `main`. The implementation revisions are:

| Repository | Compatible implementation |
| --- | --- |
| motion-tennis-camera-tracking | `5a72519d0441e88fb359b7f98a57b1f1f2581478` — [tracking handoff](https://github.com/motion-tennis/motion-tennis-camera-tracking/blob/5a72519d0441e88fb359b7f98a57b1f1f2581478/docs/s1-consumer-compatibility.md) |
| motion-tennis-physics-engine | `d6d71436f30a1effd1572b85daaf560ebaf40ba1` — [physics handoff](https://github.com/motion-tennis/motion-tennis-physics-engine/blob/d6d71436f30a1effd1572b85daaf560ebaf40ba1/docs/s1-tracking-consumer.md) |
| debug-units | Unchanged `84c3c2a0289011764980de44575bdb14c7d83376` |

The containing documentation commit and remote refs establish delivery. Publication does not accept a shared stage or extend the tested scope.

## Compatibility boundaries

The existing generated Python check establishes an exercised wire boundary: six cases and twenty envelopes, at most 497 encoded bytes including an envelope, against the 1200-byte cap. That result alone does not establish physics ingestion or trace-v1 export.

The typed physics boundary must retain tracker/session/person/frame/calibration identities and native capture metadata. Pi-reference conversion requires an explicit source- and reference-session-bound mapping, its immutable identity and conservative validity/uncertainty evidence. A recent host arrival cannot replace capture time, a missing map cannot become an identity conversion, and supplied coordinates of an `UNAVAILABLE` joint cannot make that joint usable. The same checks remain necessary after waiting for state.

The trace boundary uses the existing [normalized trace-v1 contract](https://github.com/motion-tennis/debug-units/blob/main/docs/trace-format.md). Numeric IDs become decimal strings and 16-byte run/session IDs become lowercase hexadecimal strings. Producer event sequence numbers are allocated before a bounded-ring overflow and survive export; normalization must not hide missing records. Tracking records retain their own source session and clock, with `transaction: null` unless an actual controller transaction link exists. Local event times and lifecycle boundaries must be recorded honestly rather than fabricated for the auditor.

Healthy zero-person frames, an unavailable camera, a missing expected person message, source drops, local replacement and diagnostic loss are distinct evidence. A current frame-status update must invalidate a cached pose that it no longer supports. A new tracker session cannot inherit an old controller/person association merely because a person number repeats.

## Implemented local boundary

The physics repository now contains `TrackingPoseBridge` in `include/motion_tennis/physics/tracking_pose_bridge.hpp` and `src/tracking_pose_bridge.cpp`. It receives a typed, atomic frame/status batch, explicit confirmed bindings, a declared joint-quality policy and caller-installed Pi map evidence. The byte decoder and atomic packet assembly are outside this class; the compatibility harness decodes actual generated adapter envelopes into its bounded field types.

`PoseObservation` retains the original envelope, seventeen-joint frame and capture metadata alongside mapped capture, immutable map identity/version, source/reference epochs and conservative uncertainty. Anchored rational rates avoid dropping microseconds at uint56 epochs. Error growth uses raw source elapsed time, consistent with the offline clock profile; map expiry uses the last good exchange rather than a later issuance timestamp. Full mapped capture intervals must follow map acceptance. Processing/send boundaries that are definitely in the future at Pi receipt are rejected without assigning camera-capture uncertainty to those separate boundaries.

The bridge checks required tracked shoulder/hip and playing-arm joints against an explicit fixture policy, rejects mismatched calibration and invalid timing, and replaces its cached person set from each complete status. It clears unsupported poses on empty/unavailable/incomplete frames and fences tracker/reference restarts. Same-source policy/reference reconfiguration retains frame/message ordering fences. `BatchCore` independently rechecks the selected observation and current source eligibility after state waiting, preserving the required query/response and atomic commit path. This validates observation eligibility; it does not calculate calibrated body-relative racket geometry or historical pose/IMU alignment.

The tracking repository now exports native tracking records through `RecordedPoseAdapter.export_trace()` and its `--format trace-v1` replay option. `tracking_adapter/trace.py` retains per-producer sequences allocated before loss, run-grouped headers, explicit loss notices and source completeness metadata. Old/new session lifecycle timestamps are supplied separately; absent boundaries remain untimed metadata outside the timed event list. Unknown event-placement uncertainty stays unknown rather than borrowing the camera-capture bound. Mixed runs cannot overwrite one another's identity or declared run limits.

The source bounds are four people with seventeen joints each, sixteen retained maps, sixty-four retired source sessions, sixty-four retired reference epochs in a separate registry and sixty-four physics diagnostic records. The tracking exporter retains at most sixty-four timed records, sixty-four untimed metadata records and sixty-four session states. Counter/registry exhaustion has an explicit failure or incompleteness result. A consumer must inspect `tracking_trace.complete_source_diagnostics` and untimed metadata in addition to the generic auditor: a source whose records are all absent cannot be recovered from the surviving sequence numbers alone.

## Reproduction and actual evidence

Run from the tracking checkout with the already provisioned optional codec environment and the sibling physics/debug/documentation checkouts:

```powershell
.\.venv-codec\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv-codec\Scripts\python.exe -B scripts/check_shared_contract.py
.\.venv-codec\Scripts\python.exe -B scripts/check_consumer_compatibility.py --evidence-date 2026-11-11 --report evidence/s1-consumer-compatibility-results.json
```

The C++ build requires the available CMake/MSVC toolchain. The physics component documents its own build and CTest commands. No check installs dependencies, opens a camera or contacts a network service. The ordinary observation adapter remains dependency-free; generated-codec and compiled-consumer checks are development checks with separate prerequisites.

Host validation on 2026-11-11 used Windows, Python 3.14.3 and the available CMake/MSVC environment:

| Check | Actual result and scope |
| --- | --- |
| Tracking Python suite | 64 tests passed, including the real consumer compatibility integration check. |
| Generated Python wire check | Six cases and twenty envelopes passed canonical encode/decode and shared validation; largest exercised envelope 497 bytes, below 1200 bytes including the envelope. |
| Actual typed physics consumer | Seventeen compatibility cases passed across five adapter-produced source frames and fifteen generated/decoded envelope identities. These use the real `TrackingPoseBridge` and `BatchCore`, with explicit synthetic bindings, map evidence, controller inputs and a scripted contact evaluator. |
| Actual debug auditor | Seven compatibility cases passed. Six clean producer records preserve native values, UUIDs, frame membership and quality. A tracking-only run correctly remains insufficient controller measurement evidence. |
| Deliberate diagnostic overflow | One hundred invalid source offers produced seventy-two lost records, including overwritten loss notices. The real auditor reported seventy-two source-sequence gaps and seventy-two log drops and rejected the lossy run as incomplete. That expected rejection is a passing failure-case check, not a valid trace. |

The saved tracking file `evidence/s1-consumer-compatibility-results.json` records the platform/tool environment, exact base revisions with working-tree flags, forty canonical LF source hashes, wire hashes, exercised cases and explicit limits. Base revisions and dirty-tree flags are dated validation-snapshot facts; the source hashes pin the tested content independently of its later commits and publication. The unchanged debug consumer is `84c3c2a`; no `debug-units` implementation change was needed.

Measured host `sizeof` values are 68,968 bytes for `BatchCore`, 18,144 bytes for `TrackingPoseBridge` and 704 bytes for `PoseObservation`. These describe the exercised host layout, not complete process memory, Pi ABI/RAM fit or target-device performance.

The subsequent [shared S1 review](s1-review.md) completes the scoped physics/debug technical receiver reviews and records a [fresh report](../evidence/s1-camera-handoff-results.json) against the clean published implementation revisions. It adds the exact host compiler/architecture context, independent component-suite results and the camera contribution checklist. The original tracking report remains a historical validation snapshot.

## Remaining scope and next handoff

These results close the exercised typed pose handoff and tracking-to-debug trace-format gaps. They do not accept all diagnostic profiles for every producer or establish a full-match runtime. Generic debug acceptance checks trace integrity; the harness separately checks the exercised pose/identity fields rather than claiming the auditor understands all pose semantics.

The physics core still needs retained controller-transaction duplicate handling beyond the pending queue and the remaining shared game/physics fixture and emitted-event evidence. Controller acquisition/safe-output work and the game store's documented score/fixture gaps are unchanged. The complete S1 revision/resource/evidence set and responsible human acceptance remain open; S1 stays active and incomplete, with S2 unreleased.

Next bounded consumer task: close the remaining physics/game fixture and controller-transaction lifecycle gaps against this pinned observation handoff, then collect the shared S1 evidence for review. Actual Pi mapping estimation, raw exchanges, network/packet assembly, hardware exports and placement accuracy, calibrated fusion/alignment/prediction, live collection/viewing and target interoperability retain their existing later gates.

The available Xbox Kinect remains a future adapter input. Its availability changes neither the current seventeen-joint image-space contract nor the accepted schema/profile; no new Kinect or other hardware test was performed here.
