# Shared S1 review: camera-tracking contribution

[Project status and gate checklist](project-status.md) · [Compatibility handoff](s1-tracking-consumer-compatibility.md) · [Stage requirements](project-stages.md#stage-sequence-and-acceptance-gates)

## Review outcome — 2026-11-11

The camera-tracking contribution is ready for the shared S1 gate review. Its physics input and debug trace handoff reviews are complete for the exercised controlled-input interfaces, with no blocking findings. This packet supplies the camera commits, reproducible checks, failure cases and resource evidence; the other component contributions and human acceptance of the whole stage remain open in the authoritative [status ledger](project-status.md#remaining-s1-work-at-this-review).

The project user requested this review explicitly. Codex performed it with separate technical reviewers for the physics receiver, debug receiver and evidence consistency, followed by the combined consumer rerun. These are agent technical reviews, with no claim of human component-owner sign-off. The review uses documentation base `0df5399738a78ac8dd3724da28586df7288686f1` and task branch `task/s1-camera-handoff-review`; the contribution changes shared documentation and adds evidence only. S1 remains active and incomplete; no later-stage exception or release is recorded.

## Pinned contribution and evidence

| Repository / artifact | Reviewed revision and role |
| --- | --- |
| Initial camera adapter | [`0509fbd8cc15dd7b5a1a640814b66e890aef1ca3`](https://github.com/motion-tennis/motion-tennis-camera-tracking/commit/0509fbd8cc15dd7b5a1a640814b66e890aef1ca3): recorded-input adapter, fixtures and original 47-test evidence. |
| Current camera implementation | [`5a72519d0441e88fb359b7f98a57b1f1f2581478`](https://github.com/motion-tennis/motion-tennis-camera-tracking/commit/5a72519d0441e88fb359b7f98a57b1f1f2581478): trace-v1 exporter, validation fixes and actual consumer compatibility checks; includes the initial adapter. |
| Physics receiver | [`d6d71436f30a1effd1572b85daaf560ebaf40ba1`](https://github.com/motion-tennis/motion-tennis-physics-engine/commit/d6d71436f30a1effd1572b85daaf560ebaf40ba1): bounded typed input bridge and core eligibility checks. |
| Debug receiver | [`84c3c2a0289011764980de44575bdb14c7d83376`](https://github.com/motion-tennis/debug-units/commit/84c3c2a0289011764980de44575bdb14c7d83376): existing offline auditor; no receiver code change required for this scoped review. |
| Shared compatibility documentation | [`0df5399738a78ac8dd3724da28586df7288686f1`](https://github.com/motion-tennis/documentation/commit/0df5399738a78ac8dd3724da28586df7288686f1): published handoff and ledger baseline reviewed here. |

All four current implementation/documentation tips matched freshly fetched `origin/main` on 2026-11-11. The new [consumer result file](../evidence/s1-camera-handoff-results.json) records those exact revisions with clean-worktree flags at validation time, forty canonical LF source hashes, fifteen wire-message hashes, dependency versions, individual cases and host resource outputs. The review documents and result file were added afterward; the recorded clean flags describe that validation snapshot. Current source hashes also match the earlier tracking report; historical base/dirty flags in that original report are preserved.

The accepted `motion.v03` / `0.3-proposed` / `webcam-pi3-doubles-v3` schema/profile bytes are unchanged. Their exact SHA-256 values are in the result file's `wire` section and the [compatibility baseline](s1-tracking-consumer-compatibility.md#task-and-baseline).

## Completed technical receiver reviews

| Review | Disposition and evidence |
| --- | --- |
| Physics receiver — separate Codex reviewer | Accept the exercised typed S1 handoff. Actual adapter envelopes are encoded and decoded with the shared Python codec before their values enter the real C++ bridge. The bridge retains source/session/run/person/frame/calibration identities, all seventeen joint states, raw capture time and immutable source-to-Pi map provenance. Required joints, conservative age/uncertainty, future processing/send boundaries, complete membership and source/reference restart fences are checked. The core rechecks eligibility after state waiting and before commit. The independent Release rebuild passed all 57 checks. See the [pinned receiver handoff](https://github.com/motion-tennis/motion-tennis-physics-engine/blob/d6d71436f30a1effd1572b85daaf560ebaf40ba1/docs/s1-tracking-consumer.md) and [bridge regressions](https://github.com/motion-tennis/motion-tennis-physics-engine/blob/d6d71436f30a1effd1572b85daaf560ebaf40ba1/tests/tracking_bridge_tests.cpp). |
| Debug receiver — separate Codex reviewer | Accept scoped offline trace-v1 use with the completeness policy below. Review confirmed original identities, native boundaries, sequences allocated before buffering, retained rejection evidence, separate old/new restart clocks and truthful lost-record accounting. A focused actual-exporter/auditor probe confirmed the generic auditor's tracking-metadata limitation. All 72 debug tests and four synthetic CLI fixtures passed. See the [pinned exporter](https://github.com/motion-tennis/motion-tennis-camera-tracking/blob/5a72519d0441e88fb359b7f98a57b1f1f2581478/tracking_adapter/trace.py) and [auditor](https://github.com/motion-tennis/debug-units/blob/84c3c2a0289011764980de44575bdb14c7d83376/scripts/check_trace.py). |
| Evidence consistency — separate Codex reviewer | All forty saved LF source hashes match the published source. Reported test counts, exercised wire sizes and host layout measurements agree with source and component handoffs. Fixed capacities are distinguished from measured memory; host values establish no Pi headroom or timing claim. This update also corrects the stale ledger phrase calling the already published bridge uncommitted. |

Debug adoption requires retaining run headers and untimed metadata and inspecting `tracking_trace.complete_source_diagnostics` in addition to generic `valid_trace`. The focused restart probe produced two untimed metadata records and `complete_source_diagnostics=false` while the generic audit still passed when supplied synthetic controller records. That run is incomplete tracking evidence. The generic auditor checks trace integrity rather than pose semantics; the compatibility harness independently compares the exercised pose fields. A tracking-only trace correctly fails the controller measurement requirement. Positive combined fixtures use explicitly synthetic existing controller records, never tracker-invented transactions.

The physics interface is a typed handoff after decoding. A C wire decoder, UDP packet assembly, live clock-map estimation and calibrated contact/fusion remain outside it. Coordinates of an unavailable joint do not make it eligible, repeated person numbers do not restore old associations, and frame/source loss remains separate from diagnostic loss. These are retained interface requirements, not deferred review findings.

## Reproduced checks and failure evidence

| Check run on 2026-11-11 | Result |
| --- | --- |
| Tracking API, fixture and CLI suite | 64 tests passed. |
| Generated Python v0.3 wire check | Six cases, twenty envelopes passed; largest exercised encoding 497 bytes including its envelope, against the 1200-byte cap. |
| Actual typed physics compatibility driver | Seventeen cases passed across five adapter-produced frames and fifteen generated/decoded envelopes. Uses real `TrackingPoseBridge`/`BatchCore` with declared synthetic binding, controller, map and contact/state fixtures. |
| Actual debug consumer compatibility | Seven cases passed: pose/identity preservation, clean combined trace, tracking-only insufficiency, rejection, overflow/loss, restart/retired source and mixed-run/untimed lifecycle handling. |
| Independent physics suite | Two CTest targets passed: 23 core and 34 bridge checks, 57 total. |
| Independent debug suite and CLI | 72 tests passed; synthetic, marker, clock and pipeline fixtures each exited zero with `valid_trace=true`. |

These suites overlap; their counts are not a count of unique system scenarios. The physics negative cases include absent maps, calibration mismatch, uncertainty-inclusive staleness, future boundaries, unavailable required wrists, duplicate frames, empty/incomplete membership, regressing source loss, tracker restart and Pi epoch change. The fresh report lists each case. One hundred deliberately invalid source offers caused seventy-two lost diagnostic records, including displaced loss notices; the actual auditor reported seventy-two sequence gaps and seventy-two log drops and rejected the lossy run as incomplete. That expected rejection passes the failure-case check without making the trace valid.

From `motion-tennis-camera-tracking`, with adjacent checkouts and the optional codec environment provisioned:

```powershell
.\.venv-codec\Scripts\python.exe -B scripts/check_consumer_compatibility.py --evidence-date 2026-11-11 --report ..\documentation\evidence\s1-camera-handoff-results.json
```

This command runs the tracking suite, generated wire checks and both actual consumer compatibility paths. The adapter's ordinary runtime and tests require Python 3.10+ and the standard library. This validation used Python 3.14.3 on Windows 11, CMake 4.3.0-rc2 and C++20. Optional generated-codec dependencies are exactly `grpcio==1.85.0`, `grpcio-tools==1.78.0`, `protobuf==6.33.5`, `setuptools==84.2.1` and `typing_extensions==4.16.0`, pinned in the [reviewed requirements file](https://github.com/motion-tennis/motion-tennis-camera-tracking/blob/5a72519d0441e88fb359b7f98a57b1f1f2581478/requirements-codec.txt).

From `motion-tennis-physics-engine`, reproduce the separately reviewed host build:

```powershell
cmake -S . -B build-merge -G "Visual Studio 18 2026" -A x64
cmake --build build-merge --config Release
ctest --test-dir build-merge -C Release -V
```

The inspected host toolchain is Visual Studio 18 2026, MSVC 19.51.36257.0, toolset directory 14.51.36231, x64, Windows SDK 10.0.26100.0, Release configuration. The automatic compatibility build uses the installed CMake default generator and Release configuration; the result file records Python/platform/CMake, while this packet and the pinned physics handoff retain the additional host ABI context.

From `debug-units`, the separate receiver review ran:

```powershell
$reviewTempRoot = Join-Path (Resolve-Path '..\motion-tennis-physics-engine\build-merge').Path 'debug-review-tmp'
New-Item -ItemType Directory -Force -Path $reviewTempRoot | Out-Null
$env:TEMP = $reviewTempRoot
$env:TMP = $reviewTempRoot
python -B -m unittest discover -s tests -q
python -B scripts/check_trace.py examples/synthetic-trace.jsonl
python -B scripts/check_trace.py examples/marker-trace.jsonl
python -B scripts/check_trace.py examples/clock-trace.jsonl
python -B scripts/check_trace.py examples/pipeline-trace.jsonl
```

The first debug-suite invocation encountered a sandbox permission error creating a default temporary file. The successful 72-test rerun used this controlled child of the existing ignored physics build directory, with `TEMP`/`TMP` changed only in the review PowerShell process. No source repair or test expectation change was needed. All four CLI checks reported zero errors.

## Resource evidence and limits

| Evidence type | Result / enforced capacity | Interpretation |
| --- | --- | --- |
| Measured host C++ layout | `BatchCore`: 68,968 bytes; `TrackingPoseBridge`: 18,144 bytes; `PoseObservation`: 704 bytes. | Actual compatibility-driver `sizeof` outputs on the reviewed MSVC x64 host. No complete process, heap/stack peak, Pi ABI/RAM fit or performance claim. |
| Measured exercised wire sizes | Largest of twenty exercised envelopes: 497 bytes, including the envelope. | Below the 1200-byte profile cap; not a proof of the largest possible encoding of every schema value. |
| Tracking storage bounds | One pending whole frame; at most four people, seventeen joints each; sixty-four timed diagnostics, sixty-four untimed records and sixty-four session states. | Enforced item counts with explicit replacement/loss/session-exhaustion behavior; no Python peak-memory measurement. |
| Physics storage bounds | Four bindings/poses, sixteen maps, sixty-four retired source sessions, sixty-four retired reference epochs in a separate registry and sixty-four diagnostics. | Fixed-capacity source storage; full registries reject and diagnostic overflow is counted. Synthetic test doubles can allocate. |
| Unmeasured target evidence | Live camera/model quality, Kinect capture, Pi memory headroom, clock accuracy, 800 transactions/s capacity and latency percentiles. | Retain their device/transport/integration gates; host fixtures supply none of these measurements. |

Source-backed capacities are documented in the [tracking handoff](https://github.com/motion-tennis/motion-tennis-camera-tracking/blob/5a72519d0441e88fb359b7f98a57b1f1f2581478/docs/s1-consumer-compatibility.md#trace-v1-producer) and [physics resource section](https://github.com/motion-tennis/motion-tennis-physics-engine/blob/d6d71436f30a1effd1572b85daaf560ebaf40ba1/docs/s1-tracking-consumer.md#bounded-resources-and-diagnostics). The available Xbox Kinect remains recorded [future hardware evidence](hardware.md#available-kinect-and-evidence-boundary); this review performed no new hardware test and preserves the webcam-first baseline.

## Camera contribution checklist and remaining gate work

- [x] Pin the initial/current tracking commits, compatible physics/debug revisions and unchanged contract hashes.
- [x] Complete the scoped physics receiver review, including rejection, post-wait eligibility and restart fences.
- [x] Complete the scoped debug receiver review, including lost records and explicit completeness/untimed metadata limits.
- [x] Attach a fresh reproducible consumer report, independent component-suite results, dependency/toolchain versions and resource evidence.
- [x] Include the camera contribution in the shared ledger and review navigation.

No camera-only S1 task remains in this reviewed slice. The shared checklist remains **2/7 delivery/gate items**: controller acquisition/safe outputs, retained physics controller-transaction deduplication, game score-validation repairs, their remaining shared fixtures/emitted-event/profile evidence and the complete all-component review package still need completion. The responsible human must then accept S1 before S2 is released. This camera packet closes neither those tasks nor that stage decision.
