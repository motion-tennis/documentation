# ADR 0002: Single physics writer and versioned game commits

[Decision index](README.md)

**Status:** Initial proposal, refined by [ADR 0005](0005-webcam-wireless-pi3-masterplan.md) into ordered atomic batches with a logical query per input. Sole state ownership and commit acceptance remain current design proposals. **Implementation:** absent; concurrency/restart tests remain required.

## Context

Several controllers may request decisions concurrently. The ball must also keep moving between inputs. Independent game and Pi integrators could create conflicting ball histories, while a delayed query response could lead to an outdated update.

## Proposal

The game stores the sole committed snapshot, identified by game session and state version. One fenced physics writer serializes periodic and controller jobs. Each job queries current state, calculates a candidate and submits an update with its base version. The game commits atomically only if session, writer epoch and version match; it deduplicates update IDs.

Add `state_commit_result`. Normal hit/miss controller feedback follows acceptance, preventing success feedback for a rejected calculation. Simulation tick is logical integration time and is distinct from commit version. The renderer may interpolate snapshots without writing authoritative state.

After an uncertain commit, pause further writes and resolve the same update identity within retention. If recovery cannot establish whether it committed, reset/resynchronize the session instead of blindly replaying the event. Detailed rules are in [physics](../physics.md) and [protocol](../protocol.md).

## Consequences and alternatives

This preserves the mandatory ball query and gives straightforward ordering and deduplication, but adds commit round-trip latency and can bottleneck at network speed. The 5 ms tick and four-controller capacity require measurement. A pipelined writer or speculative rollback might improve throughput but introduces reconciliation complexity; it is not part of this initial proposal. An authoritative physics-local state would conflict with the agreed PC query transaction and needs a separately approved architecture change.

## Validation needed

Test same-tick inputs, periodic/event interleavings, stale versions, duplicate updates, lost commit replies, reconnect, epoch replacement, service restart and unknown retention. Verify at most one commit per update and no positive feedback for rejected updates. Report simulation lag and latency under rendering/network load.
