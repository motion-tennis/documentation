# Architecture decision records

[Documentation home](../../README.md) · [Open decisions](../roadmap.md)

These records distinguish established project decisions from suggestions. **Agreed design** is not **Implemented**. Proposed records require team review before adoption; no runtime validation is implied by recording a decision.

| Record | Status | Subject |
| --- | --- | --- |
| [0001: component roles and required ball query](0001-component-roles-and-ball-query.md) | Historical; hardware superseded by 0005 | Required request/response retained; Kinect/Linux assumptions replaced |
| [0002: single writer and versioned commits](0002-single-writer-and-versioned-commits.md) | Proposed; refined by 0005 | Sole state ownership retained; ordered atomic batching added |
| [0003: application timing and evidence](0003-application-timing-and-evidence.md) | Agreed measurement definitions; proposed instrumentation | Local `t0`, `tr`, `t1`, clock boundaries and honest latency reporting |
| [0004: transport and skeleton backend](0004-transport-and-skeleton-backend.md) | Superseded by 0005 | Historical TCP/JSON and Kinect backend proposal |
| [0005: webcam wireless Pi3 masterplan](0005-webcam-wireless-pi3-masterplan.md) | Current constraints; prototype IMU/runtime superseded by 0008 | Webcam 2.5D, Windows RTX 5080, Pi 3 B, battery wireless, batched UDP/Protobuf and debug-units |
| [0006: independent IMU trigger markers](0006-independent-imu-trigger-markers.md) | Agreed marker design; open prototype selection resolved by 0008 | Hardware threshold marker, complete trace correlation, separate event latency, IMU/Zephyr evaluation |
| [0007: Wi-Fi topology comparison](0007-wifi-topology-comparison.md) | Agreed Wi-Fi direction and comparison plan; selection unmeasured | External AP baseline versus Pi hotspot with unchanged traffic and wired laptop; ESP-NOW deferred |
| [0008: MPU-6050 with Zephyr for the first prototype](0008-mpu6050-zephyr-prototype.md) | Agreed prototype selection; implementation and validation pending | I²C, single shared INT, Zephyr motion/timestamp extension, unchanged 200 Hz stream and gameplay schema |
| [0009: Pi-reference clock mapping and visible uncertainty](0009-pi-reference-clock-mapping.md) | Agreed reference, drift correction and debug visibility; implementation unverified | Four-timestamp observations, immutable offset/drift maps, source/reference epochs, uncertainty bands and honest local/cross-device timing |
| [0010: doubles, automatic movement and team views](0010-doubles-auto-movement-gameplay.md) | Agreed gameplay and team assignment; detailed tuning/contract extension pending | 2v2, stationary humans, gesture serve, ordinary tennis score, two rear team cameras and reuse of explicit association |

For a new decision, add a numbered Markdown file with status, context, decision or proposal, consequences, alternatives and validation needed. Link it here and update affected pages. Supersede earlier records explicitly rather than rewriting history as though a proposal had always been implemented.
