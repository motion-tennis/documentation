# Doubles gameplay, automatic movement and serving

[Documentation home](../README.md) · [Player assignment](player-assignment.md) · [Physics](physics.md) · [Game service and rendering](game-engine.md) · [Controller](controller.md) · [ADR 0010](adr/0010-doubles-auto-movement-gameplay.md)

Decision date: 2026-10-25. **Agreed design:** four humans play doubles, two against two, with automatic avatar locomotion, physical racket gestures, an overhead lift-and-swing serve, normal tennis scoring/net/out rules, explicit team assignment at startup and two elevated views from behind the teams. Humans do not chase the virtual ball. **Proposed:** the match format, screen arrangement and detailed state machines below. **Open:** gesture thresholds, movement tuning and hit assistance. **Implemented:** documentation only; no gameplay runtime, scoring, movement, serve detector or split-screen renderer exists.

Wii Tennis is an interaction reference: Nintendo describes automatic positioning and its original Wii Sports manual describes raising the controller to toss and swinging to serve. This project defines its own court, characters, rules and motion processing; no Nintendo assets or scoring variations are adopted. [Nintendo developer interview](https://iwataasks.nintendo.com/interviews/wiiu/wii-sports-club/0/2/), [official Wii Sports manual, Tennis](https://csassets.nintendo.com/noaext/image/private/t_KA_PDF/Wii_Wii_Sports?_a=DATAg1AAZAA0).

## Players, teams and startup

A full match requires four active humans, four controllers and four validated person/controller associations. One-to-three-controller runs remain integration tests; they do not silently insert computer players or claim a complete doubles match. The proposed stable slot encoding is:

| Stable player slot | Team | Player identity |
| --- | --- | --- |
| 1 | A | A1 |
| 2 | A | A2 |
| 3 | B | B1 |
| 4 | B | B2 |

These identities persist when players serve, receive, move toward the net or change court ends. They are not permanent front/back roles. Physical standing lanes establish camera/controller association and comfortable gesture space, not virtual court positions. Startup explicitly shows the four assignments and obtains confirmation before readiness; discovery order or a person's horizontal image position cannot choose a team. The [assignment contract](player-assignment.md) owns pairing, handedness, calibration and re-pairing barriers.

Proposed setup also records first-serving team, initial court end, each team's first server and receiving-side order. A visible toss-and-choice procedure is the normal match default; deterministic presets are labeled test fixtures. The toss winner chooses service/receipt or an end, with the opponents taking the remaining choice. [USTA scoring and match setup](https://www.usta.com/en/home/improve/tips-and-instruction/national/tennis-scoring-rules.html).

## Automatic movement and human-controlled racket motion

The Pi calculates four avatar roots/headings and one shared ball. Automatic movement positions each avatar for play; the assigned human still supplies the serve, swing timing and racket motion. It does not fabricate hits or supply an opponent when a person disconnects. Proposed movement is deterministic from committed state and recorded inputs, with bounded speed, acceleration, reach and teammate arbitration. Exact positioning, target selection, handover rules and assistance strength require tuning and replay evidence.

Camera pose remains an active gameplay input alongside continuous IMU data. Calibrate torso/shoulder/body-relative wrist motion and the playing hand in the constrained 2.5D model, then combine that local motion with the Pi-owned avatar root and heading. Conceptually, racket position is `avatar_root + avatar_heading_rotation * calibrated_local_racket_offset`; racket orientation combines the avatar heading with calibrated local IMU orientation. Keep the original pose/sample identities, capture times and uncertainty.

This replaces direct mapping of a person's absolute physical wrist position to the virtual court. Physical body translation is not a command to run after the ball. A monocular camera still does not establish arbitrary metric wrist depth; calibration, orientation drift, pose validity and temporal-fusion gates remain necessary. The renderer cannot choose a different collision position to make a shot look successful. [Coordinate and clock contract](coordinates-and-time.md), [tracking](tracking.md).

All four controllers continue at 200 measurement transactions/s, including between points and during another player's serve. The [hardware threshold marker](imu-trigger-markers.md) stays diagnostic: it does not authorize a toss, start a serve transaction, gate sending or decide a hit.

## Overhead serve interaction

Only the currently assigned server can initiate the serve. The proposed flow is `ready -> lift -> toss -> overhead_contact -> in_flight -> rally`, with explicit cancellation, fault and let branches. Recognize lift and swing from ordinary pose/IMU history; a single acceleration spike is insufficient. Thresholds, rearm timing, toss trajectory, contact window and permitted assistance remain versioned configuration choices.

| State | Proposed behavior |
| --- | --- |
| `ready` | Four players and clocks are ready; show server, receiver, service box and first/second attempt. Position the server avatar legally behind its baseline. |
| `lift` | Detect the assigned server's deliberate controller lift relative to the calibrated body. Debounce without adding an extra gameplay send. |
| `toss` | Pi creates the virtual toss; display it in both views. Await a deliberate overhead attempt or cancellation. |
| `overhead_contact` | Evaluate the recognized attempt against the tossed ball using the configured collision/assistance model. |
| `in_flight` | Advance the served ball and retain attempt, net-touch and landing evidence. |
| `rally` | Legal service has entered ordinary play; resolve the designated receiver's first return. |
| `fault` / `let` | Apply the rules below and return to the appropriate ready state through the same atomic commit path. |
| `interrupted` | Invalid tracking, clocks, connection or state prevents a sporting decision; pause and report the technical cause. |

A cancelled toss without a strike attempt is not a fault; an attempted strike that misses is. Preserve that distinction in the gesture state machine. [ITF 2026 Rules 16 and 19](https://www.itftennis.com/media/7221/2026-rules-of-tennis-english.pdf).

The automatic server position is proposed to enforce legal virtual footing. Physical steps in a standing lane do not create virtual foot faults. Other players' ordinary input remains measured but cannot take over the assigned server. The overhead gesture is this game's chosen interaction, not a claim that tennis prohibits other legal serving styles.

## Scoring and court rules

Use love/15/30/40. A game requires at least four points and a two-point lead: 40-all is deuce; the next point gives advantage; losing that advantage returns to deuce. **Proposed configurable match default:** best of three sets, each first to six games with a two-game lead, with a tie-break at 6-all. The user has not fixed match length. [LTA scoring guide](https://www.lta.org.uk/play/how-to-get-started/rules-scoring/).

The proposed standard tie-break is first to seven points with a two-point lead. The next scheduled server serves one point from the right, then the established rotation advances in two-point blocks while service sides alternate each point. That first tie-break server's team receives in the next set's first game. Change ends after odd-numbered games and every six tie-break points; apply the set-boundary end rule as well. [USTA scoring and tie-break guide](https://www.usta.com/en/home/improve/tips-and-instruction/national/tennis-scoring-rules.html). At a set boundary, change ends unless its total games are even; then wait until the next set's first game. [ITF Rule 10](https://www.itftennis.com/media/7221/2026-rules-of-tennis-english.pdf).

Doubles service rotates among all four players for the set, for example A1, B1, A2, B2 when those first servers are selected. Each serves a whole standard game. Each receiving team fixes its deuce/ad receiver order for the set; either partner may hit subsequent rally shots. Teams may choose new within-team orders at a new set. Rally bounds include the doubles alleys. [USTA doubles rules](https://www.usta.com/en/home/improve/tips-and-instruction/national/doubles-tennis-rules-tips.html).

Serves alternate right/left starting on the right in each standard game, targeting the diagonal service box. The doubles alleys do not enlarge that box. Two consecutive service faults lose the point. [LTA serving rules](https://www.lta.org.uk/play/how-to-get-started/rules-scoring/).

The following rule distinctions follow [ITF 2026 Rules 12, 17, 19, 22, 24 and 25](https://www.itftennis.com/media/7221/2026-rules-of-tennis-english.pdf):

| Situation | Sporting result |
| --- | --- |
| Ball touches a boundary line | In for the court/box that line bounds |
| Service touches net and is otherwise legal | Let: replay the same attempt; a previous fault remains |
| Service fails net crossing or lands outside its box, including a net-touch serve | Fault, not let |
| Rally ball clips net, crosses and lands in | Play continues |
| Rally ball is out or cannot make a legal return | Opposing team wins the point |
| Ball bounces twice before return | Opposing team wins the point |
| Receiver volleys the serve | Receiving team loses the point |
| Both partners touch the same return | Their team loses the point |

Only supported, configured sporting contacts may produce these results. Tracking loss, packet expiry, ambiguous commits and invalid clock mappings are technical failures, never double faults or ordinary lost points. Keep already committed scores; recovery of an interrupted point requires an explicit, recorded resume/replay decision. A per-sample `MISS` is not itself a lost tennis point: point resolution depends on the ball/rally state.

## Two team views

The agreed display has one view for each team, elevated behind that team's own court end and looking toward the opponents. Preserve depth cues and visible net/service boxes rather than using a purely vertical overhead view. **Proposed arrangement:** horizontal split, Team A above and Team B below, with stable labels, shared score and visible server/attempt state.

After an end change, each camera follows its team's new end while the team's screen panel stays stable. Both views render the same committed state/version and ball. Rotate camera transforms; never mirror world coordinates, handedness, hit direction or collision geometry. Render interpolation and decorative animation cannot alter game state.

## State ownership and implementation gate

The Pi remains the sole calculator of ball motion, automatic avatar positions, contact/rule events, serve state and score changes. The Windows game service stores and versions the committed result; it must not become a second rules writer. Preserve the required `ball_state_request`/`ball_state_response`, then submit one version-checked atomic update covering ball, avatars, serve/rally state, roster/rules references and score effects. Publish both views and confirmed feedback from accepted state; retries cannot award a point twice. UI setup/reset requests follow the same ownership and session barriers.

The v0.3 [Protobuf contract](../spec/motion.proto) now specifies complete roster configuration, avatar/serve/rally/score state and separate rule events. [S0 evidence](s0-baseline.md) records generated host-codec and offline contract checks. The proposed standard match format is versioned in the profile; rules calculation, gestures, movement and runtime interoperability remain unimplemented. A contract fixture does not establish a playable match.

Acceptance must cover four confirmed humans; service/receiver rotation; cancelled toss versus attempted miss; first/second serve and let; deuce/tie-break/end changes; line/net/out/second-bounce decisions; simultaneous teammate swings; technical interruption without score fabrication; duplicate commits; and both cameras showing the same state. Measure unchanged 200 Hz traffic, complete transaction outcomes and the existing timing targets with automatic movement, pose processing and both views enabled. Numerical gesture/assistance settings and uncommon rule edge cases must be resolved in versioned fixtures before claiming complete tennis-rule coverage.
