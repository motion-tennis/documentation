# Spatial calibration, sensor fusion clocks and uncertainty

[Documentation home](../README.md) · [Tracking](tracking.md) · [Physics](physics.md) · [Timing](timing.md)

**Confirmed scope:** first webcam prototype uses calibrated 2.5D play, later true 3D. **Proposed:** conventions below. No calibration, clock fit or accuracy has been measured. All services must agree on calibration/profile identity before gameplay.

## Spatial frames and calibration

World coordinates are right-handed, metres: court-center origin, +X court-right viewed from the near baseline, +Y up, +Z toward the near baseline. Render mirroring is a view transform only; it must not change collision handedness. Quaternion convention is normalized `[x,y,z,w]`, active local-to-target rotation; q and -q are equivalent. For composition, `q_world_from_sensor = q_world_from_controller * q_controller_from_sensor`, applying the rightmost rotation first.

| Frame | Required calibration / data |
| --- | --- |
| Raw webcam image | Width/height, original intrinsic matrix, distortion model and coefficients, raw timestamp kind |
| Rectified webcam image | Capture adapter undistorts once into a fixed image with `K_rect`; inference letterboxes this image; publication reverses letterbox and normalizes to its rectified width/height |
| Camera ray | Pi maps rectified pixels with `K_rect^-1`; **do not undistort again** |
| Court/world | Surveyed origin/axes and camera-to-world extrinsics |
| Player interaction plane | One declared plane and valid lane/extent per player; distinguish hand-plane mapping from the floor plane |
| IMU sensor / grip | Sensor axes, bias, specific-force convention, mounting transform and neutral heading |
| Racket | Grip-to-racket rotation/offset and collision geometry |
| Render | Explicit world-to-render transform; no independent physics |

The webcam publishes normalized **2D** rectified-image observations. Ray/plane intersection produces a constrained gameplay position, not measured arbitrary wrist depth. A floor homography is appropriate only for points on the floor; applying it to a raised hand creates a false metric position. Single-view pose depth or body-relative coordinates must not be relabeled as calibrated camera/world depth. This limitation follows projective geometry; see [OpenCV calibration reference](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html).

## Proposed calibration procedure

1. Fix the webcam and lock resolution, focus/exposure behavior and all digital framing. Calibrate lens intrinsics/distortion and the rectified matrix using a recorded target/procedure. Recalibrate on camera, resolution or mounting change.
2. Survey court axes and floor marks. Establish camera extrinsics and each player's interaction plane, valid extent and lane. Use known reference points on the **interaction plane**, not only the floor, to test reconstruction error.
3. Map controller sessions to lanes/person IDs and playing hand explicitly. Record sensor/grip/racket transforms and neutral-pose heading. Calibrate gyroscope bias and record IMU range/filter settings; six-axis measurements do not establish absolute yaw.
4. Validate stationary poses, controlled plane translations and rotations, moving swings and overlapping people. Capture residuals, false associations and out-of-plane motion. The first prototype constrains play by lane/plane; a monocular camera cannot reliably certify every out-of-plane hand motion. Keep that limitation visible rather than claiming a detector can always reject it.
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

## Proposed clock mapping

Use an affine fit `T = a_s * t_s + b_s` from each source monotonic clock into the Pi experiment timeline. Record mapping ID, source session, fit window, offset/drift estimate, validity interval and uncertainty. Four-timestamp exchanges provide observations, not a proof of symmetric paths. Characterize scheduling and asymmetry against a common GPIO/optical reference where possible; never set one-way delay equal to RTT/2.

Refresh the mapping every 1 s and expire it after 5 s without a valid update. A restart, timer discontinuity, implausible drift or bound violation invalidates it immediately. Candidate acceptance limits: network clock mapping uncertainty at most 2 ms per source and camera exposure-to-declared-timestamp uncertainty at most 8 ms. These are required evidence gates, not properties guaranteed by software timestamps. Camera mapping needs a flashing LED/common-reference experiment; the RTX model name says nothing about acquisition time.

The local `tr - t0` and `t1 - t0` need no such cross-device synchronization. Keep those metrics available even when cross-device freshness is invalid; rejected tracking decisions still produce measurable application errors.

## Temporal fusion policy

The delayed camera observation aligns with **historical** IMU samples near camera capture, not necessarily the newest transaction's sample. Retain 256 IMU samples/controller and eight camera observations/person. Interpolate orientation at capture, apply the visual plane-position observation there and replay inertial orientation to the current evaluation time. Record selected historical IDs plus the current input sample ID. Use bounded visual velocity prediction, never unbounded double integration of acceleration.

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
