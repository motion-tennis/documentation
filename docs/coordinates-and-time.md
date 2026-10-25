# Spatial calibration, sensor fusion clocks and uncertainty

[Documentation home](../README.md) · [Tracking](tracking.md) · [Physics](physics.md) · [Timing](timing.md)

**Confirmed scope:** first webcam prototype uses calibrated 2.5D play, later true 3D. **Agreed design:** the Pi monotonic clock is the experiment reference; versioned mappings correct source offset and drift while retaining raw timestamps and visible uncertainty. **Proposed:** spatial conventions, estimator details and candidate accuracy gates below. No calibration, clock fit or accuracy has been measured. All services must agree on calibration/profile identity before gameplay. See [ADR 0009](adr/0009-pi-reference-clock-mapping.md).

## Spatial frames and calibration

World coordinates are right-handed, metres: court-center origin, +X court-right viewed from the near baseline, +Y up, +Z toward the near baseline. Render mirroring is a view transform only; it must not change collision handedness. Quaternion convention is normalized `[x,y,z,w]`, active local-to-target rotation; q and -q are equivalent. For composition, `q_world_from_sensor = q_world_from_controller * q_controller_from_sensor`, applying the rightmost rotation first.

| Frame | Required calibration / data |
| --- | --- |
| Raw webcam image | Width/height, original intrinsic matrix, distortion model and coefficients, raw timestamp kind |
| Rectified webcam image | Capture adapter undistorts once into a fixed image with `K_rect`; inference letterboxes this image; publication reverses letterbox and normalizes to its rectified width/height |
| Camera ray | Pi maps rectified pixels with `K_rect^-1`; **do not undistort again** |
| Physical tracking space | Camera extrinsics, surveyed station origins/axes and calibration points |
| Virtual court/world | Configured court geometry and shared world axes; avatar roots are simulation state rather than surveyed physical player positions |
| Physical player station | One declared plane and valid tracking extent per person; estimate body-relative hand/arm motion and distinguish hand-plane mapping from the floor plane |
| Virtual avatar / local swing | Pi-controlled court root and heading plus calibrated local gesture scale/reach; physical station translation does not command court running |
| IMU sensor / grip | Sensor axes, bias, specific-force convention, mounting transform and neutral heading |
| Racket | Grip-to-racket rotation/offset and collision geometry |
| Render | Explicit world-to-render transform; no independent physics |

The webcam publishes normalized **2D** rectified-image observations. Ray/plane intersection produces a constrained station-space observation, not measured arbitrary wrist depth. In the agreed [automatic-movement doubles mode](gameplay.md), bounded hand/arm motion relative to a body or neutral reference drives a local avatar swing; the Pi supplies the avatar's court translation. A floor homography is appropriate only for points on the floor; applying it to a raised hand creates a false metric position. Single-view pose depth or body-relative coordinates must not be relabeled as calibrated camera/world depth. This limitation follows projective geometry; see [OpenCV calibration reference](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html).

## Proposed calibration procedure

1. Fix the webcam and lock resolution, focus/exposure behavior and all digital framing. Calibrate lens intrinsics/distortion and the rectified matrix using a recorded target/procedure. Recalibrate on camera, resolution or mounting change.
2. Establish camera extrinsics and each physical station's interaction plane and valid extent. Use known reference points on the **interaction plane**, not only the floor, to test reconstruction error. Define the virtual court independently; station locations do not place avatars on that court.
3. Follow the [assignment contract](player-assignment.md) for controller/person/team-slot and playing-hand identity. Record sensor/grip/racket transforms, neutral body/hand anchor, local gesture scale/reach and neutral-pose heading. Calibrate gyroscope bias and record IMU range/filter settings; six-axis measurements do not establish absolute yaw.
4. Validate stationary poses, local plane translations/rotations, upward toss gestures, overhead/forehand/backhand swings and overlapping people. Capture residuals, false associations and out-of-plane motion. The first prototype constrains measured gestures by station/plane while virtual avatars run automatically; a monocular camera cannot reliably certify every out-of-plane hand motion. Keep that limitation visible rather than claiming a detector can always reject it.
5. Record a monotonically versioned calibration ID, transform matrices, coordinate conventions, physical parameters, valid hardware/camera mode, confidence thresholds, observed residuals and date. Changing it invalidates pending work.

Proposed initial accuracy gates are wrist-plane residual p95 at most 0.10 m at surveyed points and stationary orientation drift at most 10 degrees over a 10-minute run. These are coarse 2.5D demonstrator targets, not realistic free-space racket accuracy or observed results. If they cannot be established, keep collisions disabled and use diagnostic visualization. Better accuracy, a larger collision tolerance or a different camera geometry is a reviewed profile change, not a hidden correction.

## Timestamp meanings

| Time | Domain / interpretation |
| --- | --- |
| IMU source sample time | Original sensor clock/ticks, before interrupt/FIFO delays if exposed; retain raw ticks and mapping |
| `t0` | ESP32 monotonic timestamp at declared interrupt/measurement boundary |
| Webcam timestamp | Camera/driver/presentation boundary with actual meaning; not automatically exposure start |
| Capture host receipt | Windows monotonic receipt; never overwrites source timestamp |
| Pose completion | Inference/tracker completion on Windows clock |
| Data arrival / processing completion | Separate local receiver/producer clock domains |
| Simulation tick | Logical integration time; not host time and not state version |
| `tr`, `t1` | Same ESP32 clock/session as `t0`; full valid response receipt and eligible electrical cue |

Preserve capture values unchanged. If converting 100 ns driver units to integer microseconds, preserve the raw value/unit in debug metadata and include quantization in uncertainty. A recent arrival cannot establish a recent exposure. Unknown capture timing yields `timing_valid=false`; no freshness guarantee can be claimed until calibrated.

## Pi-reference clock mapping

The agreed reference is one declared Pi monotonic clock domain and reference session. Each ESP32 and each distinct laptop clock domain is mapped into that timeline with `T_pi = a * t_source + b`. Native monotonic clocks and recorded timestamps are never stepped, replaced or rewritten by synchronization. Events already using the declared Pi reference clock need only the identity conversion within that epoch; their event-placement uncertainty still applies. Wall-clock/UTC time is optional run metadata, not the gameplay reference. The Pi's reference role does not establish its absolute physical-time accuracy.

The Pi owns runtime clock estimation, mapping validity and the clock-dependent readiness gates used by physics. It publishes immutable mapping versions asynchronously; debug collection and the viewer consume those same versions instead of independently fitting a competing runtime timeline. A stopped collector cannot block mapping updates, sampling or feedback. Tracking, game and renderer may share a laptop clock fit and its evidence only after verifying a common monotonic domain and units. Even then, publish separate mapping records/IDs bound to each producer session; sharing coefficients never reuses another producer's identity. Distinct clock domains need separate fits. A camera/driver hardware clock and exposure boundary remain separate and require their own characterized conversion and uncertainty.

### Exchange evidence and drift estimation

The proposed implementation default is Pi-initiated exchanges on the existing bidirectional TCP control connections. Let `A` be Pi send time, `B` peer receipt, `C` peer response send and `D` Pi response receipt. The Pi already has the complete observation after `D`; the existing `ClockExchange` carries the other three times. Preserve all four original timestamps, exchange identity, both endpoint sessions/clocks and boundary metadata. Source-initiated diagnostic exchanges may also be retained, but only when their locally recorded fourth time reaches the evidence record. Three times alone do not establish a complete exchange.

Timestamp sends near the actual framed-message I/O boundary and receipts at the earliest complete-frame boundary, before deferred work where possible. Record application/kernel queueing, timestamp placement and quantization uncertainty; an application send call is not an on-air timestamp. TCP scheduling and retransmission can contaminate observations. Keep rejected observations and their reasons, filter for low-queue exchanges and use a robust multi-observation fit for offset and drift. Estimator window length, sample count, weighting and outlier policy remain implementation choices to record and validate.

For one observation with clock rates treated as equal over the exchange, the conventional estimate is `theta_peer_minus_pi = ((B - A) + (C - D)) / 2` and residual round trip is `delta = (D - A) - (C - B)`. Thus the source-to-Pi conversion is approximately `t_source - theta_peer_minus_pi`, not plus that offset. These formulas are observations under an approximation, not evidence that forward and reverse delays are equal. See [RFC 5905, section 8](https://www.rfc-editor.org/rfc/rfc5905.html#section-8).

The maintained fit uses `a` as well as `b`. In consistent time units, nonnegative transport delays constrain each observation to `A - a*B <= b <= D - a*C`, widened for boundary and rate uncertainty. This illustrates why an offset point estimate alone cannot establish accuracy. Account for asymmetry explicitly and characterize the bounds against common GPIO/optical evidence where possible. Never report one-way delay as half the round trip or assume a low-delay sample proves symmetry.

### Mapping versions, validity and uncertainty

Each immutable version must retain the following metadata in runtime/debug records; these are not new gameplay Protobuf fields. The trace refers to a single-source conversion with `details.clock_mapping_id` and resolves it through the run manifest's `clock_maps` registry. Pi-issued mapping-use evidence identifies the original event/sample/time and selected version; multi-source stages use explicit `details.clock_mapping_refs` entries for each converted time. Raw emitters need not know or wait for a map, and their original records are not rewritten. A missing referenced version or assignment remains unresolved rather than being replaced by the latest available fit. Signed offsets and fractional fit parameters belong in mapping metadata, outside unsigned raw `mono_us` timestamps.

For trace-only times that physics never converted, such as an additional IRQ marker, the Pi also publishes authoritative, nonoverlapping source-time mapping-selection intervals with complete source/reference binding, activation boundaries and map IDs. The viewer may derive a `display_mapping` from such an assignment, within map validity, without sending the debug stream back through physics. Label that conversion separately from actual `runtime_mapping_use` evidence. An actual runtime reference takes precedence; a missing expected runtime reference cannot be repaired by substituting a display mapping. Missing or ambiguous selection intervals leave diagnostic events unmapped. Append assignment history without silently changing earlier selections.

| Metadata | Required meaning |
| --- | --- |
| Mapping identity | Unique mapping ID/version, source ID/session/clock and Pi reference session/clock |
| Fit provenance | Accepted and rejected exchange IDs, fit window, observation count, estimator/configuration version and timestamp boundaries |
| Conversion | Source anchor, corresponding Pi anchor, `a`, offset `b` and declared units; an anchored evaluation `T_anchor + a * (t_source - t_anchor)` avoids unnecessarily large arithmetic operands |
| Drift | Mapping rate correction `(a - 1) * 10^6` ppm, its sign convention and uncertainty; do not confuse it with the inverse source-clock rate error |
| Validity | Valid source-time interval, last accepted refresh, maximum age, and recorded state/reason: initializing, valid, uncertain, expired or invalid |
| Bounds | Uncertainty at the anchor, rate/asymmetry/boundary contributions, growth model and the resulting bound at the evaluated event time |

Age and state are evaluated from the version's recorded evidence and validity rules; later state changes reference that version rather than altering its fitted history. Uncertainty grows away from the fitted interval: a bounded rate uncertainty of `u_rate_ppm` contributes up to `u_rate_ppm * elapsed_seconds` microseconds, in addition to the anchor and other applicable errors. If no justified growth bound is available, uncertainty is unknown rather than a flat optimistic constant.

The existing candidate settings remain a 1 s refresh, expiry after 5 s without a valid update, and network mapping uncertainty at most 2 ms per source. The 2 ms gate applies to a justified error bound, not merely an offset estimate, fit residual or reported precision; an unknown bound cannot pass it. Growing uncertainty may fail the accuracy gate before the age limit. Camera exposure-to-declared-timestamp uncertainty remains at most 8 ms as a separate candidate gate. None of these values is achieved accuracy or a software-timestamp guarantee. Camera timing needs a flashing LED/common-reference experiment; the RTX model name says nothing about acquisition time.

A Pi restart or reference-clock discontinuity opens a new reference epoch and prevents future reuse of every live mapping to the old one. A source reboot/session change or clock discontinuity prevents future reuse of that source's mapping. Implausible drift or a bound violation also invalidates the affected fit. Validity is evaluated for the event's source-time interval and epoch: later expiry or restart does not retroactively erase valid earlier history. Preserve historical versions and epoch identities; never use a fresh fit to silently remap past evidence or join unrelated boots into one continuous timeline.

### Runtime gates and debug interpretation

Display mapped times together with their mapping ID, validity state, age and uncertainty. For a difference between independently mapped sources, conservatively sum both mapping bounds plus the applicable event/capture boundary errors: two 2 ms source bounds can mean 4 ms of mapping uncertainty before those extra errors. Do not silently cancel errors merely because both mappings use the same Pi reference.

Unknown or expired mappings leave events in separate local-clock lanes with their causal transaction/sample/frame/marker IDs intact. Do not claim cross-source durations or precise ordering from that display. Previously recorded events can still use the immutable mapping that was valid for their event interval. Runtime freshness and alignment gates fail closed when required bounds are unavailable or too large; continuous 200 Hz sampling/transmission and explicit failure accounting remain unchanged.

Local differences such as `tr - t0`, `t1 - t0`, controller marker-to-linked-response time and Pi query/commit round trips use one monotonic clock/session and need no mapping. Local timer-scale and event-placement errors still apply. Keep those metrics available even when cross-device freshness is invalid; rejected tracking decisions still produce measurable application errors. The [debug trace contract](https://github.com/motion-tennis/debug-units/blob/main/docs/trace-format.md) retains mapping evidence; its current offline auditor does not validate these fits or their cross-device bounds.

## Temporal fusion policy

The delayed camera observation aligns with **historical** IMU samples near camera capture, not necessarily the newest transaction's sample. Retain 256 IMU samples/controller and eight camera observations/person. Interpolate orientation at capture, apply the body-relative visual hand/arm observation there and replay inertial orientation to the current evaluation time. Record selected historical IDs plus the current input sample ID. Use bounded visual prediction for local gesture motion, never unbounded double integration of acceleration. Automatic avatar court movement is a separate Pi simulation state and does not extend the permitted age of a human gesture.

| Gate | Proposed maximum | Conservative check |
| --- | --- | --- |
| Current IMU age at decision | 30 ms | Estimated age plus applicable uncertainty |
| Camera pose age at decision | 80 ms | Capture age, not arrival age, plus uncertainty |
| Pose-to-historical-IMU alignment | 25 ms | Absolute mapped capture residual plus both clock/capture uncertainties |
| Plane-position prediction horizon | 50 ms | Time since supporting visual observation plus uncertainty |

All gates apply together. Pose age 70 ms may satisfy the 80 ms gate but fail a 50 ms prediction horizon; reject rather than claim fresh position. Unknown bounds fail closed. Recheck after the required ball-state response and before state submission; a network wait can invalidate previously acceptable inputs.

Log age, alignment, prediction and uncertainty separately. Well-aligned old observations can still be stale. Proposed covariance/error models and confidence cutoffs must be validated against recorded motion; model confidence is not calibrated positional uncertainty. A six-axis controller alone cannot correct all yaw drift or restore occluded wrist position indefinitely.

## Later true-3D profile

Add calibrated stereo, depth or multi-view observations through a new explicitly versioned schema/profile. Retain controller/session associations and all timing boundaries. Do not put a guessed z-coordinate into the existing 2D payload. Validate metric depth, multi-person identities, capture synchronization and host/driver requirements before claiming spatial collision. Kinect v2 is one possible evaluated route; its driver alone does not provide skeleton tracking.
