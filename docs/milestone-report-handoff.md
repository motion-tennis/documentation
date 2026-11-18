# M3 and Mx report preparation handoff

[Project status](project-status.md) · [M3 source](m3-system-design-integration-tests.md) · [Mx source](mx-integration-test-debugging-concept.md)

## Task and baseline

- User request: inspect new milestone work and prepare the supplied M3/Gate 2 and Mx reports; team name confirmed as Motion Tennis on 2026-11-17.
- Repository and branch: documentation, `task/m3-mx-reports`, created from freshly fetched `origin/main` at `a773ecc`. Prior task branches and debug implementation were preserved. No commit/push or team approval is inferred from this reporting request.
- Inputs: the course briefs supplied in the chat; the existing M3 R4 design; the audited M2 PDF dated 2026-11-11, including F-01-F-21 and NF-01-NF-15; current status and shared system/protocol/timing guidance. Exact Git hashes, personal paths and repository dependencies are omitted from the anonymous standalone PDFs.
- Scope: reporting sources, standalone PDFs, a small report generator and status/handoff documentation. No stage exception, hardware purchase, external message or runtime integration.
- Outcome: M3 R5 and Mx R1, dated 2026-11-17; independent PDFs with team/milestone/date, architecture/bench diagrams, embedded definitions and role-only responsibilities.

## Review decisions

M3 previously used N-01-N-11 and omitted the newer F-21 and NF-12-NF-15 obligations. The revision aligns identifiers to M2, retains the k=1 hypothesis and six physical-node count, adds explicit fail-stop/reintegration and resource/bus tests, and distinguishes clock precision/granularity from timestamp representation. Routine budgets remain planning allocations, not WCET evidence. A motor pulse cap is not inferred from the 50 ms transaction expiry. The Windows documentation freshness repair is correctly recorded as implemented.

Mx supplies the previously missing separate artifact. It defines TP-00..TP-08, hardware electrical/optical boundaries, whole-loop-to-message diagnosis, timing/functional/evidence verdicts, seeded faults and a run bundle. The tool list names roles, requirements/tests, current readiness and proposed dates. Tool dates after the course deadline are a conditional implementation plan, not a claim that tools are required to be built before this design submission; S2/S3 releases remain prerequisites.

All new optical, precision, instrumentation and finer budget proposals, hardware limits and quantitative observation-overhead targets remain explicitly subject to review. Gate 2 requires the team's design approval and Mx acceptance; neither is recorded. Historical M2 chronology Q-12 is retained as unresolved, not silently corrected.

## Generation and validation

Run `scripts/build_milestone_reports.py` with Python, ReportLab and the Windows Arial font family. It generates PDFs under the workspace `output/pdf/` and copies the same bytes into this repository's `docs/` publication paths. The script renders equivalent vector architecture/sequence diagrams directly; Mermaid source is retained for documentation, but no Mermaid-renderer validation is claimed.

Use Poppler `pdftoppm` for page PNGs, inspect every page, and use pypdf/pdfplumber for extraction, metadata, requirement-ID and page-bound checks. Validate that the PDFs include no student identities, emails, credentials, Git logs or local repository paths. Check all 36 canonical requirements in the M3 traceability table, both transaction budgets, IT-01..IT-12, and the Mx tool matrix. Run the normal documentation checker and `git diff --check`. Hardware tests remain specifications, not executed evidence.

Publication files: [M3 PDF](DRS_M3_MotionTennis.pdf) and [Mx PDF](DRS_Mx_MotionTennis.pdf). Team spelling on the title is Motion Tennis; filenames preserve the existing compact MotionTennis convention. Course due date: 2026-11-19 23:59 Europe/Vienna.

Validation completed on 2026-11-17: M3 has 18 pages and Mx has 7 pages. All rendered pages were visually inspected; a final interface-page overflow was corrected and checked again. PDF text, metadata, page bounds, 36 canonical requirement IDs, IT-01..IT-12 and TP-00..TP-08 checks passed. Published copies match the delivery PDFs byte for byte. The documentation checker and whitespace check passed. These checks establish document integrity, not hardware behavior or team acceptance.

## Authorized Mx decision update - 2026-11-18

The project user explicitly confirmed that team content confirmation constitutes Mx acceptance, including the prior tool/measurement plan. Photodiodes, logic analyzer and oscilloscope are available and hardware responsibility is assigned. The user selected stopping capture with the Windows game host and authorized initial operating-limit choices. Mx R2 records these decisions; M3 R6 aligns affected tests and the Mx acceptance record without inventing separate M3 acceptance or an internal stage release. The host-loss observation interval stays inconclusive for F-21 rather than a false safety pass. Exact board, regulator, cell/protection and motor current data remain startup prerequisites; the design sets conservative abort ceilings and excludes battery abuse/physical motor blocking.

The existing task branch and uncommitted report work are preserved. An origin fetch on 18 November failed with getaddrinfo/thread initialization; remote freshness is unverified and publication must wait for synchronization. No commit or push was attempted. Earlier 17 November validation/page counts describe R5/R1, not the revised PDFs.

Current deliverables are in workspace `output/pdf/2026-11-18/` with the prescribed filenames, plus matching copies in `docs/`. The previously delivered Mx PDF in the parent output directory was locked by an open viewer and was preserved. Use the dated output directory for this revision. M3 R6 is 19 pages; Mx R2 is 9 pages including the operating envelope and source record.

## M3 acceptance record - 2026-11-18

The project user explicitly accepted M3 as-is after accepting Mx. M3 R7 and Mx R3 record approval of the R6/R2 technical design and Gate 2 completion, including acceptance of the documented deferrals. Hardware validation, chronology clarification and internal implementation-stage release remain separate. No commit, push or course submission was performed.
