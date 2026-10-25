# ADR 0008: Use MPU-6050 with Zephyr for the first prototype

- Date: 2026-10-25
- Status: **Agreed design** for the first prototype; firmware and hardware validation are not implemented
- Supersedes: the BMI270/ESP-IDF recommendation in [ADR 0005](0005-webcam-wireless-pi3-masterplan.md) and the open first-prototype IMU/runtime choice in [ADR 0006](0006-independent-imu-trigger-markers.md)
- Related: [IMU assessment](../imu-selection.md), [marker contract](../imu-trigger-markers.md), [hardware](../hardware.md), [reference profile](../../spec/reference-profile.json)

## Context and decision

The user selected MPU-6050 with Zephyr for the first prototype after discussing available modules, continuous acquisition and an additional hardware marker. Use MPU-6050 over I²C on an ESP32 controller running Zephyr. ESP32-S3-DevKitC-1-N8R8 remains a proposed board; the exact board, breakout, dependency versions, wiring, ranges and filter/threshold settings still require confirmation and validation. No purchase, working firmware or measured sensor capability follows from this decision.

Preserve the continuous 200 Hz gameplay stream. The configurable motion interrupt is an additional diagnostic marker with its own identity and timestamp, linked through the existing sample, pose, ball-state query/response, decision, commit and feedback path. It neither starts a replacement transaction nor gates transmission. The Wi-Fi direction and external-AP/Pi-hotspot comparison in [ADR 0007](0007-wifi-topology-comparison.md) remain in place.

## Profile and compatibility

Advance the reference profile to `webcam-pi3-wireless-v2` and record MPU-6050/I²C, Zephyr and the unverified first-prototype selection status. Retain the existing `imu_candidate` key for profile continuity; the adjacent selection-status field establishes that this IMU/runtime pair is agreed for the prototype, while the complete reference design remains unverified. Profile bytes and their hash change. All components and run manifests must use the same revised profile/hash when implementation begins.

The gameplay schema and protocol version, player count, sampling rates, limits, timing targets, ports and acceptance values remain unchanged. Do not interpret the profile revision as permission to alter payloads, sampling, priorities, batching or expiry. Hardware/firmware configuration and diagnostic trace metadata are separate from gameplay data.

## Required implementation and evidence

1. Pin the actual ESP32 target, Zephyr/HAL/driver revisions and build configuration. Document I²C wiring, power and the MPU-6050's single shared INT before claiming a reproducible setup.
2. Explicitly configure and read back DLPF and sample divider together. Measure actual 200 Hz acquisition and loss under load; a divider setting alone does not prove a 5 ms sample cadence.
3. Extend the reviewed Zephyr driver path for motion configuration and early interrupt timestamps. Its existing data-ready callback does not provide the required motion handler or exact edge timing. Attribute shared-INT sources using status; preserve ambiguous overlaps and missing edges as unresolved evidence, without inventing a second MPU-6050 interrupt output.
4. Characterize the actual part's motion threshold, filter/reference semantics, duration, rearm, detector delay and IRQ-capture uncertainty. Do not describe the legacy motion engine as a verified raw absolute-acceleration comparator. A software threshold would be a different measurement boundary and cannot silently replace the hardware-marker goal.
5. Verify marker links through the complete path while continuous sample cadence and gameplay behavior remain unchanged. Keep per-sample RTT separate from marker latency; validate false/repeated triggers, haptic interference, saturation and trace loss.

Acquisition/network bring-up may proceed while marker acceptance remains open. Record any unmet marker requirement explicitly; do not claim that selecting a supported sensor binding implements the marker.

## Alternatives and consequences

LSM6DSV16X/32X remain later alternatives if measured constraints require another sensor. BMI270/ESP-IDF are historical recommendations for this prototype, not parallel default stacks. Final production hardware is outside this first-prototype decision. A later replacement needs a documented decision and profile revision; the current selection is not reopened merely because implementation work remains.

The [source-backed assessment](../imu-selection.md) retains lifecycle and driver limitations. This decision records the user's prototype choice; it does not establish supplier stock, a tested Zephyr release, absolute-threshold semantics or measured latency.
