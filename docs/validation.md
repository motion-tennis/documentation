# Documentation validation record

[Documentation home](../README.md) · [Inspection baseline](overview.md#inspection-evidence) · [Future runtime tests](testing.md)

Date: 2026-10-24. Scope: local documentation changes across all five accessible repositories. This record describes documentation validation, not system or hardware acceptance. All working trees were clean before the task; existing licenses were preserved. No commits, pushes, publishing, or repository settings changes were performed.

## Changes reviewed

| Repository | Before | After |
| --- | --- | --- |
| `documentation` | README containing a title and `test`, plus MIT license | Navigable hub; substantive requirements, architecture, hardware/component/interface/timing/setup/testing guidance; decision records; standard-library documentation checker |
| `motion-tennis-camera-tracking` | Repository-name README | Accurate status, active Kinect role, unselected skeleton backend, pairing/freshness responsibilities, proposed streams, local prerequisites and future smoke test |
| `motion-tennis-controller` | Repository-name README | ESP32 role, correlated outcomes, explicit error feedback, local timing definitions, actual checkout instructions and honest absence of firmware |
| `motion-tennis-game-engine` | Repository-name README | PC/Linux intent, query/snapshot service, proposed committed-state rules, visualization boundaries, local prerequisites and future smoke test |
| `motion-tennis-physics-engine` | `New Readme` | Pi role, explicit required ball query/response, proposed serialized periodic/event processing, conflict handling and planned tests |

The baseline contained no competing architecture to migrate. These changes replace placeholders and resolve ambiguities in the proposed design; they do not claim to fix previously implemented firmware or network behavior.

Manual cross-repository review checked English, component/hardware names, implementation labels, interface names, units, coordinate conventions, time definitions, original timestamp preservation, continuous skeleton acquisition and ball-state ownership. An independent review prompted explicit execution-time freshness rechecks after network waiting, same-process writer-epoch resumption on reconnect, session-qualified event identity, and consistent complete-message receipt semantics for `tr`.

## Commands and results

Commands were run locally with Python 3.14.8. The checker requires Python 3.9+ and only the standard library; the minimum version was not separately exercised.

| Command or check | Result |
| --- | --- |
| `python3 scripts/check_docs.py` from `documentation` | Passed across all five repositories: local paths/anchors, locally mapped GitHub project links, reachable documentation, JSON syntax, fence balance and basic Mermaid structure |
| `python3 scripts/check_docs.py --workspace /tmp` | Passed in standalone-documentation mode; absent sibling repositories and their remote links reported as skips |
| `python3 scripts/check_docs.py --help` | Passed; documented CLI arguments available |
| `git diff --check` in each of the five repositories | Passed for tracked changes |
| `git diff --exit-code -- LICENSE` in each repository | Passed; all existing license contents unchanged |
| Separate Python UTF-8, final-newline and trailing-whitespace scan of maintained Markdown and checker source | Passed, including untracked new files not covered by `git diff --check` |
| Python `ast.parse` of `scripts/check_docs.py` | Passed; source syntax valid |
| Local parser availability checks (`command -v` and Node module resolution) | No `mmdc`, Mermaid package/CLI, or `markdownlint` available |

The standard checker prints current file/link/example/diagram counts when run. Known GitHub `blob/main` references resolve to the corresponding local worktree for checking; this does not prove new pages already exist remotely.

## Limits and checks not performed

- Mermaid declarations, nested block balance, arrows and labels were reviewed, but no full Mermaid parser or rendering check ran because the tooling is absent. Rendering remains a publishing-format acceptance check; a successful structural check is not a parse guarantee.
- External URL reachability, repository access permissions and remote heading anchors were not comprehensively tested. Kinect dependency claims were checked against the primary sources linked in [tracking](tracking.md) and [hardware](hardware.md). No application deployment URL was invented.
- JSON examples were parsed and reviewed against the proposed contract, not executed against a runtime schema; no serializers or handlers exist. Numeric examples are synthetic, not measurements.
- No existing documentation CI or component test suite was available. No hardware, skeleton tracking, firmware, networking, simulation, rendering, clock synchronization or timing experiment was run because implementations and configured hardware are absent.

## Remaining implementation decisions

The [open-decision register](roadmap.md#open-decision-register) covers the skeleton backend/OS, controller parts/wiring/toolchain, Pi/PC environment, rendering and physics implementations, protocol approval/bootstrap/endpoints/security, calibration and clock mapping, freshness/deadline/resource limits, fusion/collision rules, and feedback profiles. None of these prevents completing accurate documentation, but they must be resolved before runtime acceptance or performance claims.
