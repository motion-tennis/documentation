# S1 physics and game mixed-batch fixture

The physics batch core queried three controller transactions against state version 1 at tick 100. During its precommit check, the middle sample crossed the 30 ms age limit. Physics rebuilt its candidate from the queried snapshot. The C# game store installed the rebuilt match as version **2** at tick **101**, with one new ball contact. The shared Python contract oracle independently accepted the same candidate. [Fixture](../fixtures/s1/physics-game-mixed-batch.json) · [Recorded results](../evidence/s1-physics-game-mixed-batch-results.json)

| Query | Controller / request | Physics result | Game accounting |
| --- | --- | --- | --- |
| 1 | 101 / 1 | Hit | First decision, event 0 |
| 2 | 102 / 2 | Stale input at 521,000 µs on the fixture Pi clock | Explicit rejected key, no committed decision |
| 3 | 103 / 3 | Miss | Second decision, event 1 |

Each transaction also includes the controller's 16-byte session ID. The middle input was a scripted hit in the initial candidate. Its sample was 25 ms old at query response and 31 ms old at submission. The physics fixture checks the earlier contact calculation and the rebuilt ball velocity, contact count and surviving decision order. It takes the stale-input outcome and transaction from terminal feedback, checks the batch and session identities, and reads the query ID and observation time from the matching failure trace.

The runner checks the emitted roster and initial snapshot against the existing [v0.3 setup and snapshot builders](../tests/match/fixtures.py). It compares the actual query and update with the stored fixture using generated Protobuf fields. The accepted configuration digest is SHA-256 over deterministic Protobuf configuration bytes. The game receives those bytes, the complete typed candidate and the explicitly rejected key. It verifies the query echo and starting snapshot before calling its public commit method.

Five independent stores exercised invalid first commits. Omitting the rejected key, naming a surviving input as rejected, repeating the rejected key, dropping a surviving decision, or reversing the survivors all produced an invalid result and preserved the complete starting snapshot. An identical retry of the accepted batch returned the original result. Retrying that batch with different rejection accounting was the sixth negative control and preserved the accepted version and result.

## Reproduce

Use adjacent documentation, physics and game checkouts, CMake with a C++20 compiler, the .NET SDK with the .NET 8 target, and Python with the project's pinned Protobuf and gRPC tools. The existing tracking codec environment supplies the Python dependencies. Run from the documentation checkout on Windows with that environment provisioned.

```powershell
..\motion-tennis-camera-tracking\.venv-codec\Scripts\python.exe -B scripts/check_s1_shared_batch.py --work-dir ..\tmp\s1-physics-game
```

The [runner](../scripts/check_s1_shared_batch.py) builds both test programs, regenerates the Python codec and runs the C# store. Its work directory contains the actual physics output and the typed game input for inspection. A nonzero exit signals a failed build or check. Use `--report <path>` to save a new result. The recorded report contains the tested base revisions, LF-normalized source hashes, canonical message hashes, tool versions and the game result.

## S1 checks on November 19

| Check | Result on the fixture worktrees |
| --- | --- |
| Physics | All three CTest targets passed in Release and Debug, covering 26 batch-core checks, 34 tracking-bridge checks and the new mixed-batch producer. |
| Game | All 16 standalone checks passed. The Release build and the shared-fixture invocation completed successfully. |
| Tracking and receivers | 64 tracking tests, 20 generated wire envelopes, 17 physics cases and seven debug cases passed. |
| Debug and shared contract | 72 debug tests, four trace fixtures, 32 match-contract tests, 10 evidence-freshness tests and the local documentation checker passed. |

## Evidence boundary

This is an offline S1 fixture with a scripted contact evaluator and a fake physics-side state service. The game checks that its own query returns the same starting snapshot. Rejection metadata accompanies the typed commit through the store's existing rejected-key argument. The accepted `StateUpdate` schema has no rejected-key field. Production framing, transport of that accounting, committed-event publication and end-to-end trace collection require separate evidence. Current S1 work is tracked in the [gate checklist](project-status.md#remaining-s1-work-at-this-review).
