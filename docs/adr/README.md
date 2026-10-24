# Architecture decision records

[Documentation home](../../README.md) · [Open decisions](../roadmap.md)

These records distinguish established project decisions from suggestions. **Agreed design** is not **Implemented**. Proposed records require team review before adoption; no runtime validation is implied by recording a decision.

| Record | Status | Subject |
| --- | --- | --- |
| [0001: component roles and required ball query](0001-component-roles-and-ball-query.md) | Historical; hardware superseded by 0005 | Required request/response retained; Kinect/Linux assumptions replaced |
| [0002: single writer and versioned commits](0002-single-writer-and-versioned-commits.md) | Proposed; refined by 0005 | Sole state ownership retained; ordered atomic batching added |
| [0003: application timing and evidence](0003-application-timing-and-evidence.md) | Agreed measurement definitions; proposed instrumentation | Local `t0`, `tr`, `t1`, clock boundaries and honest latency reporting |
| [0004: transport and skeleton backend](0004-transport-and-skeleton-backend.md) | Superseded by 0005 | Historical TCP/JSON and Kinect backend proposal |
| [0005: webcam wireless Pi3 masterplan](0005-webcam-wireless-pi3-masterplan.md) | Current confirmed constraints and proposed reference | Webcam 2.5D, Windows RTX 5080, Pi 3 B, battery wireless, batched UDP/Protobuf and debug-units |

For a new decision, add a numbered Markdown file with status, context, decision or proposal, consequences, alternatives and validation needed. Link it here and update affected pages. Supersede earlier records explicitly rather than rewriting history as though a proposal had always been implemented.
