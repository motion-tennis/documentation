# Player, controller and team assignment

[Documentation home](../README.md) · [Gameplay](gameplay.md) · [Tracking](tracking.md) · [Protocol](protocol.md)

**Agreed design:** normal play is doubles with four people, four controllers and two fixed teams. Players perform arm/racket gestures from calibrated physical stations; the Pi moves their avatars automatically on the virtual court. **Proposed implementation:** the slot encoding, lobby workflow and registry below. **Implemented:** no lobby, association service or gameplay runtime exists. [ADR 0010](adr/0010-doubles-auto-movement-gameplay.md) records the gameplay decision.

## Stable teams and player slots

Use this proposed canonical encoding for the existing `Association.player_slot` field:

| Wire slot | Player label | Fixed team | Avatar identity |
| --- | --- | --- | --- |
| 1 | A1 | Team A | A1 |
| 2 | A2 | Team A | A2 |
| 3 | B1 | Team B | B1 |
| 4 | B2 | Team B | B2 |

Each occupied slot has exactly one controller boot/session, one confirmed tracking-session/person, one playing hand and one avatar. A controller or tracked person cannot occupy two slots, and a team cannot have more than two players. Normal doubles starts only when all four slots are ready. One-to-three-player runs remain explicitly labeled integration tests; absent slots do not silently become AI players.

Team and slot identity survive virtual court-end changes, camera viewpoint changes and front/back role changes. Those changes affect position or presentation, not the roster. Show team colors together with persistent A1/A2/B1/B2 labels and controller IDs, so identification does not depend on color or left/right screen position alone.

Physical stations provide camera separation and calibration space. Their location does not assign a team or a virtual court lane. A player standing to the camera's left may belong to either team. Real body translation does not drive the avatar's court position; the [gameplay design](gameplay.md) defines Pi-owned automatic movement.

## Lobby and first assignment

The proposed UI presents team selection and a short guided identification step; the control/session checks run behind that flow.

1. **Register controllers.** Display each accepted controller ID, current boot/session, connection and readiness state. An optional operator-requested identify blink may help distinguish devices; this UI/firmware feature is proposed and must be logged separately from gameplay cues.
2. **Choose the destination.** Select an unassigned controller, Team A or Team B, an available slot in that team, and the playing hand. Show occupied slots and reject conflicting selections rather than replacing an existing player.
3. **Identify the person.** Guide one player at a time through lifting/moving the selected hand at their physical station. Compare its camera wrist trajectory with that controller's temporally mapped IMU motion. This supplies evidence for a candidate person, not automatic authorization. Ambiguous or invalid timing yields no accepted candidate.
4. **Confirm and reserve.** Show the controller, person overlay, hand and team/slot together for explicit operator confirmation. Physics atomically validates and reserves the candidate binding against the registry: duplicate controller/person/slot assignments are rejected even if two UI actions race. A reservation is not yet an active gameplay association.
5. **Install the association.** Physics applies the existing versioned installation and acknowledgement barrier described below. A rejected or stale installation leaves the slot unready and releases its candidate reservation without silently activating an older binding.
6. **Start normal doubles.** Require four confirmed, installed slots, usable tracking, matching calibration and valid source-to-Pi clock mappings. Match configuration and the initial committed state must also be accepted before gameplay starts. A UI click or TCP delivery alone cannot mark a slot ready.

The matching method and confidence thresholds require validation under occlusion, simultaneous motions and similar controller signals. Detection order, camera side, proximity and a reused tracker number are insufficient to establish who holds a controller.

Readiness controls gameplay eligibility, not the regular sensor stream. Keep continuous sampling/transmission and per-sample outcome accounting while a binding is unavailable or suspended; report the corresponding failure instead of an ordinary miss.

## Association registry and installation barrier

Physics owns the registry and preserves the full binding:

`(controller_id, controller_boot_session) -> (tracking_session_id, person_id, player_slot, playing_hand, calibration_id, association_version)`.

The existing `Association` message carries these identities through its controller transaction, tracking/person fields, `player_slot`, `right_hand`, calibration and association version. Its transaction sequence is zero because it identifies a controller for control setup. Increment `association_version` for every binding change and retain prior versions in trace history.

Before replacement, suspend the old association and resolve or explicitly invalidate its queued/in-flight physics work. The controller retires pending transactions and cancels queued cues tied to the old association/calibration, retaining failure and suppression reasons. Physics sends the installation with a unique `command_id`; the controller installs it while suspended and echoes the matching association/command with `response=true` and `accepted=true`, or rejects it explicitly. Retries are idempotent by command ID. Only matching acceptance plus valid clocks/calibration permits the correlated `resume` barrier. No normal gameplay input is eligible before that barrier completes.

Commit the reservation as the active registry binding only when installation succeeds; preserve uniqueness throughout installation and recovery. Late commands, old sessions or old association versions cannot overwrite a newer binding. Every pending measurement retains the association/calibration used at transmission, so delayed feedback cannot activate a cue after reassignment. See [protocol lifecycle](protocol.md#error-and-lifecycle-behavior) and [controller behavior](controller.md).

## Loss, reconnect and roster changes

Missing joints or uncertain identity suspends hit eligibility and produces an explicit tracking/input failure. Retain the slot and team as reserved for that player; never transfer them automatically to the nearest remaining person. Temporary recovery of the same established identity requires valid tracking, timing/calibration and the resume barrier. If identity cannot be established, repeat guided identification and operator confirmation.

A tracker restart invalidates its session-scoped person IDs. A controller reboot creates a new boot session even when its device ID is unchanged. Reconnects must revalidate the registered session and binding; a new controller/tracker session requires explicit confirmation and a new association installation. Reappearing numerical person IDs do not recover the old identity by themselves.

Re-pairing, hand changes and team/player changes occur only in the lobby or while paused. Rebinding the same confirmed player after a device/session restart may preserve the roster after the barrier succeeds. For an actual player or team change during a match, the proposed baseline ends that match and starts a new match/game session with the new roster; do not silently move a score or active rally to another person. A future roster-preserving substitution policy requires explicit match rules and versioned protocol support. Virtual end changes and automatic front/back movement do not constitute roster changes.

## Protocol boundary and acceptance

The v0.3 typed `MatchSetup` now carries four explicit slot/controller/person/avatar bindings, roster/rules revisions and a configuration digest. Every full match state references that exact setup. Setup is writer-epoch fenced and does not replace the existing `Association` installation ACK and resume barrier. [S0 fixtures](s0-baseline.md) check bounded encoding, uniqueness and stale references offline; runtime installation remains S1/S2 work. The 200 Hz controller payloads, diagnostic-only IRQ markers and required query/response/commit semantics remain unchanged.

Acceptance must cover all four confirmed assignments, duplicate controller/person/slot attempts, full teams, ambiguous guided motion, cancelled/rejected installation, lost/stale acknowledgements, delayed old feedback, hand/controller swaps, tracker/controller restarts and paused roster changes. Verify stable team identity across virtual end changes and camera viewpoint changes, and verify that walking between physical stations never becomes automatic team assignment or avatar locomotion. One-to-three-player test runs must remain visibly distinct from normal doubles. No such runtime or hardware test has been performed.
