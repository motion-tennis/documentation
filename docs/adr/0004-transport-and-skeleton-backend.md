# ADR 0004: Proposed transport and open skeleton dependency

[Decision index](README.md)

**Status:** Transport proposed; skeleton backend open, 2026-10-24. **Implementation:** absent.

## Context

No existing protocol, dependency list or tracker is available to standardize. Teams need a shared candidate contract without treating invented setup commands or unselected packages as working software.

## Proposal and unresolved choice

Start contract review with persistent TCP carrying length-prefixed UTF-8 JSON, explicit version/session/transaction identities and bounded queues. This favors inspectable messages and simple framing for initial experiments. TCP head-of-line delays and parsing cost must be measured. UDP or compact binary encoding remain alternatives if evidence justifies them; changing transport cannot remove application correlation, bounds, freshness, or the required ball query.

Do not name `libfreenect2` as a skeleton tracker: it supplies sensor acquisition/registration. Select and validate either a Linux acquisition-plus-estimator route or a compatible Microsoft SDK body-tracking host route before documenting runnable tracking setup. See [tracking evidence and primary sources](../tracking.md#backend-selection). The intended game PC environment remains Linux unless implementation evidence establishes another requirement.

## Consequences

The [protocol](../protocol.md) is a reviewable proposed contract with synthetic examples. Bootstrap details, finite timing limits, ports, security, and backend adapters remain open. Documentation cannot establish four-person tracking, timing accuracy or interoperability without code and hardware.

## Validation needed

Run a backend feasibility experiment for joint quality, body identities, timestamp meaning, OS/hardware support and license suitability. Then implement schema fixtures and transport fault tests, measuring load and bounded resource behavior before accepting a transport choice.
