# ADR 0004: Proposed transport and open skeleton dependency

[Decision index](README.md)

**Status:** Superseded historical proposal. [ADR 0005](0005-webcam-wireless-pi3-masterplan.md) replaces TCP/JSON live traffic with UDP/Protobuf and chooses a webcam-first Windows/RTMO reference. This page preserves earlier reasoning; it is not the current implementation contract. **Implementation:** absent.

## Context

No existing protocol, dependency list or tracker is available to standardize. Teams need a shared candidate contract without treating invented setup commands or unselected packages as working software.

## Proposal and unresolved choice

Start contract review with persistent TCP carrying length-prefixed UTF-8 JSON, explicit version/session/transaction identities and bounded queues. This favors inspectable messages and simple framing for initial experiments. TCP head-of-line delays and parsing cost must be measured. UDP or compact binary encoding remain alternatives if evidence justifies them; changing transport cannot remove application correlation, bounds, freshness, or the required ball query.

The original alternatives were Linux acquisition plus a separate estimator or a compatible Microsoft SDK body-tracking host; `libfreenect2` alone is not a skeleton tracker. Those were unimplemented options, not installed dependencies. See the current [webcam tracking stack](../tracking-stack.md) for the replacement direction.

## Consequences

The [protocol](../protocol.md) is a reviewable proposed contract with synthetic examples. Bootstrap details, finite timing limits, ports, security, and backend adapters remain open. Documentation cannot establish four-person tracking, timing accuracy or interoperability without code and hardware.

## Validation needed

Run a backend feasibility experiment for joint quality, body identities, timestamp meaning, OS/hardware support and license suitability. Then implement schema fixtures and transport fault tests, measuring load and bounded resource behavior before accepting a transport choice.
