# ADR 0010: Doubles with automatic movement, gesture serving and two team views

- Date: 2026-10-25
- Status: **Agreed gameplay direction**; no game runtime or extended match protocol is implemented
- Refines: [ADR 0005](0005-webcam-wireless-pi3-masterplan.md), retaining the controller, Wi-Fi, marker and clock decisions in ADRs 0006 through 0009
- Canonical design: [gameplay](../gameplay.md), [player assignment](../player-assignment.md), [physics](../physics.md), [display](../game-engine.md)

## Context and decision

The user selected doubles, two against two, taking Wii Tennis as the interaction reference. Physical players do not chase the ball: their avatars run automatically. Serving uses a controller lift to toss followed by an overhead stroke. Scoring follows ordinary tennis, with classical net/out failures. The display has two elevated views, each from behind its own team. Controllers are deliberately assigned to teams at startup using a clearly defined procedure.

Retain four humans with one controller, tracked person and persistent avatar per player. Use stable team slots A1/A2/B1/B2; proposed wire-slot encoding is 1/2/3/4 respectively. Reuse the existing guided controller/person identification, explicit confirmation and Association installation ACK/resume barrier. Network discovery and image position do not assign teams. Court-end changes, serve rotation and front/back movement do not change identity. Actual roster changes during a match require a paused, explicit transition; the initial policy starts a new match for a player/team substitution. Same-person session recovery follows the revalidation rules in the assignment contract.

## Motion and authoritative state

The Pi supplies virtual avatar roots/headings and calculates ball, contact, serve/rally and score transitions. Camera and IMU remain active inputs for body-relative hand/arm gestures and racket orientation around those roots. This replaces direct physical-wrist-to-court placement while retaining honest constrained 2.5D human sensing. Automatic movement does not create automatic racket hits or replace a missing player. Gesture/locomotion/assistance parameters need versioned tuning and evidence.

The Windows game service stores one atomically committed match state; its separate renderer shows that state through two camera transforms. Preserve the mandatory ball-state query/response and commit confirmation. Neither the renderer nor a second PC rule engine calculates independent authoritative movement or score. Full-state rejection/recovery must cover avatars, serve attempts, score and contact side-state along with the ball.

## Rules and views

Use love/15/30/40, deuce/advantage and ordinary doubles service/receiver order. Preserve the distinction between a legal net-touch rally return, service let, first/second serve fault, line contact and out/second bounce. A cancelled toss without a strike attempt is not a service fault. Technical tracking/clock/transport failures and ordinary per-sample misses do not automatically award points. The source-backed rule details are in [gameplay](../gameplay.md).

Best-of-three sets, six-game sets with a seven-point tie-break at 6-all, and a horizontal split with Team A above Team B are proposed configurable defaults. The user has not fixed match length or split orientation. Each view is elevated behind its team's current end; changing ends moves the cameras while team panel/identity stays stable. Interpolation and animation must respect contact/point discontinuities and cannot alter collision decisions.

## Compatibility and implementation gate

The existing `motion.proto` snapshot/update/publication describes ball state and per-input results. It lacks a complete roster, avatar, serve and score contract. Define and review a versioned schema/profile extension before implementing doubles, including atomic state, event IDs, setup versions, deduplication, recovery and worst-case encoded-size/resource fixtures. [Protocol requirements](../protocol.md#doubles-match-contract-extension) document that gate. This planning revision leaves the current schema and numeric profile values unchanged rather than claiming compatibility that does not exist.

Preserve the continuous 200 Hz controller stream, diagnostic-only threshold marker, Pi-reference clock mapping and existing timing targets. One-to-three-controller trials remain useful integration/load tests; a normal doubles match starts only with four validated players. No procurement, source-code implementation, engine installation, asset creation or gameplay/hardware test is implied.
