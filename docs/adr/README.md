# Architecture decision records

[Documentation home](../../README.md) · [Open decisions](../roadmap.md)

These records distinguish established project decisions from suggestions. **Agreed design** is not **Implemented**. Proposed records require team review before adoption; no runtime validation is implied by recording a decision.

| Record | Status | Subject |
| --- | --- | --- |
| [0001: component roles and required ball query](0001-component-roles-and-ball-query.md) | Agreed design | ESP32 controllers, active Kinect skeletons, Pi physics, PC state/visualization and required request/response |
| [0002: single writer and versioned commits](0002-single-writer-and-versioned-commits.md) | Proposed | State ownership, periodic motion, concurrency, commit acknowledgement and recovery |
| [0003: application timing and evidence](0003-application-timing-and-evidence.md) | Agreed measurement definitions; proposed instrumentation | Local `t0`, `tr`, `t1`, clock boundaries and honest latency reporting |
| [0004: transport and skeleton backend](0004-transport-and-skeleton-backend.md) | Proposed transport; open tracker | Initial TCP/JSON contract and explicit dependency gate for skeleton tracking |

For a new decision, add a numbered Markdown file with status, context, decision or proposal, consequences, alternatives and validation needed. Link it here and update affected pages. Supersede earlier records explicitly rather than rewriting history as though a proposal had always been implemented.
