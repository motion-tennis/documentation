# ADR 0012: Unity for the Windows game client

[Decision index](README.md) · [Game integration](../game-engine.md) · [Master plan](../master-plan.md)

**Status:** Agreed engine selection by explicit user request, 2026-10-29; implementation and validation pending. Supersedes the SDL3 renderer proposal in [ADR 0005](0005-webcam-wireless-pi3-masterplan.md). The separate committed-state service and Pi calculation authority remain unchanged.

## Context

The earlier reference proposed a native C++20 state service and a separate C++/SDL3 renderer on Windows. The user now requires the game engine to be implemented in Unity. The game still needs two views of one doubles match, explicit player assignment, a scoreboard and diagnostics without coupling the Pi's required state exchanges to graphics frames.

## Decision

- Implement the Windows game client, scene rendering, team cameras and player-facing UI in Unity with C#.
- Keep the headless committed-state service in a separate process; native C++20/CMake remains its proposed implementation. Unity consumes committed snapshots/events and submits versioned control requests.
- Keep ball physics, automatic avatar movement, contact/serve/rules and score calculation on the Pi. Unity animation and built-in physics must not become a second authoritative simulation.
- Preserve the required `ball_state_request`/`ball_state_response`, atomic versioned commits and `state_commit_result`, session/epoch fencing, bounded subscriptions, continuous 200 Hz inputs, diagnostic markers and timing definitions.
- Keep the accepted v0.3 schema and reference-profile bytes unchanged. This engine selection changes the presentation implementation, not the wire contract or calibrated 2.5D input model.
- Pin the Unity editor, Windows build support, render pipeline, scripting backend and C# codec/package versions only after a verified setup. No specific release, installed project or working build is established by this decision.

## Consequences and alternatives

The Unity client needs a compatible C# codec, a bounded state adapter, an explicit world-to-Unity coordinate conversion and two cameras sharing one match version. Existing host fixtures must be extended to verify the new consumer during implementation. Scene/UI work stays on the appropriate Unity thread; state-service responsiveness must be measured under Unity and tracking load. See the [implementation boundary](../game-engine.md#unity-implementation-boundary).

SDL3 is superseded for the game client. Moving state handling into Unity's frame loop or moving the Pi's simulation into Unity would change the established architecture and is outside this decision. Unity rendering does not resolve monocular depth ambiguity or prove timing targets.

## Validation and scope

This task updates shared documentation and the game repository's contributor guidance against documentation revision `7925028a6700df11a52b2eee0c225a9d9578f426`. S1 remains active; no runtime slice or later stage is released by this selection. Check documentation links, consistency and whitespace now. Later implementation must prove C# fixture compatibility, coordinate conversion, consistent two-view state, bounded disconnect/recovery and state-service performance under inference/render load. No Unity installation, source implementation, asset production or hardware test is part of this documentation change.
