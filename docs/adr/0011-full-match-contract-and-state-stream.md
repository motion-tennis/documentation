# ADR 0011: Full-match v0.3 contract and bounded state stream

- Date: 2026-10-26
- Status: Proposed S0 baseline; technical review and host fixtures are recorded in [S0 evidence](../s0-baseline.md). Human gate acceptance is pending.
- Supersedes: the ball-only schema and Pi/PC UDP state leg of [ADR 0005](0005-webcam-wireless-pi3-masterplan.md). Controller/feedback and tracking UDP, separate TCP control, and the selected tracking direction remain unchanged.

## Context

The agreed doubles game needs one state for ball, four avatars, roster/configuration references, serve/rally, score and rule events. The 0.2 proposal contains only ball state plus per-input decisions. A complete match and eight full decisions cannot be assumed to fit the existing 1,200-byte UDP limit. The generated-codec report includes maximum structural sizes and a full valid fixture; it distinguishes structural upper bounds from semantically admissible states.

Reducing the input rate, dropping query identities, lowering batch capacity or splitting an atomic state into separately committed pieces would change agreed behavior. Increasing UDP size would make path MTU/fragmentation another correctness dependency. Compacting identifiers through undocumented aliases would weaken traceability.

## Proposed decision

Use `motion.v03`, exact protocol/profile/schema negotiation, a typed `MatchSetup` and complete `MatchState`. Reserve the removed ball-only snapshot/update fields. Every candidate includes the complete match plus at most eight decisions and sixteen rule events. An immutable setup digest/revision binds four confirmed controller/person/avatar slots to rules and tuning. All setup changes are writer-epoch fenced and use the existing suspended installation/ACK/resume barriers.

Keep controller input/feedback and per-person pose/status on UDP with the 1,200-byte envelope limit. Move only Pi/PC query/response/update/result to a dedicated TCP state connection on port 41010. Use a four-byte big-endian length and at most 8,192 envelope bytes. State publication has the same cap. Retain the separate control connection on 41041 for setup and ambiguous-commit recovery.

Use one state batch in flight, at most three outbound frames, one assembly buffer and an 8 ms partial-frame deadline. Reject invalid lengths and wrong-channel bodies before processing. A partial-frame timeout closes the connection. Exact retry payloads and retained results remain idempotent; different payloads under one key are invalid. Unsent duplicate retries are coalesced. No deadline extends because TCP is reconnecting or retransmitting. After ambiguous acceptance, control recovery resolves the original commit before further state work.

The continuous four-by-200 Hz stream, 5 ms release, eight-query/two-per-controller capacity, required `ball_state_request`/`ball_state_response`, commit-before-feedback, 50 ms local expiry, diagnostic markers and Pi clock-map semantics are unchanged. The Pi still calculates all match changes; the PC only validates and atomically stores/publishes them.

## Consequences and acceptance

The state stream avoids IP fragmentation and retains one atomic bounded message. It introduces head-of-line and connection-recovery risks that must be measured on the actual Pi/Windows link in S2 and under integrated load in S5. No host codec test establishes those timings. The same protocol/profile and state transport apply in both planned WLAN topology variants.

Generated Python and statically bounded nanopb C host fixtures check cross-codec bytes/round trips, maximum structural encodings, malformed/truncated/oversized inputs and contract storage products. Offline semantic fixtures check setup, references, ordering and atomic replay/rejection. Target compiler/ABI interoperability, device memory headroom, real rules calculation, runtime validation and networking remain S1/S2/S4 work.

The versioned assumptions and later proof gates are in [S0 evidence](../s0-baseline.md). Adopting this proposed baseline is part of human S0 acceptance; the implementation task does not independently release S1.
