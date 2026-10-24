# Coordinates, calibration, and clock domains

[Documentation home](../README.md) · [Tracking](tracking.md) · [Timing](timing.md) · [Protocol](protocol.md)

**Implemented:** no transforms, clock mapping, or calibration assets exist in the inspected component repositories. **Agreed design:** decisions combine skeleton and controller observations, preserve original timestamps, and report measurable timing behavior. **Proposed:** the conventions and procedures on this page. **Open:** numerical error limits and the selected synchronization implementation.

## Spatial frames and calibration

Use a common metric, right-handed world frame: origin at court center on the ground, `+X` toward court-right when viewed from the near baseline toward the net, `+Y` upward, and `+Z` from the net toward the near baseline. Thus `X cross Y = Z`. A camera placed differently must be transformed into this frame; display mirroring must not silently reverse physical handedness.

| Frame | Purpose and transform to record |
| --- | --- |
| Kinect sensor frame | Backend-native axes, units, handedness, and capture origin; convert via a calibrated sensor-to-world transform |
| World/court frame | Shared positions for body joints, racket, and ball |
| IMU sensor frame | Manufacturer axes, mounting orientation, accelerometer sign and angular-rate convention |
| Controller frame | Stable physical grip axes independent of the chosen sensor board |
| Racket frame | Virtual racket center, face normal, collision geometry, and offset relative to the controller/hand |
| Render frame | Visualization framework's axes and scale; apply an explicit world-to-render conversion |

Positions and lengths use metres, time intervals in physical formulas use seconds, angular rates use radians per second, and linear velocity/acceleration use metres per second/metres per second squared. Timestamp representation follows the [protocol](protocol.md); do not confuse a timestamp's integer unit with a physics integration unit.

Quaternions use `[x, y, z, w]`, are normalized, and represent active rotations from the named local frame into the target frame. State the source and target frames wherever an orientation is emitted. For composition, `q_world_from_sensor = q_world_from_controller * q_controller_from_sensor`; the rightmost rotation is applied first. `q` and `-q` represent the same rotation. Interpolation must handle this equivalence and reject non-finite or near-zero-norm inputs. Backend conversion may require a change of basis; reordering components alone does not fix a handedness mismatch.

**Proposed calibration procedure:**

1. Fix the Kinect mounting and mark surveyed court axes and floor references. Estimate the sensor-to-world transform and verify translation, scale, handedness, and floor orientation against independent reference positions.
2. Record the IMU mounting transform into the grip frame and selected playing hand. Estimate biases using the sensor's documented method; record output range, sample/filter settings, gravity treatment, and whether orientation is sensor-provided or estimated.
3. Define the controller-to-racket rotation and offset with a reproducible neutral grip/pose. Align the wrist/hand reference from skeleton tracking to the controller placement; do not equate joint center with a physical sensor position.
4. Check known translations and rotations, a stationary pose, a controlled swing, and both playing hands. Report positional/angular residuals rather than merely saying calibration succeeded.
5. Store a `calibration_id`, transform values, units, hardware/session applicability, procedure version, residuals, and creation time. Invalidate the calibration when camera or sensor mounting changes.

Calibration tolerances, reference fixtures, recalibration frequency, gravity subtraction, and any magnetometer use remain open. A backend's depth registration calibration is not by itself a court or racket calibration.

## Timestamp meanings

| Time | Clock domain and interpretation |
| --- | --- |
| IMU sample/capture time | Sensor clock if exposed; may precede interrupt because of conversion, filtering, or FIFO buffering |
| Controller `t0` | ESP32 monotonic clock at the specified interrupt/measurement boundary |
| Skeleton capture time | Camera/backend source clock with a documented exposure/frame convention |
| Data arrival | Receiver's local monotonic clock, after acquisition, processing, and transport |
| Processing completion | Producing component's local monotonic clock after its computation |
| Simulation time and tick | Logical time advanced by physics and committed with ball state; not wall time |
| Controller `tr` and `t1` | Same ESP32 clock as `t0`, at matching result reception and electrical output activation |

Keep source timestamps unchanged through processing. Append stage timestamps and clock IDs rather than rewriting the original timestamp. A timestamp without a clock domain, unit, and epoch/session is ambiguous. Restart and counter wrap handling must be explicit; extend short hardware counters consistently before subtraction, and never subtract values from different boots.

The local differences `tr - t0` and `t1 - t0` require no clock synchronization across devices. Cross-device stage durations and sensor alignment do require a clock mapping. Wall-clock time can label a run but should not drive local durations if it can jump. See [measurement boundaries](timing.md).

## Proposed clock mapping

For each source clock `s`, estimate an affine mapping into a common monotonic experiment time: `T = a_s * t_s + b_s`. Retain the mapping ID, units, validity interval, estimated offset and drift, and uncertainty bound. Do not assume one estimate stays valid indefinitely. Reset or invalidate it on reboot, timer discontinuity, excessive drift, or a missed refresh interval.

A candidate software implementation is a repeated timestamp exchange with four endpoint timestamps, bounded/observed path asymmetry, and a drift fit over time. The team must select and validate the algorithm; neither NTP/PTP nor a custom protocol is implemented. Where hardware timestamping or a shared electrical reference is available, use it to characterize the software mapping and instrumentation error. Scheduling and network asymmetry contribute uncertainty. Half the round trip is not established one-way delay.

To compare two captures, map both timestamps and propagate both mapping uncertainties plus capture-boundary uncertainty. For an estimated age `A`, report an interval such as `[A - u, A + u]`, with how `u` was obtained. If the maximum permitted age is `Amax`, conservatively require `A + u <= Amax`; a future-dated sample outside the permitted uncertainty is invalid. The same principle applies to IMU/pose alignment residuals. Unknown capture timing produces unknown acquisition age, even if network arrival is recent.

## Temporal fusion policy

Physics should record both age at decision time and the time difference between the selected IMU and skeleton observations. These answer different questions: two equally old inputs may align closely while still being too stale for gameplay. Interpolation adds a policy choice and may add waiting; extrapolation adds model uncertainty. Neither is permitted to hide missing observations.

The first implementation must select maximum pose age, maximum IMU age, maximum alignment error, allowed uncertainty, bounded history size, and any interpolation/extrapolation horizon. Store these in the experiment configuration and log the decision policy version. Reject observations when required bounds cannot be established. A visually smooth avatar is not evidence of valid collision timing.

## Validation evidence

Use known physical positions/orientations for spatial checks and GPIO/common-trigger measurements for clock checks. Test reboot, counter wrap, delayed packets, asymmetric delay, camera movement, and changes in sampling/filter configuration. Preserve mapping residuals, calibration residuals, estimated uncertainty, and failing cases with the run. These are required future checks; no synchronization or calibration accuracy has been measured in this project.
