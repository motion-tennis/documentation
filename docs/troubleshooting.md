# Troubleshooting

[Documentation home](../README.md) · [Development setup](development.md) · [Testing](testing.md)

## Current checkout

**Implemented:** documentation and a documentation checker. There is no component executable, firmware image, package manifest or deployment configuration. A failed attempt to run a game/build command is not evidence of a missing dependency until the component has an implementation and documented entry point. Follow [development setup](development.md) for the work that can be performed now.

| Problem | Check and action |
| --- | --- |
| `python3` is unavailable or too old | The checker requires Python 3.9 or later. Use a compatible interpreter available on the development host; no third-party Python packages are required. |
| A relative documentation link fails | Confirm the target path and case, then compare the heading with its generated anchor. Update the source link or target together; run `python3 scripts/check_docs.py` again. |
| A project GitHub link is skipped | The linked component checkout is absent from the configured workspace. Clone the actual repository if available or use `--workspace` to point to the parent containing the checkouts. A skip is not remote-link verification. |
| A new GitHub documentation link returns 404 | Check whether the corresponding documentation commit has been reviewed and published. Local validation can resolve an uncommitted local file; it cannot make that file exist on GitHub. Access permissions may also hide a private repository. |
| A Mermaid block passes the checker but does not render | The checker only performs structural checks. Open the document in a Mermaid-capable viewer, obtain the parser error and correct the diagram. Record the viewer/version when investigating syntax differences. |
| A clone fails | Compare the remote with the central repository map and verify your GitHub access/SSH setup. Do not paste private keys or credentials into issue reports or documentation. |

## Proposed runtime diagnosis

The following table describes expected diagnostics for future implementations, not existing commands, logs or observed hardware behavior. Preserve the failing transaction's identifiers and timestamps before changing configuration. See [protocol](protocol.md), [physics](physics.md), [tracking](tracking.md) and [timing](timing.md) for the intended invariants.

| Symptom | Evidence to collect | Expected investigation or recovery |
| --- | --- | --- |
| Controller is connected but never completes a swing | Controller/session/request key, send time, Pi admission result, query/response and commit stages | A transport receipt is insufficient. Locate the missing application stage and terminate outstanding work at the configured deadline. |
| Every swing becomes a miss during occlusion | Frame quality, association version, selected joints, capture age and alignment uncertainty | Treat unavailable or unsuitable tracking as an explicit failure. Confirm no fallback maps tracking failure to a miss. |
| Kinect depth imagery exists but no joints exist | Selected driver/SDK, actual joint output and OS support | Acquisition is not skeleton tracking. Resolve the open skeleton dependency described in [tracking](tracking.md). |
| Racket attaches to the wrong player | Controller boot/session, tracking session, person ID, association history | Invalidate ambiguous association and repeat deliberate pairing. Do not infer identity from reused numerical person IDs after a tracking restart. |
| Motion appears mirrored, rotated or scaled | Calibration ID, source/destination frames, units and quaternion ordering | Verify transforms using known reference positions and rotations. Follow [coordinates and time](coordinates-and-time.md); do not repair the view while leaving collision coordinates inconsistent. |
| Ball jumps backwards or hits disappear | Game session, query ID, base and committed versions, update ID, arbitration order | Reject stale updates. Ensure game owns committed state and physics alone calculates its advances; rendering must not independently commit movement. |
| Ball stops while controllers are idle | Physics scheduler tick log, network waits, game commit readiness | Check periodic jobs as well as event transactions. Network waits must not create an unlimited tick backlog; apply the documented pause/degradation policy. |
| Controller vibrates twice for one hit | Feedback/event ID, duplicate and retry history, controller terminal record | Deduplicate before actuation; reconcile lost commit responses before repeating a state update. Retransmission must not create a new event. |
| Controller actuates after a reboot or very late | Original and current session IDs, request deadline, response arrival | Discard and count obsolete-session or terminal-transaction responses. Start a new boot/session identity after restart. |
| LED or motor behavior differs from the intended feedback | Feedback parameters, output marker, measured pin/driver output and physical onset | Separate requested intensity, electrical actuation and physical vibration. Verify selected wiring and driver before attributing delay to the network. |
| Software RTT looks good but physical feedback is late | `t0`, `tr`, `t1`, logic-analyzer trace, optional photodiode or vibration measurement | Report application response, electrical feedback and physical onset separately. Check scheduling, driver and sensor boundaries. |
| Negative data age or implausibly small one-way delay | Clock domains, mapping revision, offset/drift, uncertainty, restart/wrap logs | Reject invalid comparisons. Re-establish the clock mapping; do not substitute half the RTT for a one-way delay measurement. |
| Recent packet contains an old pose | Original capture timestamp, processing completion and arrival time | Base freshness on capture time with valid mapping and uncertainty. Arrival recency does not make a stale frame suitable. |
| Latency rises when logging is enabled | Queue occupancy, log overflow, CPU use, serial/storage write durations | Buffer logs and export asynchronously. Quantify observer overhead; count loss rather than blocking the measured path indefinitely. |
| Percentiles improve while users see more failures | All admitted/started transaction counts, failure/timeout/dropped counts, filtering policy | Include failure responses and censored observations in the report. Successful-only latency can hide overload. |

## Useful issue report

Provide the affected component, exact revisions, hardware/OS versions once selected, steps to reproduce, expected versus observed outcome, run ID, relevant correlation keys, sanitized configuration and a bounded log/trace extract. Include clock domains and the actual measurement boundary. Do not include Wi-Fi passwords, tokens, private keys or unnecessarily identifiable camera recordings. State whether the problem came from live hardware, a replay, a simulator or static documentation review.
