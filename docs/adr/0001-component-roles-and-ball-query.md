# ADR 0001: Component roles and required ball-state query

[Decision index](README.md)

**Status:** Historical agreed design from the initial brief, recorded 2026-10-24. Hardware/deployment portions are superseded by [ADR 0005](0005-webcam-wireless-pi3-masterplan.md): webcam-first 2.5D, Windows laptop and Pi 3 Model B. The explicit ball-state request/response and active pose fusion remain required. **Implementation:** runtime absent.

## Context

The demonstrator's purpose is to investigate distributed real-time processing with up to four players. Its transaction must expose the latency and consistency effects of obtaining game state from another component. Removing that exchange would change the system behavior being evaluated.

## Decision

Use ESP32 handheld controllers with Wi-Fi, IMU, LED and vibration motor. Use Kinect v2 skeleton data actively with controller measurements. Run physics on a Raspberry Pi. Run state storage and visualization on a PC, intended Linux; tracking may share that PC as a separate service if its backend supports the deployment.

Each valid controller physics transaction requests a current ball snapshot from the game and receives its version/tick before calculating its result. Physics returns controller feedback and sends game state/events. Keep both request and response arrows in diagrams and in implementation traces. Continuous camera acquisition is independent of transactions.

## Consequences and alternatives

The game is the committed-state store and physics calculates changes; a consistency protocol is therefore necessary. Network waits are part of application response time. A physics-local authoritative ball cache or a game-only physics loop could reduce exchanges, but neither satisfies this required transaction. Such designs are not the initial architecture.

Skeleton tracking is mandatory; depth access or presence detection alone is insufficient. No ESP32 model, firmware framework, game framework or Linux skeleton backend has been selected. See [architecture](../architecture.md), [tracking](../tracking.md) and the proposed [consistency decision](0002-single-writer-and-versioned-commits.md).

## Validation needed

Correlated traces must show input, selected pose, explicit ball query/response, result, game update and controller output. Run invalid-input and tracking-loss paths as separate failures. No runtime trace exists yet.
